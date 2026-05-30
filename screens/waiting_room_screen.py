import wx
import threading
import utils.utils as utils


class WaitingRoomPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server, client_socket):
        super().__init__(parent)

        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.client_socket = client_socket
        self.methods = utils.Utils()
        self.running = True

        self.SetBackgroundColour(wx.Colour(245, 245, 242))

        self.title_font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia")
        self.body_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.label_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        header_panel = wx.Panel(self)
        header_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        header_panel.SetMinSize((-1, 70))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.go_back_btn = wx.Button(header_panel, label="← Back")
        self.go_back_btn.SetFont(self.label_font)
        self.go_back_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        self.go_back_btn.Bind(wx.EVT_BUTTON, self._on_back_clicked)

        app_title = wx.StaticText(header_panel, label="MedConnect")
        app_title.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia"))
        app_title.SetForegroundColour(wx.Colour(26, 26, 26))

        header_sizer.AddSpacer(12)
        header_sizer.Add(self.go_back_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(app_title, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.AddSpacer(60)
        header_panel.SetSizer(header_sizer)
        self.main_sizer.Add(header_panel, 0, wx.EXPAND)
        self.main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        self.main_sizer.AddStretchSpacer(1)

        self.title = wx.StaticText(self, label="Waiting Room")
        self.title.SetFont(self.title_font)
        self.title.SetForegroundColour(wx.Colour(26, 26, 26))
        self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.desc = wx.StaticText(self, label="Please wait — a doctor will be with you shortly.")
        self.desc.SetFont(self.body_font)
        self.desc.SetForegroundColour(wx.Colour(107, 107, 107))
        self.main_sizer.Add(self.desc, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)

        self.main_sizer.AddStretchSpacer(1)

        self.SetSizer(self.main_sizer)
        self.Layout()

        threading.Thread(target=self.wait_for_server, daemon=True).start()

    def _on_back_clicked(self, event):
        self.cleanup()
        self.switch_panel("home")

    def wait_for_server(self):
        try:
            self.client_socket.settimeout(1.0)
            
            while self.running:
                try:
                    data = self.client_socket.recv(4096)
                    if not data:
                        break  
                    
                    message = self.methods.decrypt_message(data)
                    wx.CallAfter(self.handle_server_message, message)
                except TimeoutError:
                    continue
                    
        except Exception as e:
            if self.running:
                print("Error receiving from server:", e)
        finally:
            try:
                self.client_socket.settimeout(None)
            except:
                pass
            print("Background thread has successfully closed.")

    def handle_server_message(self, message):
        if not self.running:
            return
            
        if message.startswith("ACCEPTED"):
            parts = message.split(",")
            doctor_ip = parts[1].strip() if len(parts) >= 2 else None
            self.cleanup() 
            self.switch_panel("live_chat", doctor_ip)

    def cleanup(self):
        self.running = False

    def Destroy(self):
        self.cleanup()
        super().Destroy()