import wx
import threading
from globals import globals
import utils.utils as utils


class StaffPanel(wx.Panel):
    def __init__(self, parent, switch_panel, send_to_server):
        super().__init__(parent)

        self.methods = utils.Utils()
        self.switch_panel = switch_panel
        self.send_to_server = send_to_server

        self.SetBackgroundColour(wx.Colour(245, 245, 242))

        self.title_font     = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD,   False, "Georgia")
        self.body_font      = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.label_font     = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")
        self.card_title_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD,  False, "Arial")
        self.card_body_font  = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Arial")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

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

        top_row = wx.BoxSizer(wx.HORIZONTAL)

        page_title = wx.StaticText(self, label="Staff Management")
        page_title.SetFont(self.title_font)
        page_title.SetForegroundColour(wx.Colour(26, 26, 26))
        top_row.Add(page_title, 1, wx.ALIGN_CENTER_VERTICAL)

        refresh_btn = wx.Button(self, label="⟳ Refresh", size=(100, 32))
        refresh_btn.SetFont(self.label_font)
        refresh_btn.SetForegroundColour(wx.Colour(107, 107, 107))
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        top_row.Add(refresh_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.Add(top_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
        self.sizer.AddSpacer(6)

        page_sub = wx.StaticText(self, label="View all registered doctors and manage their system access.")
        page_sub.SetFont(self.label_font)
        page_sub.SetForegroundColour(wx.Colour(107, 107, 107))
        self.sizer.Add(page_sub, 0, wx.LEFT, 20)

        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP, 12)

        self.loading_text = wx.StaticText(self, label="Loading staff...")
        self.loading_text.SetFont(self.body_font)
        self.loading_text.SetForegroundColour(wx.Colour(107, 107, 107))
        self.sizer.Add(self.loading_text, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        self.grid_sizer = wx.GridSizer(cols=3, hgap=14, vgap=14)

        self.scroll_panel = wx.ScrolledWindow(self, size=(500, 500))
        self.scroll_panel.SetScrollRate(5, 5)
        self.scroll_panel.SetBackgroundColour(wx.Colour(245, 245, 242))
        self.scroll_panel.SetSizer(self.grid_sizer)

        self.sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 16)

        self.SetSizer(self.sizer)
        self.Layout()

        self.doctor_cards = []   # list of (card_panel, dr_username)

        threading.Thread(target=self.load_staff, daemon=True).start()


    def load_staff(self):
        try:
            users_raw = self.send_to_server("GET_VERIFIED_DR_USERS")
            users = users_raw.split(",") if users_raw else []
            wx.CallAfter(self.populate_grid, users)
        except Exception as e:
            wx.CallAfter(wx.MessageBox, f"Error loading staff: {e}")

    def populate_grid(self, users):
        self.Freeze()

        self.grid_sizer.Clear(delete_windows=True)
        self.doctor_cards.clear()

        for dr_username in users:
            self.create_doctor_card(dr_username.strip())

        if hasattr(self, "loading_text") and self.loading_text:
            self.loading_text.Destroy()
            self.loading_text = None

        self.scroll_panel.Show()
        self.scroll_panel.FitInside()
        self.Layout()
        self.Thaw()
        self.Refresh()


    def create_doctor_card(self, dr_username):
        card = wx.Panel(self.scroll_panel, style=wx.BORDER_NONE)
        card.SetBackgroundColour(wx.Colour(255, 255, 255))

        card_sizer = wx.BoxSizer(wx.VERTICAL)

        accent = wx.Panel(card, size=(-1, 4))
        accent.SetBackgroundColour(wx.Colour(180, 35, 35))
        card_sizer.Add(accent, 0, wx.EXPAND)

        dr_name_text = wx.StaticText(
            card,
            label=f"Dr. {dr_username}",
            style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        dr_name_text.SetFont(self.card_title_font)
        dr_name_text.SetForegroundColour(wx.Colour(26, 26, 26))
        dr_name_text.Wrap(200)
        card_sizer.Add(dr_name_text, 0, wx.ALIGN_CENTER | wx.TOP | wx.LEFT | wx.RIGHT, 12)

        
        dr_specialty = self.send_to_server(f"GET_DR_SPECIALTY_BY_USERNAME,{dr_username}")
        specialty_text = wx.StaticText(
            card,
            label=dr_specialty if dr_specialty else "Unknown specialty",
            style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        )
        specialty_text.SetFont(self.card_body_font)
        specialty_text.SetForegroundColour(wx.Colour(107, 107, 107))
        specialty_text.Wrap(200)
        card_sizer.Add(specialty_text, 0, wx.ALIGN_CENTER | wx.TOP, 4)

        card_sizer.Add(wx.StaticLine(card), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        disable_btn = wx.Button(card, label="Disable Access", size=(-1, 34))
        disable_btn.SetBackgroundColour(wx.Colour(180, 35, 35))
        disable_btn.SetForegroundColour(wx.Colour(255, 235, 235))
        disable_btn.SetFont(self.label_font)
        disable_btn.Bind(
            wx.EVT_BUTTON,
            lambda evt, u=dr_username, c=card: self.on_disable_click(u, c)
        )
        card_sizer.Add(disable_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        card.SetSizer(card_sizer)

        self.grid_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 4)
        self.doctor_cards.append((card, dr_username))

        card.Bind(wx.EVT_ENTER_WINDOW, lambda evt, c=card: self.on_card_hover(c, True))
        card.Bind(wx.EVT_LEAVE_WINDOW, lambda evt, c=card: self.on_card_hover(c, False))


    def on_disable_click(self, dr_username, card):
        confirm = wx.MessageDialog(
            self,
            f"Are you sure you want to disable Dr. {dr_username}'s access?\nThis will prevent them from logging in.",
            "Confirm Disable",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        if confirm.ShowModal() == wx.ID_YES:
            try:
                result = self.send_to_server(f"DISABLE_DR_ACCESS,{dr_username}")
                if result == "OK":
                    wx.MessageBox(
                        f"Dr. {dr_username}'s access has been disabled.",
                        "Done",
                        wx.OK | wx.ICON_INFORMATION
                    )
                    # Remove card from the grid
                    self.Freeze()
                    self.grid_sizer.Detach(card)
                    card.Destroy()
                    self.doctor_cards = [(c, u) for c, u in self.doctor_cards if u != dr_username]
                    self.scroll_panel.FitInside()
                    self.Layout()
                    self.Thaw()
                    self.Refresh()
                else:
                    wx.MessageBox(
                        f"Failed to disable Dr. {dr_username}: {result}",
                        "Error",
                        wx.OK | wx.ICON_ERROR
                    )
            except Exception as e:
                wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)

        confirm.Destroy()

    def on_refresh(self, event):
        self.Freeze()
        self.grid_sizer.Clear(delete_windows=True)
        self.doctor_cards.clear()
        self.Thaw()
        threading.Thread(target=self.load_staff, daemon=True).start()

    def on_card_hover(self, card, hover):
        card.SetBackgroundColour(wx.Colour(255, 240, 240) if hover else wx.Colour(255, 255, 255))
        card.Refresh()