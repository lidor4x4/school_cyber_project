import wx
import cv2
import numpy as np
import base64


class VideoPanel(wx.Panel):
    # Custom panel that avoids flicker by bypassing background erase
    # And drawing frames directly using BufferedPaintDC.
    def __init__(self, parent):
        super().__init__(parent)

        # Last frame buffer
        self.frame_bmp = None

        # Prevent flicker by stopping background erase
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

        # Paint event
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def set_frame(self, bmp):
        self.frame_bmp = bmp
        self.Refresh()
        self.Update()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()

        if self.frame_bmp:
            dc.DrawBitmap(self.frame_bmp, 0, 0)


class LiveChatPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.is_video_disabled = False

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self, label="Live Chat")
        self.sizer.Add(self.title, 0, wx.ALL | wx.CENTER, 10)

        # Use the new VideoPanel instead of StaticBitmap
        self.video_panel = VideoPanel(self)
        self.sizer.Add(self.video_panel, 1, wx.EXPAND | wx.ALL, 10)

        # Disable camera button:
        self.disable_camera_btn = wx.Button(self, label="Disable video")
        self.sizer.Add(self.disable_camera_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(self.sizer)

        def disable_video(e):
            self.is_video_disabled = not self.is_video_disabled

        self.disable_camera_btn.Bind(wx.EVT_BUTTON, disable_video)

        self.SetSizer(self.sizer)

        # Webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            wx.MessageBox("Could not open webcam", "Error", wx.ICON_ERROR)
            return

        # Timer to update frames
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_frame, self.timer)
        self.timer.Start(30)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_close)

    def update_frame(self, event):
        if not self.is_video_disabled:
            ret, frame = self.cap.read()
            if not ret:
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            frame_base64 = base64.b64encode(frame)
            # self.send_to_server(frame_base64)

            bmp = wx.Bitmap.FromBuffer(w, h, frame)

            # Draw inside the flicker-free panel
            self.video_panel.set_frame(bmp)
        else:
            bmp = wx.Bitmap(700, 500)

            dc = wx.MemoryDC(bmp)

            dc.SetBackground(wx.Brush(wx.BLACK))
            dc.Clear()

            dc.SelectObject(wx.NullBitmap)

            del dc
            self.video_panel.set_frame(bmp)


    def on_close(self, event):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
