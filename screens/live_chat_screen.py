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
        self.queue_visible = False

        self.stop_event = threading.Event()

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
        go_back_btn.Bind(wx.EVT_BUTTON, self.handle_go_back)
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

        controls.Add(self.disable_video_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        controls.Add(self.disable_audio_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        controls_wrapper.AddStretchSpacer()
        controls_wrapper.Add(controls, 0, wx.ALIGN_CENTER)
        controls_wrapper.AddStretchSpacer()

        self.main_sizer.Add(controls_wrapper, 0, wx.EXPAND | wx.BOTTOM, 10)

        queue_wrapper = wx.BoxSizer(wx.HORIZONTAL)
        queue_wrapper.AddStretchSpacer()

        self.queue_toggle_btn = wx.Button(self, label="See Queue", size=(140, 40))
        self.queue_toggle_btn.Bind(wx.EVT_BUTTON, self.toggle_queue)

        queue_wrapper.Add(self.queue_toggle_btn, 0, wx.RIGHT | wx.BOTTOM, 20)

        self.main_sizer.Add(queue_wrapper, 0, wx.EXPAND)

        self.queue_panel = wx.Panel(self)
        self.queue_panel.Hide()
        self.queue_panel.SetBackgroundColour(wx.Colour(240, 240, 240))

        self.queue_sizer = wx.BoxSizer(wx.VERTICAL)
        self.queue_panel.SetSizer(self.queue_sizer)

        self.main_sizer.Add(self.queue_panel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 20)

        self.SetSizer(self.main_sizer)

        self.disable_video_btn.Bind(wx.EVT_BUTTON, self.toggle_video)
        self.disable_audio_btn.Bind(wx.EVT_BUTTON, self.toggle_audio)

        self.video_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_udp.bind(("", 0))
        self.video_udp.settimeout(0.5)

        self.audio_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_udp.bind(("", 0))
        self.audio_udp.settimeout(0.5)

        self.cap = cv2.VideoCapture(0)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)

        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_audio, daemon=True).start()

    def toggle_queue(self, _):
        self.queue_visible = not self.queue_visible

        if self.queue_visible:
            self.queue_toggle_btn.SetLabel("Hide Queue")
            self.queue_panel.Show()
            # Fetching must be threaded or it will freeze the video capture
            threading.Thread(target=self.load_queue_async, daemon=True).start()
        else:
            self.queue_toggle_btn.SetLabel("See Queue")
            self.queue_panel.Hide()

        # Update sizer layout without freezing
        self.main_sizer.Layout()

    def load_queue_async(self):
        response = self.send_to_server("GET_QUEUE,Dudu Farok")
        wx.CallAfter(self.refresh_queue_ui, response)

    def refresh_queue_ui(self, response):
        if not self.queue_visible:
            return

        self.Freeze() # Stops UI repaint during rebuild
        
        # Clear existing
        for child in self.queue_panel.GetChildren():
            child.Destroy()
        self.queue_sizer.Clear()

        if not response:
            txt = wx.StaticText(self.queue_panel, label="No patients in queue.")
            self.queue_sizer.Add(txt, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        else:
            patients = response.split(",")
            for patient in patients:
                self.add_patient_row(patient.strip())

        # LOCAL Layout: only calculate the queue area
        self.queue_panel.Layout()
        # Refresh the main sizer so the queue panel actually takes its space
        self.main_sizer.Layout()
        
        self.Thaw() # Resume UI painting

    def add_patient_row(self, patient_name):
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.AddStretchSpacer()

        name_label = wx.StaticText(self.queue_panel, label=patient_name)
        accept_btn = wx.Button(self.queue_panel, label="Accept", size=(70, 30))
        kick_btn = wx.Button(self.queue_panel, label="Kick", size=(70, 30))

        accept_btn.Bind(wx.EVT_BUTTON, lambda e, p=patient_name: self.accept_patient(p))
        kick_btn.Bind(wx.EVT_BUTTON, lambda e, p=patient_name: self.kick_patient(p))

        row.Add(name_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        row.Add(accept_btn, 0, wx.RIGHT, 5)
        row.Add(kick_btn, 0)

        self.queue_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 5)

    def accept_patient(self, patient_name):
        self.send_to_server(f"ACCEPT_PATIENT,{patient_name}")
        threading.Thread(target=self.load_queue_async, daemon=True).start()

    def kick_patient(self, patient_name):
        self.send_to_server(f"KICK_PATIENT,{patient_name}")
        threading.Thread(target=self.load_queue_async, daemon=True).start()

    def handle_go_back(self, _):
        self.stop_event.set()
        self.switch_panel("home")

    def on_destroy(self, event):
        self.stop_event.set()
        try:
            self.cap.release()
            self.video_udp.close()
            self.audio_udp.close()
        except:
            pass
        event.Skip()

    def load_icon_normalized(self, path, box_size):
        img = wx.Image(path, wx.BITMAP_TYPE_ANY)
        iw, ih = img.GetSize()
        scale = min(box_size / iw, box_size / ih)
        img = img.Scale(int(iw * scale), int(ih * scale), wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(img)

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
        self.disable_audio_btn.SetBitmap(
            self.muted_mic_bitmap if self.is_audio_disabled else self.unmuted_mic_bitmap
        )

    def send_video(self):
        while not self.stop_event.is_set():
            if self.is_video_disabled:
                frame = self.disabled_np
                # Use a small check to see if the widget is still valid
                if self.self_video:
                    wx.CallAfter(self.self_video.SetBitmap, self.video_off_bmp)
            else:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame = cv2.resize(frame, (600, 400))
                frame = cv2.flip(frame, 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bmp = wx.Bitmap.FromBuffer(600, 400, rgb)
                if self.self_video:
                    wx.CallAfter(self.self_video.SetBitmap, bmp)

            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            try:
                self.video_udp.sendto(buf.tobytes(), (self.server_ip, VIDEO_PORT))
            except:
                pass

            time.sleep(0.04) # SLIGHTLY slower to give the UI thread room to breathe

    def receive_video(self):
        while not self.stop_event.is_set():
            try:
                data, _ = self.video_udp.recvfrom(MAX_UDP_SIZE)
                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue

                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w = rgb.shape[:2]
                bmp = wx.Bitmap.FromBuffer(w, h, rgb)

                if self.remote_video:
                    wx.CallAfter(self.remote_video.SetBitmap, bmp)
            except:
                continue

    def send_audio(self):
        def callback(indata, frames, time_info, status):
            if self.stop_event.is_set() or self.is_audio_disabled:
                return
            try:
                data = (indata * 32767).astype(np.int16).tobytes()
                self.audio_udp.sendto(data, (self.server_ip, AUDIO_PORT))
            except:
                pass

        with sd.InputStream(channels=1, samplerate=44100,
                            blocksize=BLOCKSIZE, callback=callback):
            while not self.stop_event.is_set():
                sd.sleep(200)

    def receive_audio(self):
        stream = sd.OutputStream(channels=1, samplerate=44100,
                                 blocksize=BLOCKSIZE, dtype="float32")
        stream.start()

        while not self.stop_event.is_set():
            try:
                data, _ = self.audio_udp.recvfrom(BLOCKSIZE * 2)
            except:
                continue

            audio = np.frombuffer(data, np.int16).astype(np.float32) / 32767
            stream.write(audio)

        stream.stop()
        stream.close()