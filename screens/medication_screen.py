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

        self.SetBackgroundColour(wx.Colour(245, 245, 242))
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.Panel(self)
        header.SetBackgroundColour(wx.Colour(255, 255, 255))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        go_back_btn = wx.Button(header, label="Back")
        go_back_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        go_back_btn.Bind(wx.EVT_BUTTON, self.on_go_back)

        if self.user_role == "patient":
            title_text = f"Hello {self.username}, your prescribed medication"
        else:
            title_text = f"Hello Dr. {self.username}, your patient's medications"

        title = wx.StaticText(header, label=title_text)
        title.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia"))
        title.SetForegroundColour(wx.Colour(26, 26, 26))

        header_sizer.AddSpacer(12)
        header_sizer.Add(go_back_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer()
        header_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer()
        header_sizer.AddSpacer(12)
        header.SetSizer(header_sizer)
        header.SetMinSize((-1, 60))

        self.main_sizer.Add(header, 0, wx.EXPAND)
        self.main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)
        self.main_sizer.AddSpacer(20)

        if self.user_role == "patient":
            self.build_patient_view()
        elif self.user_role == "dr":
            self.build_doctor_view()

        self.SetSizer(self.main_sizer)
        self.Layout()

    def build_patient_view(self):
        response = self.send_to_server(f"GET_MY_MEDICATION,{self.username}")

        card = wx.Panel(self)
        card.SetBackgroundColour(wx.Colour(255, 255, 255))
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        if not response or response.strip() == "NONE" or response.strip() == "":
            msg = wx.StaticText(card, label="No medication prescribed yet.")
            msg.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial"))
            msg.SetForegroundColour(wx.Colour(150, 150, 150))
            card_sizer.Add(msg, 0, wx.ALL, 20)
        else:
            rx_label = wx.StaticText(card, label="Prescribed Medication:")
            rx_label.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial"))
            rx_label.SetForegroundColour(wx.Colour(107, 107, 107))

            rx_value = wx.StaticText(card, label=response.strip())
            rx_value.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial"))
            rx_value.SetForegroundColour(wx.Colour(15, 110, 86))

            card_sizer.Add(rx_label, 0, wx.LEFT | wx.TOP, 20)
            card_sizer.Add(rx_value, 0, wx.LEFT | wx.BOTTOM, 20)

        card.SetSizer(card_sizer)

        wrapper = wx.BoxSizer(wx.HORIZONTAL)
        wrapper.AddStretchSpacer()
        wrapper.Add(card, 0, wx.ALL, 10)
        wrapper.AddStretchSpacer()
        self.main_sizer.Add(wrapper, 0, wx.EXPAND)

    def build_doctor_view(self):
        response = self.send_to_server(f"GET_MY_PATIENTS_MEDICATION,{self.username}")

        scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        scroll.SetScrollRate(0, 10)
        scroll.SetBackgroundColour(wx.Colour(245, 245, 242))
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        if not response or response.strip() == "NONE" or response.strip() == "":
            msg = wx.StaticText(scroll, label="No patient medication records found.")
            msg.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial"))
            msg.SetForegroundColour(wx.Colour(150, 150, 150))
            scroll_sizer.Add(msg, 0, wx.ALL, 20)
        else:
            patients = response.strip().split(",")
            for entry in patients:
                if ":" not in entry:
                    continue
                patient_name, medication = entry.split(":", 1)
                card = self.make_patient_card(scroll, patient_name.strip(), medication.strip())
                scroll_sizer.Add(card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        scroll.SetSizer(scroll_sizer)
        self.main_sizer.Add(scroll, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

    def make_patient_card(self, parent, patient_name, medication):
        card = wx.Panel(parent)
        card.SetBackgroundColour(wx.Colour(255, 255, 255))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        info_sizer = wx.BoxSizer(wx.VERTICAL)

        name_label = wx.StaticText(card, label=patient_name)
        name_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial"))
        name_label.SetForegroundColour(wx.Colour(26, 26, 26))

        med_label = wx.StaticText(card, label=f"Medication:  {medication if medication else 'None prescribed'}")
        med_label.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial"))
        med_label.SetForegroundColour(wx.Colour(15, 110, 86) if medication else wx.Colour(150, 150, 150))

        info_sizer.Add(name_label, 0, wx.BOTTOM, 4)
        info_sizer.Add(med_label, 0)

        sizer.Add(info_sizer, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        card.SetSizer(sizer)
        return card

    def on_go_back(self, event):
        if self.switch_panel:
            self.switch_panel("home")