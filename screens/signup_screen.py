import wx
import re
from globals import globals
import utils.utils as utils
import threading


class SignupPanel(wx.Panel):
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
        header_sizer.AddSpacer(60)
        header_panel.SetSizer(header_sizer)
        self.sizer.Add(header_panel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        # ── Title ─────────────────────────────────────────────────────────────
        self.sizer.AddSpacer(24)

        page_title = wx.StaticText(self, label="Create an account")
        page_title.SetFont(self.title_font)
        page_title.SetForegroundColour(wx.Colour(26, 26, 26))
        self.sizer.Add(page_title, 0, wx.ALL | wx.CENTER, 4)

        page_sub = wx.StaticText(self, label="Fill in the details below to get started.")
        page_sub.SetFont(self.label_font)
        page_sub.SetForegroundColour(wx.Colour(107, 107, 107))
        self.sizer.Add(page_sub, 0, wx.ALL | wx.CENTER, 4)

        self.sizer.AddSpacer(16)

        # ── Username ──────────────────────────────────────────────────────────
        self.username_error = wx.StaticText(self, label="")
        self.username_error.SetFont(self.error_font)
        self.username_error.SetForegroundColour(wx.Colour(162, 45, 45))
        self.sizer.Add(self.username_error, 0, wx.LEFT | wx.RIGHT, 60)

        self.username_ctrl = wx.TextCtrl(self, value="", size=(300, 36))
        self.username_ctrl.SetHint("Username")
        self.username_ctrl.SetFont(self.body_font)
        self.sizer.Add(self.username_ctrl, 0, wx.ALL | wx.CENTER, 6)

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

        # ── Confirm password ──────────────────────────────────────────────────
        self.confirm_password_error = wx.StaticText(self, label="")
        self.confirm_password_error.SetFont(self.error_font)
        self.confirm_password_error.SetForegroundColour(wx.Colour(162, 45, 45))
        self.sizer.Add(self.confirm_password_error, 0, wx.LEFT | wx.RIGHT, 60)

        self.confirm_password_ctrl = wx.TextCtrl(self, value="", style=wx.TE_PASSWORD, size=(300, 36))
        self.confirm_password_ctrl.SetHint("Confirm password")
        self.confirm_password_ctrl.SetFont(self.body_font)
        self.sizer.Add(self.confirm_password_ctrl, 0, wx.ALL | wx.CENTER, 6)

        self.sizer.AddSpacer(10)

        # ── Role selection ────────────────────────────────────────────────────
        self.slection_error = wx.StaticText(self, label="")
        self.slection_error.SetFont(self.error_font)
        self.slection_error.SetForegroundColour(wx.Colour(162, 45, 45))
        self.sizer.Add(self.slection_error, 0, wx.ALL | wx.CENTER, 2)

        self.chk_patient = wx.CheckBox(self, label="I'm a patient")
        self.chk_patient.SetFont(self.label_font)
        self.chk_patient.SetForegroundColour(wx.Colour(26, 26, 26))
        self.sizer.Add(self.chk_patient, 0, wx.ALL | wx.CENTER, 4)

        self.chk_dr = wx.CheckBox(self, label="I'm a doctor")
        self.chk_dr.SetFont(self.label_font)
        self.chk_dr.SetForegroundColour(wx.Colour(26, 26, 26))
        self.chk_dr.Bind(wx.EVT_CHECKBOX, self.on_doctor_checked)
        self.sizer.Add(self.chk_dr, 0, wx.ALL | wx.CENTER, 4)

        # ── Doctor specialty ──────────────────────────────────────────────────
        self.dr_specialty_ctrl_error = wx.StaticText(self, label="")
        self.dr_specialty_ctrl_error.SetFont(self.error_font)
        self.dr_specialty_ctrl_error.SetForegroundColour(wx.Colour(162, 45, 45))
        self.sizer.Add(self.dr_specialty_ctrl_error, 0, wx.LEFT | wx.RIGHT, 60)

        self.dr_specialty_ctrl = wx.TextCtrl(self, value="", size=(300, 36))
        self.dr_specialty_ctrl.SetHint("Your specialty")
        self.dr_specialty_ctrl.SetFont(self.body_font)
        self.sizer.Add(self.dr_specialty_ctrl, 0, wx.ALL | wx.CENTER, 6)
        self.dr_specialty_ctrl.Hide()

        self.sizer.AddSpacer(16)

        # ── Signup button ─────────────────────────────────────────────────────
        self.signup_btn = wx.Button(self, label="Create Account", size=(300, 44))
        self.signup_btn.SetBackgroundColour(wx.Colour(15, 110, 86))
        self.signup_btn.SetForegroundColour(wx.Colour(225, 245, 238))
        self.signup_btn.SetFont(self.body_font)
        self.signup_btn.Bind(wx.EVT_BUTTON, self.on_signup)
        self.sizer.Add(self.signup_btn, 0, wx.ALL | wx.CENTER, 5)

        # ── Back to home button ───────────────────────────────────────────────
        self.back_btn = wx.Button(self, label="Back to Home", size=(300, 36))
        self.back_btn.SetFont(self.label_font)
        self.back_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        self.back_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("home"))
        self.sizer.Add(self.back_btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(self.sizer)

    def on_doctor_checked(self, event):
        if self.chk_dr.IsChecked():
            self.dr_specialty_ctrl.Show()
        else:
            self.dr_specialty_ctrl.Hide()
        self.Layout()

    def on_signup(self, event):
        username = self.username_ctrl.GetValue()
        email = self.email_ctrl.GetValue()
        password = self.password_ctrl.GetValue()
        confirm_password = self.confirm_password_ctrl.GetValue()
        dr_specialty = self.dr_specialty_ctrl.GetValue()

        self.username_error.SetLabel("")
        self.email_error.SetLabel("")
        self.password_error.SetLabel("")
        self.confirm_password_error.SetLabel("")
        self.slection_error.SetLabel("")
        self.dr_specialty_ctrl_error.SetLabel("")

        errors = False

        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
        if not valid:
            self.email_error.SetLabel("Invalid email address")
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

        if not self.chk_dr.IsChecked() and not self.chk_patient.IsChecked():
            self.slection_error.SetLabel("You must choose a user type")
            errors = True

        if self.chk_dr.IsChecked() and dr_specialty == "":
            self.dr_specialty_ctrl_error.SetLabel("You need to specify your specialty.")
            errors = True

        if not errors:
            if not dr_specialty:
                dr_specialty = ""

            selected = ""
            if self.chk_patient.IsChecked():
                selected = "patient"
            if self.chk_dr.IsChecked():
                selected = "dr"

            res = self.send_to_server(f"SIGN_UP, {email}, {password}, {username}, {selected}, {dr_specialty}")
            if "successful" in res:
                globals["auth_state"] = True
                globals["user_name"] = username
                globals["user_role"] = selected
                self.switch_panel("home")