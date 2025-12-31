import wx
import socket
import utils.utils as utils

from screens.live_chat_screen import LiveChatPanel
from screens.login_screen import LoginPanel
from screens.signup_screen import SignupPanel
from screens.home_screen import HomePanel

UDP_CONTROL_PORT = 12348

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="My App", size=(1900, 1000))

        self.HOST = "192.168.3.250"
        self.PORT = 12345

        # TCP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))

        # UDP CONTROL
        self.udp_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_control.bind(("", 0))  # random local port

        self.methods = utils.Utils()
        self.current_panel = None

        self.switch_panel("home")
        self.Show()

    # ---------------- SWITCH PANEL ----------------
    def switch_panel(self, name):
        if self.current_panel:
            self.current_panel.Destroy()

        if name == "login":
            self.current_panel = LoginPanel(self, self.switch_panel, self.send_to_server)
        elif name == "signup":
            self.current_panel = SignupPanel(self, self.switch_panel, self.send_to_server)
        elif name == "home":
            self.current_panel = HomePanel(self, self.switch_panel, self.send_to_server)
        elif name == "live_chat":
            self.current_panel = LiveChatPanel(self, self.switch_panel, self.send_to_server)

        self.Layout()

    # ---------------- SEND TO SERVER ----------------
    def send_to_server(self, message, fast=False):
        """
        fast=False -> TCP (secure / reliable)
        fast=True  -> UDP CONTROL (low latency)
        """
        if fast:
            self.udp_control.sendto(message.encode(), (self.HOST, UDP_CONTROL_PORT))
            return None

        encrypted = self.methods.encrypt_message(message)
        self.client_socket.send(encrypted)
        response = self.client_socket.recv(4096)
        return self.methods.decrypt_message(response)
