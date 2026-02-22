import wx
from globals import globals
import utils.utils as utils


class ScheduleMeetingPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)

        self.methods = utils.Utils()
        self.switch_panel = switch_panel
        self.client_socket = send_to_server
        self.auth_state = globals["auth_state"]
        self.user_role = globals["user_role"]
        self.verified_dr = True

        self.title_font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.card_title_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.schedule_meeting_text = wx.StaticText(self, label="Schedule Meeting Page")
        self.schedule_meeting_text.SetFont(self.title_font)
        self.sizer.Add(self.schedule_meeting_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15,)

        go_back_btn = wx.Button(self, label="Go Back")
        go_back_btn.Bind(wx.EVT_BUTTON, lambda evt: self.switch_panel("home"))
        self.sizer.Add(go_back_btn, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)

        self.grid_sizer = wx.GridSizer(cols=4, hgap=20, vgap=20)
        self.sizer.Add(self.grid_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20,)

        self.SetSizer(self.sizer)

        users = self.methods.get_verified_dr_users()

        for email in users:
            self.create_doctor_card(email)

        self.Layout()
        self.Refresh()


    def create_doctor_card(self, dr_username):
        card = wx.Panel(self, style=wx.BORDER_SIMPLE)
        card.SetBackgroundColour(wx.Colour(245, 245, 245))
        card.SetMinSize((250, 150))

        card_sizer = wx.BoxSizer(wx.VERTICAL)

        dr_username_text = wx.StaticText(card, label=f"Dr. {dr_username}", style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        dr_username_text.SetFont(self.card_title_font)
        dr_username_text.Wrap(220)

        card_sizer.Add(dr_username_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        users_in_queue = self.methods.get_dr_queue_by_username(dr_username)
        if "The queue is empty" in users_in_queue:
            users_in_queue = None
        users_in_queue_count = str(len(users_in_queue.split(",")) if users_in_queue else 0)

        users_in_queue_text = wx.StaticText(
            card,
            label=f"{users_in_queue_count} users in queue."
        )
        users_in_queue_text.SetFont(self.card_title_font)

        card_sizer.Add(users_in_queue_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        schedule_btn = wx.Button(card, label="Schedule Meeting")
        schedule_btn.Bind(wx.EVT_BUTTON, lambda evt, u=dr_username: self.verify_user_click(u))

        card_sizer.Add(schedule_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        card.SetSizer(card_sizer)

        # Hover animation
        card.Bind(wx.EVT_ENTER_WINDOW, lambda evt: self.on_card_hover(card, True))
        card.Bind(wx.EVT_LEAVE_WINDOW, lambda evt: self.on_card_hover(card, False))

        self.grid_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 10)


    def on_card_hover(self, card, hover):
        if hover:
            card.SetBackgroundColour(wx.Colour(230, 230, 230))
        else:
            card.SetBackgroundColour(wx.Colour(245, 245, 245))
        card.Refresh()


    def verify_user_click(self, dr_username):
        try:
            username = globals["user_name"]
            print(f"Scheduling meeting with doctor: {dr_username} for user: {username}")
            returned = self.methods.add_to_dr_queue(dr_username, username)
            if returned == "User already in queue":
                wx.MessageBox(f"Scheduling wasn't successful you already have a meeting with: Dr. {dr_username}.", "meetings wasn't confirmed", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox(f'Scheduling was successful you have a meeting with: Dr. {dr_username}.', 'meetings confirmed', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            print(f"Error scheduling meeting: {e}")
