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

        # Video box
        self.video_box = wx.StaticBitmap(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.video_box, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # UDP sockets
        self.video_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Camera
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
            frame = cv2.resize(frame, (640, 480))
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            self.video_udp.sendto(buf.tobytes(), (SERVER_IP, VIDEO_PORT))

    def receive_video(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 0))
        while True:
            data, _ = sock.recvfrom(65535)
            img = cv2.imdecode(np.frombuffer(data, np.uint8), 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = img.shape[:2]
            bmp = wx.Bitmap.FromBuffer(w, h, img)
            wx.CallAfter(self.video_box.SetBitmap, bmp)

    # ---------------- AUDIO ----------------
    def send_audio(self):
        def callback(indata, frames, time, status):
            self.audio_udp.sendto(indata.tobytes(), (SERVER_IP, AUDIO_PORT))

        with sd.InputStream(channels=1, samplerate=44100, callback=callback):
            while True:
                sd.sleep(1000)

    def receive_audio(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 0))
        stream = sd.OutputStream(channels=1, samplerate=44100)
        stream.start()
        while True:
            data, _ = sock.recvfrom(4096)
            audio = np.frombuffer(data, dtype=np.float32)
            stream.write(audio)
