import wx
import cv2
import socket
import threading
import numpy as np
import sounddevice as sd

SERVER_IP = "localhost"
VIDEO_PORT = 12346
AUDIO_PORT = 12347

class LiveChatPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.send_to_server = send_to_server

    
        self.self_video = wx.StaticBitmap(self)
        self.remote_video = wx.StaticBitmap(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.self_video, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.remote_video, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        self.video_udp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_udp_recv.bind(("", 0))

        self.audio_udp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp_recv.bind(("", 0))

        
        self.cap = cv2.VideoCapture(0)

        # Threads
        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_audio, daemon=True).start()

    # ---------------- VIDEO ----------------
    def send_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.resize(frame, (320, 240))
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            self.video_udp_send.sendto(buf.tobytes(), (SERVER_IP, VIDEO_PORT))

            # Show self video
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = img_rgb.shape[:2]
            bmp = wx.Bitmap.FromBuffer(w, h, img_rgb)
            wx.CallAfter(self.self_video.SetBitmap, bmp)

    def receive_video(self):
        while True:
            data, _ = self.video_udp_recv.recvfrom(65535)
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = img_rgb.shape[:2]
            bmp = wx.Bitmap.FromBuffer(w, h, img_rgb)
            wx.CallAfter(self.remote_video.SetBitmap, bmp)

    # ---------------- AUDIO ----------------
    def send_audio(self):
        def callback(indata, frames, time, status):
            self.audio_udp_send.sendto(indata.tobytes(), (SERVER_IP, AUDIO_PORT))

        with sd.InputStream(channels=1, samplerate=44100, callback=callback):
            while True:
                sd.sleep(1000)

    def receive_audio(self):
        stream = sd.OutputStream(channels=1, samplerate=44100)
        stream.start()
        while True:
            data, _ = self.audio_udp_recv.recvfrom(4096)
            audio = np.frombuffer(data, dtype=np.float32)
            stream.write(audio)
