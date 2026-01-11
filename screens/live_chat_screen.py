import wx
import cv2
import socket
import threading
import numpy as np
import sounddevice as sd
import time

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

        image = wx.Image("disabled_video_photo.png", wx.BITMAP_TYPE_ANY)
        image = image.Scale(600, 400, wx.IMAGE_QUALITY_HIGH)
        self.video_off_bmp = wx.Bitmap(image)
        self.disabled_np = self.wx_image_to_cv(image)

        muted_mic_image = wx.Image("assets/muted mic photo.jpg", wx.BITMAP_TYPE_ANY)
        unmuted_mic_image = wx.Image("assets/unmuted_photo.png", wx.BITMAP_TYPE_ANY)

        muted_mic_image.Scale(60, 40, wx.IMAGE_QUALITY_HIGH)
        unmuted_mic_image.Scale(60, 40, wx.IMAGE_QUALITY_HIGH)

        self.muted_mic_bitmap = wx.Bitmap(muted_mic_image) 
        self.unmuted_mic_bitmap = wx.Bitmap(unmuted_mic_image)

        # self.static_bitmap_muted_mic = wx.StaticBitmap(self, wx.ID_ANY, muted_mic_bitmap)
        # self.static_bitmap_unmuted_mic = wx.StaticBitmap(self, wx.ID_ANY, unmuted_mic_bitmap)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(55, wx.DEFAULT, wx.NORMAL, wx.BOLD, underline=True)  
        title = wx.StaticText(self, label="Video Chat")
        title.SetFont(font)
        self.main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        self.main_sizer.AddSpacer(200)  

        video_container = wx.BoxSizer(wx.HORIZONTAL)

        video_container.AddSpacer(50)

        self.self_video = wx.StaticBitmap(self, size=(600, 400))
        video_container.Add(self.self_video, 1, wx.EXPAND | wx.ALL, 5)

        # video_container.Add(self.static_bitmap_muted_mic, 1, wx.ALL|wx.EXPAND, 10)
        # video_container.Add(self.static_bitmap_unmuted_mic, 1, wx.ALL|wx.EXPAND, 10)

        self.remote_video = wx.StaticBitmap(self, size=(600, 400))
        video_container.Add(self.remote_video, 1, wx.EXPAND | wx.ALL, 5)

        video_container.AddSpacer(50)

        self.main_sizer.Add(video_container, 1, wx.CENTER | wx.EXPAND)

        self.main_sizer.AddSpacer(30)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.disable_video_btn = wx.Button(self, label="Disable Video")
        self.disable_audio_btn = wx.BitmapButton(self, wx.ID_ANY, self.unmuted_mic_bitmap, size=(60, 40))

        btn_sizer.Add(self.disable_video_btn, 1, wx.EXPAND | wx.ALL, 5)
        btn_sizer.Add(self.disable_audio_btn, 1, wx.EXPAND, 5)

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
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def toggle_video(self, event):
        self.is_video_disabled = not self.is_video_disabled
        label = "Enable Video" if self.is_video_disabled else "Disable Video"
        self.disable_video_btn.SetLabel(label)

    def toggle_audio(self, event):
        self.is_audio_disabled = not self.is_audio_disabled
        label = "Enable Audio" if self.is_audio_disabled else "Disable Audio"
        self.disable_audio_btn.SetLabel(label)
        if self.is_audio_disabled:
            self.disable_audio_btn.SetBitmap(self.muted_mic_bitmap)
        else:
            self.disable_audio_btn.SetBitmap(self.unmuted_mic_bitmap)

    def send_video(self):
        while True:
            if self.is_video_disabled:
                frame = self.disabled_np
                wx.CallAfter(self.self_video.SetBitmap, self.video_off_bmp)
            else:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame = cv2.resize(frame, (600, 400))
                frame = cv2.flip(frame, 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bmp = wx.Bitmap.FromBuffer(600, 400, rgb)
                wx.CallAfter(self.self_video.SetBitmap, bmp)

            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            self.video_udp.sendto(buf.tobytes(), (self.server_ip, VIDEO_PORT))

            time.sleep(0.03)

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
            if not self.is_audio_disabled:
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
