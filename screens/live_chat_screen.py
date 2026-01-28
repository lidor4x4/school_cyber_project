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
        self.switch_panel = switch_panel
        self.is_video_disabled = False
        self.is_audio_disabled = False

        VIDEO_W, VIDEO_H = 600, 400
        ICON_BOX = 64
        BTN_BOX = 76

        self.video_off_bmp, self.disabled_np = self.load_video_off_image(VIDEO_W, VIDEO_H)

        self.muted_mic_bitmap = self.load_icon_normalized("assets/muted mic photo.jpg", ICON_BOX)
        self.unmuted_mic_bitmap = self.load_icon_normalized("assets/unmuted_photo.png", ICON_BOX)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="Video Chat")
        title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        self.main_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 20)

        go_back_btn = wx.Button(self, label="Go Back")
        go_back_btn.Bind(wx.EVT_BUTTON, lambda evt,: self.switch_panel("home"))
        self.main_sizer.Add(go_back_btn, 0, wx.RIGHT, 5)


        self.main_sizer.AddStretchSpacer(1)

        video_row = wx.BoxSizer(wx.HORIZONTAL)
        self.self_video = wx.StaticBitmap(self, size=(VIDEO_W, VIDEO_H))
        self.remote_video = wx.StaticBitmap(self, size=(VIDEO_W, VIDEO_H))
        video_row.Add(self.self_video, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        video_row.Add(self.remote_video, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        self.main_sizer.Add(video_row, 0, wx.ALIGN_CENTER)
        self.main_sizer.AddStretchSpacer(1)

        controls_wrapper = wx.BoxSizer(wx.HORIZONTAL)
        controls = wx.BoxSizer(wx.HORIZONTAL)

        self.disable_video_btn = wx.Button(self, label="Stop Video", size=(160, 56))
        self.disable_audio_btn = wx.BitmapButton(
            self,
            bitmap=self.unmuted_mic_bitmap,
            size=(BTN_BOX, BTN_BOX),
            style=wx.BORDER_NONE
        )
        self.disable_audio_btn.SetMinSize((BTN_BOX, BTN_BOX))
        self.disable_audio_btn.SetMaxSize((BTN_BOX, BTN_BOX))

        controls.Add(self.disable_video_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        controls.Add(self.disable_audio_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        controls_wrapper.AddStretchSpacer()
        controls_wrapper.Add(controls, 0, wx.ALIGN_CENTER)
        controls_wrapper.AddStretchSpacer()

        self.main_sizer.Add(controls_wrapper, 0, wx.EXPAND | wx.BOTTOM, 20)

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

    def load_icon_normalized(self, path, box_size):
        img = wx.Image(path, wx.BITMAP_TYPE_ANY)
        iw, ih = img.GetSize()
        scale = min(box_size / iw, box_size / ih)
        new_w, new_h = int(iw * scale), int(ih * scale)
        img = img.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

        canvas = wx.Bitmap(box_size, box_size)
        dc = wx.MemoryDC(canvas)
        dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0)))
        dc.Clear()
        x = (box_size - new_w) // 2
        y = (box_size - new_h) // 2
        dc.DrawBitmap(wx.Bitmap(img), x, y, True)
        dc.SelectObject(wx.NullBitmap)
        return canvas

    def load_video_off_image(self, w, h):
        img = wx.Image("disabled_video_photo.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        np_img = self.wx_image_to_cv(img)
        return bmp, np_img

    def wx_image_to_cv(self, wx_img):
        w, h = wx_img.GetWidth(), wx_img.GetHeight()
        data = wx_img.GetData()
        img = np.frombuffer(data, dtype=np.uint8).reshape((h, w, 3))
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def toggle_video(self, _):
        self.is_video_disabled = not self.is_video_disabled
        self.disable_video_btn.SetLabel("Start Video" if self.is_video_disabled else "Stop Video")

    def toggle_audio(self, _):
        self.is_audio_disabled = not self.is_audio_disabled
        if self.is_audio_disabled:
            self.disable_audio_btn.SetBitmap(self.muted_mic_bitmap)
            self.disable_audio_btn.SetBackgroundColour(wx.Colour(220, 50, 50))
        else:
            self.disable_audio_btn.SetBitmap(self.unmuted_mic_bitmap)
            self.disable_audio_btn.SetBackgroundColour(wx.NullColour)
        self.disable_audio_btn.Refresh()

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
            self.audio_udp.sendto(data, (self.server_ip, AUDIO_PORT))

        with sd.InputStream(channels=1, samplerate=44100, blocksize=BLOCKSIZE, callback=callback):
            while True:
                sd.sleep(1000)

    def receive_audio(self):
        stream = sd.OutputStream(channels=1, samplerate=44100, blocksize=BLOCKSIZE, dtype="float32")
        stream.start()
        while True:
            data, _ = self.audio_udp.recvfrom(BLOCKSIZE * 2)
            audio = np.frombuffer(data, np.int16).astype(np.float32) / 32767
            stream.write(audio)
