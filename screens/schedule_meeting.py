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

        self.title_font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.card_title_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.schedule_meeting_text = wx.StaticText(self, label="Schedule Meeting Page")
        self.schedule_meeting_text.SetFont(self.title_font)
        self.sizer.Add(self.schedule_meeting_text, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        go_back_btn = wx.Button(self, label="Go Back")
        go_back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("home"))
        self.sizer.Add(go_back_btn, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)

        self.loading_text = wx.StaticText(self, label="Loading doctors...")
        self.loading_text.SetFont(self.title_font)
        self.sizer.Add(self.loading_text, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        self.grid_sizer = wx.GridSizer(cols=3, hgap=20, vgap=20)

        # Create a ScrolledWindow for the doctor cards to be displayed in a scrollable area
        self.scroll_panel = wx.ScrolledWindow(self, size=(500, 500))  # Set initial size
        self.scroll_panel.SetScrollRate(5, 5)  # Control scrolling speed
        self.scroll_panel.SetSizer(self.grid_sizer)

        self.sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 20)

        self.SetSizer(self.sizer)
        self.Layout()

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

        self.scroll_panel.Show()  # Show the scrollable area

        self.Layout()

        self.Thaw()
        self.Refresh()

    def create_doctor_card(self, dr_username):
        card = wx.Panel(self.scroll_panel, style=wx.BORDER_SIMPLE)
        card.SetBackgroundColour(wx.Colour(245, 245, 245))

        card_sizer = wx.BoxSizer(wx.VERTICAL)

        dr_username_text = wx.StaticText(
            card,
            label=f"Dr. {dr_username}",
            style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        dr_username_text.SetFont(self.card_title_font)
        dr_username_text.Wrap(200)  
        card_sizer.Add(dr_username_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        dr_specialty = self.send_to_server(f"GET_DR_SPECIALTY_BY_USERNAME,{dr_username}")
        dr_username_specialty = wx.StaticText(
            card,
            label=f"Specializes in: {dr_specialty}",
            style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        dr_username_specialty.SetFont(self.card_title_font)
        dr_username_specialty.Wrap(200)
        card_sizer.Add(dr_username_specialty, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        users_in_queue = self.send_to_server(
            f"GET_DR_QUEUE_BY_USERNAME,{dr_username}"
        )

        if not users_in_queue or "empty" in users_in_queue.lower():
            count = 0
        else:
            count = len(users_in_queue.split(","))

        queue_text = wx.StaticText(card, label=f"{count} users in queue")
        queue_text.SetFont(self.card_title_font)
        card_sizer.Add(queue_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        btn = wx.Button(card, label="Schedule Meeting")
        btn.Bind(wx.EVT_BUTTON, lambda evt, u=dr_username: self.verify_user_click(u))
        card_sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        card.SetSizer(card_sizer)

        self.grid_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 5)

        card.Bind(wx.EVT_ENTER_WINDOW, lambda evt: self.on_card_hover(card, True))
        card.Bind(wx.EVT_LEAVE_WINDOW, lambda evt: self.on_card_hover(card, False))

    def on_card_hover(self, card, hover):
        card.SetBackgroundColour(wx.Colour(230, 230, 230) if hover else wx.Colour(245, 245, 245))
        card.Refresh()

    def verify_user_click(self, dr_username):
        try:
            username = globals["user_name"]

            print("dr username", dr_username)
            print("username", username)

            print(f"TEST: ADD_TO_DR_QUEUE,{dr_username},{username}")

            returned = self.send_to_server(
                f"ADD_TO_DR_QUEUE,{dr_username},{username}"
            )

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