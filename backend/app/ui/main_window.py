import ttkbootstrap as tb
from ttkbootstrap.constants import *
from app.ui.users_page import UsersPage


class MainWindow(tb.Frame):
    """Main dashboard window using ttkbootstrap."""

    SIDEBAR_W = 210

    def __init__(self, parent, role: str, show_login_callback):
        super().__init__(parent)
        self.role = role
        self.show_login_callback = show_login_callback
        self.pack(fill=BOTH, expand=YES)

        self._pages: dict[str, tb.Frame] = {}
        self._nav_buttons: dict[str, tb.Button] = {}

        self._build_layout()
        self._build_pages()
        self._show_page("home")

    # ── Layout ────────────────────────────────────────────
    def _build_layout(self):
        # Sidebar
        self.sidebar = tb.Frame(self, bootstyle="dark", width=self.SIDEBAR_W)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        # Brand block
        brand = tb.Frame(self.sidebar, bootstyle="dark", padding=(18, 20, 18, 12))
        brand.pack(fill=X)
        tb.Label(brand, text="PARAGON", font=("Georgia", 18, "bold"),
                 bootstyle="inverse-dark").pack(anchor=W)
        tb.Label(brand, text="Property Management System", font=("Helvetica", 9),
                 bootstyle="inverse-dark").pack(anchor=W)

        tb.Separator(self.sidebar, orient=HORIZONTAL).pack(fill=X, padx=0, pady=(0, 10))

        # Nav items
        nav_items = [("🏠   Home", "home"), ("⚙️   Settings", "settings")]
        if self.role in ("manager","location_admin"):
            nav_items.append(("👥   Users", "users"))

        for label, key in nav_items:
            btn = tb.Button(
                self.sidebar, text=label,
                bootstyle="secondary-outline",
                width=22, padding=(10, 8),
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(fill=X, padx=10, pady=3)
            self._nav_buttons[key] = btn

        # Logout (pinned to bottom)
        bottom = tb.Frame(self.sidebar, bootstyle="dark")
        bottom.pack(side=BOTTOM, fill=X, padx=10, pady=14)
        tb.Separator(self.sidebar, orient=HORIZONTAL).pack(side=BOTTOM, fill=X)
        tb.Button(
            bottom, text="⬅   Logout",
            bootstyle="danger-outline",
            width=22, padding=(10, 8),
            command=self._logout,
        ).pack(fill=X)

        # Content area
        self.content = tb.Frame(self)
        self.content.pack(side=RIGHT, fill=BOTH, expand=YES)

    # ── Pages ─────────────────────────────────────────────
    def _build_pages(self):
        # Home
        home = tb.Frame(self.content)
        inner = tb.Frame(home)
        inner.place(relx=0.5, rely=0.46, anchor="center")
        tb.Label(inner, text=f"Welcome to PARAGON PROPERTY MANAGEMENT SYSTEM {self.role.capitalize()}!",
                 font=("Georgia", 23, "bold")).pack()
        tb.Label(inner, text="Select an option from the sidebar to get started.",
                 font=("Helvetica", 12), bootstyle="secondary").pack(pady=(8, 0))
        self._pages["home"] = home

        # Settings (placeholder)
        settings = tb.Frame(self.content)
        tb.Label(settings, text="Settings", font=("Georgia", 28, "bold")).place(
            relx=0.5, rely=0.5, anchor="center"
        )
        self._pages["settings"] = settings

        # Users (admin only)
        if self.role in ("manager", 'location_admin'):
            users = UsersPage(self.content)
            self._pages["users"] = users

    def _show_page(self, name: str):
        for page in self._pages.values():
            page.pack_forget()

        # Highlight active nav button
        for key, btn in self._nav_buttons.items():
            if key == name:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="secondary-outline")

        if name in self._pages:
            self._pages[name].pack(fill=BOTH, expand=YES)

    # ── Logout ────────────────────────────────────────────
    def _logout(self):
        self.destroy()
        self.show_login_callback()