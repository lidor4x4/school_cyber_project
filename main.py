import wx
from screen_manager import MainFrame


class MyApp(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Center()
        frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
