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

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, label="Login"), 0, wx.ALL | wx.CENTER, 10)

        self.info = wx.StaticText(self, label="")
        self.info.SetForegroundColour(wx.RED)
        self.sizer.Add(self.info, 0, wx.ALL | wx.CENTER, 10)

        # Email error static_text:
        self.email_error = wx.StaticText(self, label="")
        self.email_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.email_error, 0, wx.ALL | wx.CENTER, 10)

        # Email text_ctrl
        self.email_ctrl = wx.TextCtrl(self, value="", pos=(50, 50), size=(200, -1))
        self.email_ctrl.SetHint("Email: ")
        self.sizer.Add(self.email_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # password error static_text:
        self.password_error = wx.StaticText(self, label="")
        self.password_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.password_error, 0, wx.ALL | wx.CENTER, 10)

        # Password text_ctrl
        self.password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, pos=(50, 50), size=(200, -1))
        self.password_ctrl.SetHint("Password: ")
        self.sizer.Add(self.password_ctrl, 0, wx.ALL | wx.CENTER, 10)

        self.login_btn = wx.Button(self, label="Login")
        self.sizer.Add(self.login_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(self.sizer)

        self.home_btn = wx.Button(self, label="Go Home")
        self.sizer.Add(self.home_btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(self.sizer)

        self.home_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("home"))
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)

    def on_login(self, event):
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
            res = self.send_to_server(f"LOGIN, {email}, {password}")
            if "Login was successful" in res:
                self.info.SetLabel("Login Successful")
                globals["auth_state"] = True
                username = res.split(",")[1]
                print(username)
                print(email)
                globals["user_name"] = username
                self.switch_panel("home")
            else:
                self.info.SetLabel(res)
