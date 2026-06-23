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
        self.stop_event = threading.Event()
        self.cards = {}  # email -> card panel

        self.title_font = wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title_font.SetUnderlined(True)
        self.email_font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.build_title()
        self.build_empty_label()
        self.build_grid()
        self.build_back_button()

        self.Layout()
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)

        threading.Thread(target=self.poll_loop, daemon=True).start()


    def build_title(self):
        self.title = wx.StaticText(self, label="Verify Doctors.")
        self.title.SetFont(self.title_font)
        self.main_sizer.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

    def build_empty_label(self):
        self.empty_label = wx.StaticText(self, label="No doctors pending verification.")
        self.empty_label.SetFont(self.email_font)
        self.empty_label.SetForegroundColour(wx.Colour(107, 107, 107))
        self.empty_label.Hide()
        self.main_sizer.Add(self.empty_label, 0, wx.ALIGN_CENTER | wx.ALL, 20)

    def build_grid(self):
        self.grid_sizer = wx.GridSizer(cols=4, hgap=20, vgap=20)
        self.main_sizer.Add(self.grid_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

    def build_back_button(self):
        go_back_btn = wx.Button(self, label="Go Back")
        go_back_btn.Bind(wx.EVT_BUTTON, self.on_go_back)
        self.main_sizer.Add(go_back_btn, 0, wx.RIGHT, 5)


    def on_destroy(self, event):
        self.stop_event.set()
        event.Skip()

    def on_go_back(self, event):
        self.stop_event.set()
        self.switch_panel("home")


    def poll_loop(self):
        while not self.stop_event.is_set():
            users = self.send_to_server("GET_UNVERIFIED").split(",")
            wx.CallAfter(self.add_new_cards, users)
            sleep(3)


    def add_new_cards(self, users):
        if self.stop_event.is_set():
            return

        for email in users:
            email = email.strip()
            if email and email not in self.cards:
                self.add_card(email)

        self.empty_label.Show(len(self.cards) == 0)
        self.grid_sizer.Layout()
        self.Layout()
        self.Refresh()

    def add_card(self, email):
        card = wx.Panel(self)
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        email_text = wx.StaticText(card, label=email)
        email_text.SetFont(self.email_font)
        card_sizer.Add(email_text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        yes_btn = wx.Button(card, label="YES")
        yes_btn.SetBackgroundColour(wx.Colour(15, 110, 86))
        yes_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        yes_btn.Bind(wx.EVT_BUTTON, lambda evt, e=email, c=card: self.on_verify(e, c))

        no_btn = wx.Button(card, label="NO")
        no_btn.SetBackgroundColour(wx.Colour(180, 35, 35))
        no_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        no_btn.Bind(wx.EVT_BUTTON, lambda evt, e=email, c=card: self.on_reject(e, c))

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(yes_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(no_btn, 0)

        card_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        card.SetSizer(card_sizer)

        self.grid_sizer.Add(card, 0, wx.ALIGN_CENTER)
        self.cards[email] = card

    def remove_card(self, email, card):
        self.grid_sizer.Detach(card)
        card.Destroy()
        self.cards.pop(email, None)
        self.empty_label.Show(len(self.cards) == 0)
        self.grid_sizer.Layout()
        self.Layout()
        self.Refresh()

    def on_verify(self, email, card):
        self.remove_card(email, card)
        threading.Thread(target=self.methods.verify_user, args=(email, True), daemon=True).start()

    def on_reject(self, email, card):
        self.remove_card(email, card)
        threading.Thread(target=self.methods.reject_user, args=(email,), daemon=True).start()