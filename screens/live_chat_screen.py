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
        self.disabled_video_sent = False

        self.image_disable = wx.Image("disabled_video_photo.png", wx.BITMAP_TYPE_ANY)
        self.image_disable = self.image_disable.Scale(600, 400, wx.IMAGE_QUALITY_HIGH)
        self.video_off_bmp = wx.Bitmap(self.image_disable)

        self.disabled_np = self.wx_image_to_cv(self.image_disable)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD, True, "Times New Roman")
        title = wx.StaticText(self, label="Video Chat")
        title.SetFont(font)
        self.main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        self.self_video = wx.StaticBitmap(self, size=(600, 400))
        self.remote_video = wx.StaticBitmap(self, size=(600, 400))

        video_sizer = wx.BoxSizer(wx.HORIZONTAL)
        video_sizer.Add(self.self_video, 1, wx.EXPAND | wx.ALL, 5)
        video_sizer.Add(self.remote_video, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(video_sizer, 1, wx.EXPAND)

        self.disable_video_btn = wx.Button(self, label="Disable Video")
        self.disable_audio_btn = wx.Button(self, label="Disable Audio")

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.disable_video_btn, 1, wx.EXPAND | wx.ALL, 5)
        btn_sizer.Add(self.disable_audio_btn, 1, wx.EXPAND | wx.ALL, 5)

        self.main_sizer.Add(btn_sizer, 0, wx.EXPAND)

        self.disable_video_btn.Bind(wx.EVT_BUTTON, self.toggle_video)
        self.disable_audio_btn.Bind(wx.EVT_BUTTON, self.toggle_audio)

        self.SetSizer(self.main_sizer)

        self.video_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_udp.bind(("", 0))

        self.audio_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp.bind(("", 0))

        self.cap = cv2.VideoCapture(0)

        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_audio, daemon=True).start()


    def wx_image_to_cv(self, wx_img):
        w, h = wx_img.GetWidth(), wx_img.GetHeight()
        data = wx_img.GetData()
        img = np.frombuffer(data, dtype=np.uint8).reshape((h, w, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img


    def toggle_video(self, event):
        self.is_video_disabled = not self.is_video_disabled
        self.disabled_video_sent = False

    def toggle_audio(self, event):
        self.is_audio_disabled = not self.is_audio_disabled


    def send_video(self):
        while True:
            if not self.is_video_disabled:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame = cv2.resize(frame, (600, 400))
                frame = cv2.flip(frame, 1)

                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                self.video_udp.sendto(buf.tobytes(), (self.server_ip, VIDEO_PORT))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bmp = wx.Bitmap.FromBuffer(600, 400, rgb)
                wx.CallAfter(self.self_video.SetBitmap, bmp)

                self.disabled_video_sent = False

            else:
                if not self.disabled_video_sent:
                    _, buf = cv2.imencode(
                        ".jpg",
                        self.disabled_np,
                        [cv2.IMWRITE_JPEG_QUALITY, 70]
                    )
                    self.video_udp.sendto(buf.tobytes(), (self.server_ip, VIDEO_PORT))
                    wx.CallAfter(self.self_video.SetBitmap, self.video_off_bmp)
                    self.disabled_video_sent = True


    def receive_video(self):
        while True:
            data, _ = self.video_udp.recvfrom(MAX_UDP_SIZE)
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            bmp = wx.Bitmap.FromBuffer(w, h, rgb)
            wx.CallAfter(self.remote_video.SetBitmap, bmp)


    def send_audio(self):
        def callback(indata, frames, time_info, status):
            if self.is_audio_disabled:
                return
            data = (indata * 32767).astype(np.int16).tobytes()
            self.audio_udp.sendto(data, (self.server_ip, AUDIO_PORT))

        with sd.InputStream(
            channels=1,
            samplerate=44100,
            blocksize=BLOCKSIZE,
            callback=callback
        ):
            while True:
                sd.sleep(1000)

    def receive_audio(self):
        stream = sd.OutputStream(
            channels=1,
            samplerate=44100,
            blocksize=BLOCKSIZE,
            dtype="float32"
        )
        stream.start()

        while True:
            data, _ = self.audio_udp.recvfrom(BLOCKSIZE * 2)
            audio = np.frombuffer(data, np.int16).astype(np.float32) / 32767
            stream.write(audio)
