import wx
import re
from globals import globals
import utils.utils as utils


class SignupPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server  # keep your method reference
        self.methods = utils.Utils()

        # Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, label="Signup Page"), 0, wx.ALL | wx.CENTER, 10)

        # Email error static_text:
        self.email_error = wx.StaticText(self, label="")
        self.email_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.email_error, 0, wx.ALL | wx.CENTER, 10)

        # Email text_ctrl
        self.email_ctrl = wx.TextCtrl(self, value="", size=(200, -1))
        self.email_ctrl.SetHint("Email: ")
        self.sizer.Add(self.email_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # password error static_text:
        self.password_error = wx.StaticText(self, label="")
        self.password_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.password_error, 0, wx.ALL | wx.CENTER, 10)

        # Password text_ctrl
        self.password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, size=(200, -1))
        self.password_ctrl.SetHint("Password: ")
        self.sizer.Add(self.password_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # Buttons
        self.signup_btn = wx.Button(self, label="Signup")
        self.back_btn = wx.Button(self, label="Back to Home")
        self.sizer.Add(self.signup_btn, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.back_btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(self.sizer)

        # Bind buttons
        self.back_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("home"))
        self.signup_btn.Bind(wx.EVT_BUTTON, self.on_signup)

    def on_signup(self, event):
        # self.email_error.SetLabel("TEST")
        email = self.email_ctrl.GetValue()
        password = self.password_ctrl.GetValue()
        errors = False

        # Input's check
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
        if not valid:
            self.email_error.SetLabel("Invalid Email")
            errors = True
        if len(password) < 8:
            self.password_error.SetLabel("Password must be at least 8 characters long")
            errors = True

        if not errors:
            res = self.send_to_server(f"SIGN_UP, {[email, password]}")
            if "successful" in res:
                globals["auth_state"] = True
                user_name = email.split("@")[0]
                globals["user_name"] = user_name
                self.switch_panel("home")
