import wx
from globals import globals
import utils.utils as utils


class HomePanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.methods = utils.Utils()
        self.switch_panel = switch_panel
        self.client_socket = send_to_server
        self.auth_state = globals["auth_state"]
        self.user_role = globals["user_role"]
        self.verified_dr = True

        self.font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.home_screen_text = wx.StaticText(self, label="Home Page")
        self.home_screen_text.SetFont(self.font)
        self.sizer.Add(self.home_screen_text, 0, wx.ALL | wx.CENTER, 10)

        print(self.auth_state)
        print(self.user_role)
        print("dsadsa", globals['user_name'])
        #print(send_to_server(f"VERIFY,{globals['user_name']}"))
        # If the user is logged in
        if self.auth_state:
            user_name = globals["user_name"]
            print(user_name)
            self.user_name_static_text = wx.StaticText(self, label=f"Welcome: {user_name}")
            self.user_name_static_text.SetFont(self.font)
            self.sizer.Add(self.user_name_static_text, 0, wx.ALL | wx.CENTER, 10)

           
            if user_name.strip() == "Admin":  
                self.live_chat_btn = wx.Button(self, label="Live Chat")
                self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
                self.live_chat_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("live_chat"))

                self.verify_dr_btn = wx.Button(self, label="Verify Doctors")
                self.sizer.Add(self.verify_dr_btn, 0, wx.ALL | wx.CENTER, 5)
                self.verify_dr_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("verify_doctor_screen"))

                go_schedule_meeting_btn = wx.Button(self, label="Schedule a meeting")
                go_schedule_meeting_btn.Bind(wx.EVT_BUTTON, lambda evt,: self.switch_panel("schedule_meeting"))
                self.sizer.Add(go_schedule_meeting_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)


            # If the user is a doctor
            elif self.user_role == "dr":
                if not send_to_server(f"VERIFY,{user_name}"):
                    self.not_verified_text = wx.StaticText(self, label=f"{user_name}, you aren't verified yet.")
                    self.not_verified_text.SetFont(self.font)
                    self.sizer.Add(self.not_verified_text, 0, wx.ALL | wx.CENTER, 10)
                else:
                    self.live_chat_btn = wx.Button(self, label="Live Chat")
                    self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
                    self.live_chat_btn.Bind(wx.EVT_BUTTON, self.handle_live_chat_screen)
            # Other authenticated users
            else:
                self.live_chat_btn = wx.Button(self, label="Live Chat")
                self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
                self.live_chat_btn.Bind(wx.EVT_BUTTON, self.handle_live_chat_screen)
                go_schedule_meeting_btn = wx.Button(self, label="Schedule a Meeting")
                go_schedule_meeting_btn.Bind(wx.EVT_BUTTON, lambda evt,: self.switch_panel("schedule_meeting"))
                self.sizer.Add(go_schedule_meeting_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)



        # If the user isn't logged in
        else:
            self.login_btn = wx.Button(self, label="Login")
            self.signup_btn = wx.Button(self, label="Sign Up")
            self.sizer.Add(self.login_btn, 0, wx.ALL | wx.CENTER, 5)
            self.sizer.Add(self.signup_btn, 0, wx.ALL | wx.CENTER, 5)

            self.login_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("login"))
            self.signup_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("signup"))

        self.SetSizer(self.sizer)

    def handle_live_chat_screen(self, event):
        if globals["user_role"] == "dr":
            self.switch_panel("live_chat")
        else:
            self.switch_panel("waiting_room")
