import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from app.db.database import SessionLocal
from app.db.models import User
from app.auth.security import hash_password


class UsersPage(tb.Frame):
    """Users management page using ttkbootstrap."""

    def __init__(self, parent):
        super().__init__(parent)
        self.db = SessionLocal()
        self._build_ui()
        self.load_users()

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tb.Frame(self, padding=(20, 16, 20, 8))
        header.pack(fill=X)

        tb.Label(header, text="Users", font=("Georgia", 20, "bold")).pack(side=LEFT)

        btn_bar = tb.Frame(header)
        btn_bar.pack(side=RIGHT)

        tb.Button(btn_bar, text="＋  Add User", bootstyle="success",
                  padding=(10, 6), command=self._open_add_dialog).pack(side=LEFT, padx=(0, 6))
        tb.Button(btn_bar, text="✎  Edit", bootstyle="secondary",
                  padding=(10, 6), command=self._edit_selected).pack(side=LEFT, padx=(0, 6))
        tb.Button(btn_bar, text="🗑  Delete", bootstyle="danger",
                  padding=(10, 6), command=self._delete_selected).pack(side=LEFT)

        tb.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=20)

        # Table
        table_frame = tb.Frame(self, padding=(20, 12, 20, 0))
        table_frame.pack(fill=BOTH, expand=YES)

        cols = ("id", "username", "role", "full_name")
        self.tree = tb.Treeview(
            table_frame, columns=cols, show="headings",
            bootstyle="dark", selectmode="browse",
        )

        col_cfg = [
            ("id",        "ID",        60,  CENTER),
            ("username",  "Username",  200, W),
            ("role",      "Role",      120, CENTER),
            ("full_name", "Full Name", 220, W),
        ]
        for col_id, heading, width, anchor in col_cfg:
            self.tree.heading(col_id, text=heading, anchor=anchor)
            self.tree.column(col_id, width=width, anchor=anchor, minwidth=40)

        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL,
                                 command=self.tree.yview, bootstyle="round-dark")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Footer count
        self._count_var = tb.StringVar()
        tb.Label(self, textvariable=self._count_var,
                 font=("Helvetica", 10), bootstyle="secondary").pack(
            anchor=E, padx=24, pady=(4, 10)
        )

    # ── Data ──────────────────────────────────────────────
    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        users = self.db.query(User).all()
        for user in users:
            self.tree.insert("", END, values=(
                user.id, user.username, user.role.name.value if user.role else "-", user.full_name))
            
        self._count_var.set(f"{len(users)} user(s)")

    def _selected_user_id(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0])["values"][0])

    # ── Actions ───────────────────────────────────────────
    def _open_add_dialog(self):
        from app.ui.add_user_dialog import AddUserDialog
        dlg = AddUserDialog(self)
        self.wait_window(dlg)
        self.db.rollback()
        self.load_users()

    def _edit_selected(self):
        from app.ui.add_user_dialog import AddUserDialog

        uid = self._selected_user_id()
        if uid is None:
            Messagebox.show_warning("Please select a user to edit.", title="No Selection")
            return

        user = self.db.query(User).filter(User.id == uid).first()
        if not user:
            return

        dlg = AddUserDialog(self, editing=True)
        dlg.username_input.insert(0, user.username)
        dlg.full_name_input.insert(0, user.full_name or "")
        dlg.password_input.configure({"show": "•"})
        dlg.role_var.set(user.role.name.value if user.role else 'manager')
        self.wait_window(dlg)

        if not dlg.submitted:
            return

        # Uniqueness check (excluding self)
        existing = (
            self.db.query(User)
            .filter(User.username == dlg.result_username, User.id != user.id)
            .first()
        )
        if existing:
            Messagebox.show_warning("That username is already taken.", title="Duplicate Username")
            return

        try:
            user.username  = dlg.result_username
            user.role      = dlg.result_role
            user.full_name = dlg.result_full_name
            if dlg.result_password:
                user.password_hash = hash_password(dlg.result_password)
            self.db.commit()
            Messagebox.show_info("User updated successfully!", title="Success")
        except Exception as exc:
            self.db.rollback()
            Messagebox.show_error(str(exc), title="Database Error")

        self.load_users()

    def _delete_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            Messagebox.show_warning("Please select a user to delete.", title="No Selection")
            return

        confirm = Messagebox.yesno(
            "Are you sure you want to delete this user?\nThis cannot be undone.",
            title="Confirm Delete",
        )
        if confirm == "Yes":
            user = self.db.query(User).filter(User.id == uid).first()
            if user:
                self.db.delete(user)
                self.db.commit()
                self.load_users()