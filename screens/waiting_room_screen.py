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

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Waiting Room")
        title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_font.SetUnderlined(True)
        self.title.SetFont(title_font)
        self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        self.desc = wx.StaticText(self, label="Please wait for your turn.")
        desc_font = wx.Font(21, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.desc.SetFont(desc_font)
        self.main_sizer.Add(self.desc, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        self.go_back_btn = wx.Button(self, label="Go Back")
        self.go_back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("home"))
        self.main_sizer.Add(self.go_back_btn, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)

        self.SetSizer(self.main_sizer)
        self.Layout()

        threading.Thread(target=self.wait_for_server, daemon=True).start()

    def wait_for_server(self):
        try:
            data = self.client_socket.recv(4096)
            if data:
                message = self.methods.decrypt_message(data)
                wx.CallAfter(self.handle_server_message, message)
        except Exception as e:
            print("Error receiving from server:", e)

    def handle_server_message(self, message):
        if message == "ACCEPTED":
            self.switch_panel("live_chat")

    def Destroy(self):
        self.running = False
        super().Destroy()