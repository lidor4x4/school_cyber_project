import wx
import utils.utils as utils
from globals import globals

class MedicationScreen(wx.Panel):
    def __init__(self, parent, switch_panel=None, send_to_server=None):
        super().__init__(parent)

        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.methods = utils.Utils()
        self.username = globals["user_name"].strip()
        self.user_role = self.send_to_server(f"GET_USER_ROLE_BY_USERNAME,{self.username}")
        print("The user's role is", self.user_role)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        if self.user_role == "patient":
            self.title = wx.StaticText(self, label=f"Hello {self.username} your prescribed medication is:")
            title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            title_font.SetUnderlined(True)
            self.title.SetFont(title_font)

            self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        elif self.user_role == "dr":
            self.title = wx.StaticText(self, label=f"Hello Dr.{self.username} your patient's medication is:")
            title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            title_font.SetUnderlined(True)
            self.title.SetFont(title_font)

            self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)



        go_back_btn = wx.Button(self, label="Go Back")
        go_back_btn.Bind(wx.EVT_BUTTON, self.on_go_back)
        self.main_sizer.Add(go_back_btn, 0, wx.RIGHT, 5)

        self.SetSizer(self.main_sizer)
        self.Layout()


    def on_go_back(self, event):
        if self.switch_panel:
            self.switch_panel("home")


