import wx
from globals import globals
import utils.utils as utils


class HomePanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.methods = utils.Utils()
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.auth_state = globals["auth_state"]
        self.user_role = globals["user_role"]

        self.SetBackgroundColour(wx.Colour(245, 245, 242))

        self.title_font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia")
        self.body_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.label_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        header_panel = wx.Panel(self)
        header_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        header_panel.SetMinSize((-1, 70))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        app_title = wx.StaticText(header_panel, label="MedConnect")
        app_title.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia"))
        app_title.SetForegroundColour(wx.Colour(26, 26, 26))

        app_sub = wx.StaticText(header_panel, label="Your health, connected.")
        app_sub.SetFont(self.label_font)
        app_sub.SetForegroundColour(wx.Colour(107, 107, 107))

        title_col = wx.BoxSizer(wx.VERTICAL)
        title_col.Add(app_title, 0)
        title_col.Add(app_sub, 0)

        header_sizer.AddSpacer(20)
        header_sizer.Add(title_col, 0, wx.ALIGN_CENTER_VERTICAL)
        header_panel.SetSizer(header_sizer)
        self.sizer.Add(header_panel, 0, wx.EXPAND)

        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        print(self.auth_state)
        print(self.user_role)

        if self.auth_state:
            user_name = globals["user_name"]
            print(user_name)

            self.welcome_text = wx.StaticText(self, label=f"Welcome back, {user_name}")
            self.welcome_text.SetFont(self.title_font)
            self.welcome_text.SetForegroundColour(wx.Colour(26, 26, 26))
            self.sizer.Add(self.welcome_text, 0, wx.ALL | wx.CENTER, 20)

            if user_name.strip() == "Admin":
                section_lbl = wx.StaticText(self, label="MANAGEMENT")
                section_lbl.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial"))
                section_lbl.SetForegroundColour(wx.Colour(155, 155, 155))
                self.sizer.Add(section_lbl, 0, wx.LEFT | wx.BOTTOM, 16)

                self.live_chat_btn = wx.Button(self, label="Live Chat", size=(220, 44))
                self.live_chat_btn.SetBackgroundColour(wx.Colour(225, 245, 238))
                self.live_chat_btn.SetForegroundColour(wx.Colour(15, 110, 86))
                self.live_chat_btn.SetFont(self.body_font)
                self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
                self.live_chat_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("live_chat"))

                self.verify_dr_btn = wx.Button(self, label="Verify Doctors", size=(220, 44))
                self.verify_dr_btn.SetBackgroundColour(wx.Colour(230, 241, 251))
                self.verify_dr_btn.SetForegroundColour(wx.Colour(24, 95, 165))
                self.verify_dr_btn.SetFont(self.body_font)
                self.sizer.Add(self.verify_dr_btn, 0, wx.ALL | wx.CENTER, 5)
                self.verify_dr_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("verify_doctor_screen"))

                go_schedule_meeting_btn = wx.Button(self, label="Schedule a Meeting", size=(220, 44))
                go_schedule_meeting_btn.SetBackgroundColour(wx.Colour(238, 237, 254))
                go_schedule_meeting_btn.SetForegroundColour(wx.Colour(83, 74, 183))
                go_schedule_meeting_btn.SetFont(self.body_font)
                self.sizer.Add(go_schedule_meeting_btn, 0, wx.ALL | wx.CENTER, 5)
                go_schedule_meeting_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("schedule_meeting"))

            elif self.user_role == "dr":
                verify_status = send_to_server(f"VERIFY,{user_name}")
                print("Verify Status", verify_status)
                if verify_status == "0":
                    self.not_verified_text = wx.StaticText(self, label=f"{user_name}, your profile is under review.\nYou'll get access to Live Chat once approved.")
                    self.not_verified_text.SetFont(self.body_font)
                    self.not_verified_text.SetForegroundColour(wx.Colour(133, 79, 11))
                    self.not_verified_text.SetBackgroundColour(wx.Colour(250, 238, 218))
                    self.sizer.Add(self.not_verified_text, 0, wx.ALL | wx.CENTER, 20)
                else:
                    self.live_chat_btn = wx.Button(self, label="Live Chat", size=(220, 44))
                    self.live_chat_btn.SetBackgroundColour(wx.Colour(225, 245, 238))
                    self.live_chat_btn.SetForegroundColour(wx.Colour(15, 110, 86))
                    self.live_chat_btn.SetFont(self.body_font)
                    self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
                    self.live_chat_btn.Bind(wx.EVT_BUTTON, self.handle_live_chat_screen)

            else:
                self.live_chat_btn = wx.Button(self, label="Live Chat", size=(220, 44))
                self.live_chat_btn.SetBackgroundColour(wx.Colour(225, 245, 238))
                self.live_chat_btn.SetForegroundColour(wx.Colour(15, 110, 86))
                self.live_chat_btn.SetFont(self.body_font)
                self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
                self.live_chat_btn.Bind(wx.EVT_BUTTON, self.handle_live_chat_screen)

                go_schedule_meeting_btn = wx.Button(self, label="Schedule a Meeting", size=(220, 44))
                go_schedule_meeting_btn.SetBackgroundColour(wx.Colour(230, 241, 251))
                go_schedule_meeting_btn.SetForegroundColour(wx.Colour(24, 95, 165))
                go_schedule_meeting_btn.SetFont(self.body_font)
                self.sizer.Add(go_schedule_meeting_btn, 0, wx.ALL | wx.CENTER, 5)
                go_schedule_meeting_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("schedule_meeting"))

            self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP, 20)
            sign_out_btn = wx.Button(self, label="Sign Out", size=(120, 34))
            sign_out_btn.SetFont(self.label_font)
            sign_out_btn.SetForegroundColour(wx.Colour(107, 107, 107))
            sign_out_btn.Bind(wx.EVT_BUTTON, self.handle_sign_out)
            self.sizer.Add(sign_out_btn, 0, wx.ALL | wx.CENTER, 12)

        else:
            self.guest_title = wx.StaticText(self, label="Welcome back")
            self.guest_title.SetFont(self.title_font)
            self.guest_title.SetForegroundColour(wx.Colour(26, 26, 26))
            self.sizer.Add(self.guest_title, 0, wx.ALL | wx.CENTER, 20)

            self.guest_sub = wx.StaticText(self, label="Sign in to access your appointments, records, and care team.")
            self.guest_sub.SetFont(self.label_font)
            self.guest_sub.SetForegroundColour(wx.Colour(107, 107, 107))
            self.sizer.Add(self.guest_sub, 0, wx.ALL | wx.CENTER, 4)

            self.sizer.AddSpacer(16)

            self.login_btn = wx.Button(self, label="Log In", size=(220, 44))
            self.login_btn.SetBackgroundColour(wx.Colour(15, 110, 86))
            self.login_btn.SetForegroundColour(wx.Colour(225, 245, 238))
            self.login_btn.SetFont(self.body_font)
            self.sizer.Add(self.login_btn, 0, wx.ALL | wx.CENTER, 5)
            self.login_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("login"))

            self.signup_btn = wx.Button(self, label="Create Account", size=(220, 44))
            self.signup_btn.SetFont(self.body_font)
            self.sizer.Add(self.signup_btn, 0, wx.ALL | wx.CENTER, 5)
            self.signup_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("signup"))

        self.SetSizer(self.sizer)

    def handle_sign_out(self, event):
        user_name = globals["user_name"]
        self.send_to_server(f"CHANGE_TO_OFFLINE{user_name}")
        globals["auth_state"] = False
        globals["user_name"] = ""
        globals["user_role"] = ""
        globals["is_admin"] = False
        globals["is_online"] = False
        self.switch_panel("home")

    def handle_live_chat_screen(self, event):
        if globals["user_role"] == "dr":
            self.switch_panel("live_chat")
        else:
            self.switch_panel("waiting_room")