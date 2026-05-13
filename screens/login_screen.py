import wx
import re
import utils.utils as utils
from globals import globals


class LoginPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.methods = utils.Utils()

        self.SetBackgroundColour(wx.Colour(245, 245, 242))

        self.title_font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia")
        self.body_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.label_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.error_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # ── Header ────────────────────────────────────────────────────────────
        header_panel = wx.Panel(self)
        header_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        header_panel.SetMinSize((-1, 70))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.go_back_btn = wx.Button(header_panel, label="← Back")
        self.go_back_btn.SetFont(self.label_font)
        self.go_back_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        self.go_back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("home"))

        app_title = wx.StaticText(header_panel, label="MedConnect")
        app_title.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia"))
        app_title.SetForegroundColour(wx.Colour(26, 26, 26))

        header_sizer.AddSpacer(12)
        header_sizer.Add(self.go_back_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(app_title, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.AddSpacer(60)  # balance the back button
        header_panel.SetSizer(header_sizer)
        self.sizer.Add(header_panel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        # ── Title ─────────────────────────────────────────────────────────────
        self.sizer.AddSpacer(30)
        page_title = wx.StaticText(self, label="Log in")
        page_title.SetFont(self.title_font)
        page_title.SetForegroundColour(wx.Colour(26, 26, 26))
        self.sizer.Add(page_title, 0, wx.ALL | wx.CENTER, 4)

        page_sub = wx.StaticText(self, label="Enter your credentials to continue.")
        page_sub.SetFont(self.label_font)
        page_sub.SetForegroundColour(wx.Colour(107, 107, 107))
        self.sizer.Add(page_sub, 0, wx.ALL | wx.CENTER, 4)

        self.sizer.AddSpacer(20)

        # ── Server info message ───────────────────────────────────────────────
        self.info = wx.StaticText(self, label="")
        self.info.SetFont(self.label_font)
        self.info.SetForegroundColour(wx.Colour(133, 79, 11))
        self.sizer.Add(self.info, 0, wx.ALL | wx.CENTER, 4)

        # ── Email ─────────────────────────────────────────────────────────────
        self.email_error = wx.StaticText(self, label="")
        self.email_error.SetFont(self.error_font)
        self.email_error.SetForegroundColour(wx.Colour(162, 45, 45))
        self.sizer.Add(self.email_error, 0, wx.LEFT | wx.RIGHT, 60)

        self.email_ctrl = wx.TextCtrl(self, value="", size=(300, 36))
        self.email_ctrl.SetHint("Email")
        self.email_ctrl.SetFont(self.body_font)
        self.sizer.Add(self.email_ctrl, 0, wx.ALL | wx.CENTER, 6)

        # ── Password ──────────────────────────────────────────────────────────
        self.password_error = wx.StaticText(self, label="")
        self.password_error.SetFont(self.error_font)
        self.password_error.SetForegroundColour(wx.Colour(162, 45, 45))
        self.sizer.Add(self.password_error, 0, wx.LEFT | wx.RIGHT, 60)

        self.password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, size=(300, 36))
        self.password_ctrl.SetHint("Password")
        self.password_ctrl.SetFont(self.body_font)
        self.sizer.Add(self.password_ctrl, 0, wx.ALL | wx.CENTER, 6)

        self.sizer.AddSpacer(16)

        # ── Login button ──────────────────────────────────────────────────────
        self.login_btn = wx.Button(self, label="Log In", size=(300, 44))
        self.login_btn.SetBackgroundColour(wx.Colour(15, 110, 86))
        self.login_btn.SetForegroundColour(wx.Colour(225, 245, 238))
        self.login_btn.SetFont(self.body_font)
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        self.sizer.Add(self.login_btn, 0, wx.ALL | wx.CENTER, 5)

        # ── Go home button ────────────────────────────────────────────────────
        self.home_btn = wx.Button(self, label="Go Home", size=(300, 36))
        self.home_btn.SetFont(self.label_font)
        self.home_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        self.home_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("home"))
        self.sizer.Add(self.home_btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(self.sizer)

    def on_login(self, event):
        email = self.email_ctrl.GetValue()
        password = self.password_ctrl.GetValue()

        self.email_error.SetLabel("")
        self.password_error.SetLabel("")
        self.info.SetLabel("")

        errors = False

        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
        if not valid:
            self.email_error.SetLabel("Invalid email address")
            errors = True
        if len(password) < 8:
            self.password_error.SetLabel("Password must be at least 8 characters long")
            errors = True

        if not errors:
            res = self.send_to_server(f"LOGIN, {email}, {password}")
            if "Login was successful" in res:
                self.info.SetLabel("Login successful!")
                self.info.SetForegroundColour(wx.Colour(15, 110, 86))
                globals["auth_state"] = True
                username = res.split(",")[1]
                print(username)
                print(email)
                globals["user_name"] = username
                globals["user_role"] = self.send_to_server(f"GET_USER_ROLE_BY_EMAIL,{email}")
                self.switch_panel("home")
            else:
                self.info.SetLabel(res)
                self.info.SetForegroundColour(wx.Colour(162, 45, 45))