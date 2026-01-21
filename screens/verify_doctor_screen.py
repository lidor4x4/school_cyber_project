import wx
import threading
from time import sleep
import utils.utils as utils

class VerifyDoctorPanel(wx.Panel):
    def __init__(self, parent, switch_panel=None, send_to_server=None):
        super().__init__(parent)

        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.methods = utils.Utils()
        self.updating = False 

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Verify Doctors.")
        title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_font.SetUnderlined(True)
        self.title.SetFont(title_font)
        self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        self.grid_sizer = wx.GridSizer(cols=4, hgap=20, vgap=20)
        self.main_sizer.Add(self.grid_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(self.main_sizer)
        self.Layout()

        threading.Thread(target=self.update_data_loop, daemon=True).start()
        
    def update_grid(self, users):
        self.updating = True

        for child in self.grid_sizer.GetChildren():
            win = child.GetWindow()
            if win:
                win.Destroy()
        self.grid_sizer.Clear(True)  

        email_font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        for email in users:
            card_sizer = wx.BoxSizer(wx.VERTICAL)

            email_text = wx.StaticText(self, label=email)
            email_text.SetFont(email_font)
            card_sizer.Add(email_text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

            btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

            yes_btn = wx.Button(self, label="YES")
            yes_btn.Bind(wx.EVT_BUTTON, lambda evt, e=email: self.verify_user_click(e, True))
            btn_sizer.Add(yes_btn, 0, wx.RIGHT, 5)

            no_btn = wx.Button(self, label="NO")
            no_btn.Bind(wx.EVT_BUTTON, lambda evt, e=email: self.reject_user_click(e))
            btn_sizer.Add(no_btn, 0)

            card_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)

            self.grid_sizer.Add(card_sizer, 0, wx.ALIGN_CENTER)


        self.grid_sizer.Layout()
        self.Layout()
        self.Refresh()
        self.updating = False

    def verify_user_click(self, email, verify, event=None):
        self.methods.verify_user(email, verify)

        users = self.methods.get_unverified_users()
        wx.CallAfter(self.update_grid, users)

    def reject_user_click(self, email):
        self.methods.reject_user(email)

        users = self.methods.get_unverified_users()
        wx.CallAfter(self.update_grid, users)

    def update_data_loop(self):
        while True:
            if not self.updating:
                users = self.methods.get_unverified_users()
                wx.CallAfter(self.update_grid, users)
            sleep(3)
