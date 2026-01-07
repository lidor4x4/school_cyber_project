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

SEND_W, SEND_H = 320, 240     # network size
SHOW_W, SHOW_H = 600, 400     # screen size


class LiveChatPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server, server_ip):
        super().__init__(parent)

        self.server_ip = server_ip
        self.send_to_server = send_to_server

        self.is_video_disabled = False
        self.is_audio_disabled = False

        # ---- flicker control ----
        self.last_self_frame = None
        self.last_remote_frame = None
        self.video_disabled_drawn = False

        image = wx.Image("disabled_video_photo.png", wx.BITMAP_TYPE_ANY)
        image = image.Scale(SHOW_W, SHOW_H, wx.IMAGE_QUALITY_HIGH)
        self.video_off_bmp = wx.Bitmap(image)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(55, wx.DEFAULT, wx.NORMAL, wx.BOLD, underline=True)
        title = wx.StaticText(self, label="Video Chat")
        title.SetFont(font)
        self.main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        self.main_sizer.AddSpacer(80)

        video_container = wx.BoxSizer(wx.HORIZONTAL)

        self.self_video = wx.StaticBitmap(self, size=(SHOW_W, SHOW_H))
        self.remote_video = wx.StaticBitmap(self, size=(SHOW_W, SHOW_H))

        video_container.Add(self.self_video, 1, wx.EXPAND | wx.ALL, 5)
        video_container.Add(self.remote_video, 1, wx.EXPAND | wx.ALL, 5)

        self.main_sizer.Add(video_container, 1, wx.CENTER | wx.EXPAND)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.disable_video_btn = wx.Button(self, label="Disable Video")
        self.disable_audio_btn = wx.Button(self, label="Disable Audio")

        btn_sizer.Add(self.disable_video_btn, 1, wx.EXPAND | wx.ALL, 5)
        btn_sizer.Add(self.disable_audio_btn, 1, wx.EXPAND | wx.ALL, 5)

        self.main_sizer.Add(btn_sizer, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)

        self.disable_video_btn.Bind(wx.EVT_BUTTON, self.toggle_video)
        self.disable_audio_btn.Bind(wx.EVT_BUTTON, self.toggle_audio)

        self.video_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_udp.bind(("", 0))

        self.audio_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp.bind(("", 0))

        self.cap = cv2.VideoCapture(0)

        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_audio, daemon=True).start()

    def toggle_video(self, event):
        self.is_video_disabled = not self.is_video_disabled
        self.disable_video_btn.SetLabel(
            "Enable Video" if self.is_video_disabled else "Disable Video"
        )

    def toggle_audio(self, event):
        self.is_audio_disabled = not self.is_audio_disabled
        self.disable_audio_btn.SetLabel(
            "Enable Audio" if self.is_audio_disabled else "Disable Audio"
        )

    # ---------------- VIDEO ----------------

    def send_video(self):
        while True:
            if self.is_video_disabled:
                if not self.video_disabled_drawn:
                    wx.CallAfter(self.self_video.SetBitmap, self.video_off_bmp)
                    self.video_disabled_drawn = True
                time.sleep(0.1)
                continue

            self.video_disabled_drawn = False

            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)

            # ---- SEND SMALL FRAME ----
            send_frame = cv2.resize(frame, (SEND_W, SEND_H))
            _, buf = cv2.imencode(".jpg", send_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            self.video_udp.sendto(buf.tobytes(), (self.server_ip, VIDEO_PORT))

            # ---- DISPLAY BIG FRAME ----
            display = cv2.resize(frame, (SHOW_W, SHOW_H))
            rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)

            if self.last_self_frame is None or not np.array_equal(rgb, self.last_self_frame):
                bmp = wx.Bitmap.FromBuffer(SHOW_W, SHOW_H, rgb)
                wx.CallAfter(self.self_video.SetBitmap, bmp)
                self.last_self_frame = rgb.copy()

            time.sleep(0.03)

    def receive_video(self):
        while True:
            data, _ = self.video_udp.recvfrom(MAX_UDP_SIZE)

            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is None or img.shape[:2] != (SEND_H, SEND_W):
                continue

            display = cv2.resize(img, (SHOW_W, SHOW_H))
            rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)

            if self.last_remote_frame is None or not np.array_equal(rgb, self.last_remote_frame):
                bmp = wx.Bitmap.FromBuffer(SHOW_W, SHOW_H, rgb)
                wx.CallAfter(self.remote_video.SetBitmap, bmp)
                self.last_remote_frame = rgb.copy()

    # ---------------- AUDIO ----------------

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
