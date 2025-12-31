import wx
import cv2
import socket
import threading
import numpy as np
import sounddevice as sd

VIDEO_PORT = 12346
AUDIO_PORT = 12347
MAX_UDP_SIZE = 65535
BLOCKSIZE = 2048

class LiveChatPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server, server_ip):
        super().__init__(parent)
        self.server_ip = server_ip
        self.send_to_server = send_to_server
        self.is_video_disabled = False
        self.is_audio_disabled = False
 
        img = wx.Image("disabled_video_photo.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(600, 400, wx.IMAGE_QUALITY_HIGH)
        self.video_off_bmp = wx.Bitmap(img)



        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD, True, "New Times Roman")
        self.video_screen_text = wx.StaticText(self, label="Video Chat")
        self.video_screen_text.SetFont(self.font)
        self.main_sizer.Add(self.video_screen_text, 0, wx.ALL | wx.CENTER, 10)


        self.self_video = wx.StaticBitmap(self, size=(600, 400))
        self.remote_video = wx.StaticBitmap(self, size=(600, 400))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.self_video, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.remote_video, 1, wx.EXPAND | wx.ALL, 5)

        self.main_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)

        #self.self_video = wx.StaticBitmap(self, size=(600, 400))
        #self.remote_video = wx.StaticBitmap(self, size=(600, 400))

        def disable_video():
            self.is_video_disabled = not self.is_video_disabled

        def disable_audio():
            self.is_audio_disabled = not self.is_audio_disabled

        self.disable_video_btn = wx.Button(self, label="Disable Video")
        self.disable_audio_btn = wx.Button(self, label="Disable Audio")

        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        controls_sizer.Add(self.disable_video_btn, 1, wx.EXPAND | wx.ALL, 5)
        controls_sizer.Add(self.disable_audio_btn, 1, wx.EXPAND | wx.ALL, 5)

        self.disable_video_btn.Bind(wx.EVT_BUTTON, lambda e: disable_video())
        self.disable_audio_btn.Bind(wx.EVT_BUTTON, lambda e: disable_audio())


        self.main_sizer.Add(controls_sizer, 1, wx.EXPAND | wx.ALL, 5)



        self.SetSizer(self.main_sizer)
        self.Layout()

        self.video_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_udp.bind(("", 0))

        self.audio_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp.bind(("", 0))

        self.cap = cv2.VideoCapture(0)

        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_audio, daemon=True).start()

    def send_video(self):
        while True:  # run forever
            if not self.is_video_disabled:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame = cv2.resize(frame, (600, 400))
                frame = cv2.flip(frame, 1)

                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                self.video_udp.sendto(buf.tobytes(), (self.server_ip, VIDEO_PORT))

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = img.shape[:2]
                bmp = wx.Bitmap.FromBuffer(w, h, img)
                wx.CallAfter(self.self_video.SetBitmap, bmp)
            else:
                wx.CallAfter(self.self_video.SetBitmap, self.video_off_bmp)

            # small sleep to prevent high CPU usage
            cv2.waitKey(30)

    def receive_video(self):
        while True:
            data, _ = self.video_udp.recvfrom(MAX_UDP_SIZE)
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = img.shape[:2]
            bmp = wx.Bitmap.FromBuffer(w, h, img)
            wx.CallAfter(lambda: [self.remote_video.SetBitmap(bmp)])


    def send_audio(self):
        def callback(indata, frames, time, status):
            if indata.shape[0] != BLOCKSIZE:
                indata = np.pad(indata, ((0,BLOCKSIZE-indata.shape[0]),(0,0)))
            data_to_send = (indata * 32767).astype(np.int16).tobytes()
            self.audio_udp.sendto(data_to_send, (self.server_ip, AUDIO_PORT))

        with sd.InputStream(channels=1, samplerate=44100, callback=callback, blocksize=BLOCKSIZE):
            while True:
                sd.sleep(1000)

    def receive_audio(self):
        stream = sd.OutputStream(channels=1, samplerate=44100, dtype='float32', blocksize=BLOCKSIZE)
        stream.start()
        
        while True:
            data, _ = self.audio_udp.recvfrom(BLOCKSIZE*2)  # int16 = 2 bytes per sample
            audio_float32 = np.frombuffer(data, dtype=np.int16).astype(np.float32)/32767
            stream.write(audio_float32)
