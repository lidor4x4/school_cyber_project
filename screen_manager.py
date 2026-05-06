import wx
import socket
import threading
import queue
import utils.utils as utils

from screens.live_chat_screen import LiveChatPanel
from screens.login_screen import LoginPanel
from screens.signup_screen import SignupPanel
from screens.home_screen import HomePanel
from screens.verify_doctor_screen import VerifyDoctorPanel
from screens.waiting_room_screen import WaitingRoomPanel
from screens.schedule_meeting import ScheduleMeetingPanel

VIDEO_PORT = 12346
AUDIO_PORT = 12347

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="My App", size=(1280, 720))

        self.HOST = "192.168.3.78"
        self.PORT = 12345

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))

        self.methods = utils.Utils()
        self.current_panel = None
        self.push_callback = None

        self._expected_reply = threading.Event()
        self._reply_queue = queue.Queue()

        threading.Thread(target=self._listen_for_push, daemon=True).start()

        self.switch_panel("home")
        self.Show()

    def _listen_for_push(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                message = self.methods.decrypt_message(data)

                if self._expected_reply.is_set():
                    self._reply_queue.put(message)
                else:
                    if self.push_callback:
                        wx.CallAfter(self.push_callback, message)
            except:
                break

    def register_push_callback(self, callback):
        self.push_callback = callback

    def send_to_server(self, message):
        encrypted = self.methods.encrypt_message(message)
        self._expected_reply.set()
        self.client_socket.send(encrypted)
        response = self._reply_queue.get()
        self._expected_reply.clear()
        return response

    def send_to_server_unsecured(self, message):
        self.client_socket.send(message)
        response = self.client_socket.recv(4096)
        return response

    def switch_panel(self, name):
        if self.current_panel:
            self.current_panel.Destroy()

        self.push_callback = None

        if name == "login":
            self.current_panel = LoginPanel(self, self.switch_panel, self.send_to_server)
        elif name == "signup":
            self.current_panel = SignupPanel(self, self.switch_panel, self.send_to_server)
        elif name == "home":
            self.current_panel = HomePanel(self, self.switch_panel, self.send_to_server)
        elif name == "live_chat":
            self.current_panel = LiveChatPanel(self, self.switch_panel, self.send_to_server, self.HOST, self.register_push_callback)
        elif name == "verify_doctor_screen":
            self.current_panel = VerifyDoctorPanel(self, self.switch_panel, self.send_to_server)
        elif name == "waiting_room":
            self.current_panel = WaitingRoomPanel(self, self.switch_panel, self.send_to_server, self.client_socket)
        elif name == "schedule_meeting":
            self.current_panel = ScheduleMeetingPanel(self, self.switch_panel, self.send_to_server)

        self.Layout()