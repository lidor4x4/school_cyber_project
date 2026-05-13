import wx
import threading
from globals import globals
import utils.utils as utils


class ScheduleMeetingPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)

        self.methods = utils.Utils()
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server

        self.SetBackgroundColour(wx.Colour(245, 245, 242))

        self.title_font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia")
        self.body_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.label_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.card_title_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial")
        self.card_body_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # ── Header ────────────────────────────────────────────────────────────
        header_panel = wx.Panel(self)
        header_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        header_panel.SetMinSize((-1, 70))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        go_back_btn = wx.Button(header_panel, label="← Back")
        go_back_btn.SetFont(self.label_font)
        go_back_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        go_back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("home"))

        app_title = wx.StaticText(header_panel, label="MedConnect")
        app_title.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Georgia"))
        app_title.SetForegroundColour(wx.Colour(26, 26, 26))

        header_sizer.AddSpacer(12)
        header_sizer.Add(go_back_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(app_title, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer(1)
        header_sizer.AddSpacer(60)
        header_panel.SetSizer(header_sizer)
        self.sizer.Add(header_panel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        # ── Page title + filter row ───────────────────────────────────────────
        top_row = wx.BoxSizer(wx.HORIZONTAL)

        self.schedule_meeting_text = wx.StaticText(self, label="Schedule a Meeting")
        self.schedule_meeting_text.SetFont(self.title_font)
        self.schedule_meeting_text.SetForegroundColour(wx.Colour(26, 26, 26))
        top_row.Add(self.schedule_meeting_text, 1, wx.ALIGN_CENTER_VERTICAL)

        self.cb = wx.ComboBox(self, size=(180, 32), choices=["All Specialties"], style=wx.CB_READONLY)
        self.cb.SetSelection(0)
        self.cb.SetFont(self.label_font)
        self.cb.Bind(wx.EVT_COMBOBOX, self.on_filter)
        top_row.Add(self.cb, 0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.Add(top_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.AddSpacer(6)

        page_sub = wx.StaticText(self, label="Browse available doctors and book your appointment.")
        page_sub.SetFont(self.label_font)
        page_sub.SetForegroundColour(wx.Colour(107, 107, 107))
        self.sizer.Add(page_sub, 0, wx.LEFT, 20)

        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP, 12)

        # ── Loading text ──────────────────────────────────────────────────────
        self.loading_text = wx.StaticText(self, label="Loading doctors...")
        self.loading_text.SetFont(self.body_font)
        self.loading_text.SetForegroundColour(wx.Colour(107, 107, 107))
        self.sizer.Add(self.loading_text, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        # ── Scrollable grid ───────────────────────────────────────────────────
        self.grid_sizer = wx.GridSizer(cols=3, hgap=14, vgap=14)

        self.scroll_panel = wx.ScrolledWindow(self, size=(500, 500))
        self.scroll_panel.SetScrollRate(5, 5)
        self.scroll_panel.SetBackgroundColour(wx.Colour(245, 245, 242))
        self.scroll_panel.SetSizer(self.grid_sizer)

        self.sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 16)

        self.SetSizer(self.sizer)
        self.Layout()

        self.doctors_specialties = []
        self.doctor_cards = []

        threading.Thread(target=self.load_users, daemon=True).start()

    def load_users(self):
        try:
            users_raw = self.send_to_server("GET_VERIFIED_DR_USERS")
            users = users_raw.split(",") if users_raw else []
            wx.CallAfter(self.add_users, users)
        except Exception as e:
            wx.CallAfter(wx.MessageBox, f"Error loading doctors: {e}")

    def add_users(self, users):
        self.Freeze()

        for email in users:
            self.create_doctor_card(email)

        if hasattr(self, "loading_text") and self.loading_text:
            self.loading_text.Destroy()

        unique_specialties = ["All Specialties"] + sorted(set(self.doctors_specialties))
        self.cb.SetItems(unique_specialties)
        self.cb.SetSelection(0)

        self.scroll_panel.Show()
        self.Layout()
        self.Thaw()
        self.Refresh()

    def create_doctor_card(self, dr_username):
        card = wx.Panel(self.scroll_panel, style=wx.BORDER_NONE)
        card.SetBackgroundColour(wx.Colour(255, 255, 255))

        card_sizer = wx.BoxSizer(wx.VERTICAL)

        # Teal accent bar at the top
        accent = wx.Panel(card, size=(-1, 4))
        accent.SetBackgroundColour(wx.Colour(15, 110, 86))
        card_sizer.Add(accent, 0, wx.EXPAND)

        # Doctor name
        dr_username_text = wx.StaticText(
            card,
            label=f"Dr. {dr_username}",
            style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        dr_username_text.SetFont(self.card_title_font)
        dr_username_text.SetForegroundColour(wx.Colour(26, 26, 26))
        dr_username_text.Wrap(200)
        card_sizer.Add(dr_username_text, 0, wx.ALIGN_CENTER | wx.TOP | wx.LEFT | wx.RIGHT, 12)

        # Specialty
        dr_specialty = self.send_to_server(f"GET_DR_SPECIALTY_BY_USERNAME,{dr_username}")
        self.doctors_specialties.append(dr_specialty)

        dr_username_specialty = wx.StaticText(
            card,
            label=dr_specialty,
            style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        dr_username_specialty.SetFont(self.card_body_font)
        dr_username_specialty.SetForegroundColour(wx.Colour(15, 110, 86))
        dr_username_specialty.Wrap(200)
        card_sizer.Add(dr_username_specialty, 0, wx.ALIGN_CENTER | wx.TOP, 4)

        card_sizer.Add(wx.StaticLine(card), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Queue count
        users_in_queue = self.send_to_server(f"GET_DR_QUEUE_BY_USERNAME,{dr_username}")
        if not users_in_queue or "empty" in users_in_queue.lower():
            count = 0
        else:
            count = len(users_in_queue.split(","))

        queue_text = wx.StaticText(card, label=f"{count} in queue")
        queue_text.SetFont(self.card_body_font)
        queue_text.SetForegroundColour(wx.Colour(107, 107, 107))
        card_sizer.Add(queue_text, 0, wx.ALIGN_CENTER | wx.TOP, 8)

        # Schedule button
        btn = wx.Button(card, label="Schedule Meeting", size=(-1, 34))
        btn.SetBackgroundColour(wx.Colour(15, 110, 86))
        btn.SetForegroundColour(wx.Colour(225, 245, 238))
        btn.SetFont(self.label_font)
        btn.Bind(wx.EVT_BUTTON, lambda evt, u=dr_username: self.verify_user_click(u))
        card_sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        card.SetSizer(card_sizer)

        self.grid_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 4)
        self.doctor_cards.append((card, dr_specialty))

        card.Bind(wx.EVT_ENTER_WINDOW, lambda evt: self.on_card_hover(card, True))
        card.Bind(wx.EVT_LEAVE_WINDOW, lambda evt: self.on_card_hover(card, False))

    def on_filter(self, event):
        selected = self.cb.GetValue()

        self.Freeze()
        self.grid_sizer.Clear(delete_windows=False)

        for card, specialty in self.doctor_cards:
            if selected == "All Specialties" or specialty == selected:
                card.Show()
                self.grid_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 4)
            else:
                card.Hide()

        self.scroll_panel.Layout()
        self.scroll_panel.FitInside()
        self.Thaw()
        self.Refresh()

    def on_card_hover(self, card, hover):
        card.SetBackgroundColour(wx.Colour(240, 250, 246) if hover else wx.Colour(255, 255, 255))
        card.Refresh()

    def verify_user_click(self, dr_username):
        try:
            username = globals["user_name"]

            print("dr username", dr_username)
            print("username", username)
            print(f"TEST: ADD_TO_DR_QUEUE,{dr_username},{username}")

            returned = self.send_to_server(f"ADD_TO_DR_QUEUE,{dr_username},{username}")

            print("returned", returned)

            if returned == "User already in queue":
                wx.MessageBox(
                    f"You already have a meeting with Dr. {dr_username}.",
                    "Not confirmed",
                    wx.OK | wx.ICON_INFORMATION
                )
            else:
                wx.MessageBox(
                    f"You now have a meeting with Dr. {dr_username}.",
                    "Confirmed",
                    wx.OK | wx.ICON_INFORMATION
                )

        except Exception as e:
            print(f"Error scheduling meeting: {e}")