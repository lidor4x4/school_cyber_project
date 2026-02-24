import wx
import re
from globals import globals
import utils.utils as utils


class SignupPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server 
        self.methods = utils.Utils()

        # Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, label="Signup Page"), 0, wx.ALL | wx.CENTER, 10)

        self.go_back_btn = wx.Button(self, label="Go Back")
        self.go_back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("home"))
        self.sizer.Add(self.go_back_btn, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)


        # username error static_text:
        self.username_error = wx.StaticText(self, label="")
        self.username_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.username_error, 0, wx.ALL | wx.CENTER, 10)

        # username text_ctrl
        self.username_ctrl = wx.TextCtrl(self, value="", size=(200, -1))
        self.username_ctrl.SetHint("Username: ")
        self.sizer.Add(self.username_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # Email error static_text:
        self.email_error = wx.StaticText(self, label="")
        self.email_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.email_error, 0, wx.ALL | wx.CENTER, 10)

        # Email text_ctrl
        self.email_ctrl = wx.TextCtrl(self, value="", size=(200, -1))
        self.email_ctrl.SetHint("Email: ")
        self.sizer.Add(self.email_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # Password error static_text:
        self.password_error = wx.StaticText(self, label="")
        self.password_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.password_error, 0, wx.ALL | wx.CENTER, 10)

        # Password text_ctrl
        self.password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, size=(200, -1))
        self.password_ctrl.SetHint("Password: ")
        self.sizer.Add(self.password_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # Confirm password error static_text:
        self.confirm_password_error = wx.StaticText(self, label="")
        self.confirm_password_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.confirm_password_error, 0, wx.ALL | wx.CENTER, 10)

        # Confirm password text_ctrl
        self.confirm_password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, size=(200, -1))
        self.confirm_password_ctrl.SetHint("Confirm password: ")
        self.sizer.Add(self.confirm_password_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # selection check error static_text:
        self.slection_error = wx.StaticText(self, label="")
        self.slection_error.SetForegroundColour(wx.RED)
        self.sizer.Add(self.slection_error, 0, wx.ALL | wx.CENTER, 10)

        self.chk_patient = wx.CheckBox(self, label="I'm a patient")
        self.chk_dr = wx.CheckBox(self, label="I'm a doctor")

        self.sizer.Add(self.chk_patient, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.chk_dr, 0, wx.ALL | wx.CENTER, 5)

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
        username = self.username_ctrl.GetValue()
        email = self.email_ctrl.GetValue()
        password = self.password_ctrl.GetValue()
        confirm_password = self.confirm_password_ctrl.GetValue()
        errors = False

        # Input check
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
        if not valid:
            self.email_error.SetLabel("Invalid Email")
            errors = True

        if len(password) < 8:
            self.password_error.SetLabel("Password must be at least 8 characters long")
            errors = True

        if password != confirm_password:
            self.confirm_password_error.SetLabel("The two passwords should be the same.")
            errors = True

        if self.chk_dr.IsChecked() and self.chk_patient.IsChecked():
            self.slection_error.SetLabel("You must choose one user type")
            errors = True

        if not errors:
            selected = ""
            if self.chk_patient.IsChecked(): 
                selected = "patient"
            if self.chk_dr.IsChecked(): 
                selected = "dr"
            res = self.send_to_server(f"SIGN_UP, {email}, {password}, {username}, {selected}")
            if "successful" in res:
                globals["auth_state"] = True
                globals["user_name"] = username
                globals["user_role"] = selected
                self.switch_panel("home")
