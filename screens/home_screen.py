import wx
from globals import globals

# Admin:
# admin@gmail.com
# 123456789


class HomePanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)
        self.switch_panel = switch_panel
        self.client_socket = send_to_server
        self.auth_state = globals["auth_state"]
        self.font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.home_screen_text = wx.StaticText(self, label="Home Page")
        self.home_screen_text.SetFont(self.font)
        self.sizer.Add(self.home_screen_text, 0, wx.ALL | wx.CENTER, 10)

        print(self.auth_state)
        def sign_admin(self):
            globals["auth_state"] = True
            globals["user_name"] = "user"
            
            # Clear the previous sizer contents
            self.sizer.Clear(True)
            
            # Create and center the "Welcome: ADMIN" label
            self.user_name_static_text = wx.StaticText(self, label=f"Welcome: user")
            self.user_name_static_text.SetFont(self.font)
            self.sizer.Add(self.user_name_static_text, 0, wx.ALL | wx.ALIGN_CENTER, 10)
            
            # Create and center the "Live Chat" button
            self.live_chat_btn = wx.Button(self, label="Live Chat")
            self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            self.live_chat_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("live_chat"))
            
            # Apply the updated sizer
            self.SetSizer(self.sizer)
            self.Layout()  # Refresh the layout after changes


        self.admin_btn = wx.Button(self, label="ADMIN LOGIN")
        self.sizer.Add(self.admin_btn, 0, wx.ALL | wx.CENTER, 5)
        self.admin_btn.Bind(wx.EVT_BUTTON, lambda e: sign_admin(self))


        # If the user is logged in
        if self.auth_state:
            user_name = globals["user_name"]
            self.user_name_static_text = wx.StaticText(self, label=f"Welcome: {user_name}")
            self.user_name_static_text.SetFont(self.font)
            self.sizer.Add(self.user_name_static_text, 0, wx.ALL | wx.CENTER, 10)
            self.live_chat_btn = wx.Button(self, label="Live Chat")
            self.sizer.Add(self.live_chat_btn, 0, wx.ALL | wx.CENTER, 5)
            self.live_chat_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("live_chat"))
            self.SetSizer(self.sizer)

        # else the user isn't logged in
        else:
            self.login_btn = wx.Button(self, label="Login")
            self.signup_btn = wx.Button(self, label="Sign Up")
            self.sizer.Add(self.login_btn, 0, wx.ALL | wx.CENTER, 5)
            self.sizer.Add(self.signup_btn, 0, wx.ALL | wx.CENTER, 5)
            self.SetSizer(self.sizer)
            
            self.login_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("login"))
            self.signup_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel("signup"))
