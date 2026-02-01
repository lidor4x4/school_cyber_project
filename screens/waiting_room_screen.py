import wx
#import threading
from time import sleep
import utils.utils as utils

class WaitingRoomPanel(wx.Panel):
    def __init__(self, parent, switch_panel=None, send_to_server=None):
        super().__init__(parent)

        self.switch_panel = switch_panel
        self.send_to_server = send_to_server
        self.methods = utils.Utils()

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Waiting Room")
        title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_font.SetUnderlined(True)
        self.title.SetFont(title_font)
        self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        self.desc = wx.StaticText(self, label="Please wait for your turn.")
        desc_font = wx.Font(21, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.desc.SetFont(desc_font)
        self.main_sizer.Add(self.desc, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)


        self.SetSizer(self.main_sizer)
        self.Layout()

