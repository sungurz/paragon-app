import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from app.db.database import SessionLocal
from app.db.models import User
from app.auth.security import hash_password


class AddUserDialog(tb.Toplevel):
    """
    Modal dialog for creating or editing a user.

    After wait_window() returns check:
        dialog.submitted       — True if confirmed
        dialog.result_*        — values entered
    """

    def __init__(self, parent, editing: bool = False):
        super().__init__(parent)
        self.editing = editing
        self.db = SessionLocal()

        self.submitted        = False
        self.result_username  = ""
        self.result_password  = ""
        self.result_role      = ""
        self.result_full_name = ""

        self.title("Edit User" if editing else "Add New User")
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()

        # Center over parent
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - 380) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - 430) // 2
        self.geometry(f"380x430+{px}+{py}")

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self):
        frame = tb.Frame(self, padding=28)
        frame.pack(fill=BOTH, expand=YES)

        tb.Label(
            frame,
            text="Edit User" if self.editing else "Add New User",
            font=("Georgia", 17, "bold"),
        ).pack(anchor=W, pady=(0, 18))

        # Username
        tb.Label(frame, text="Username", font=("Helvetica", 11),
                 bootstyle="secondary").pack(anchor=W)
        self.username_input = tb.Entry(frame, font=("Helvetica", 12), width=36)
        self.username_input.pack(fill=X, pady=(2, 12))

        # Full Name
        tb.Label(frame, text="Full Name", font=("Helvetica", 11),
                 bootstyle="secondary").pack(anchor=W)
        self.full_name_input = tb.Entry(frame, font=("Helvetica", 12), width=36)
        self.full_name_input.pack(fill=X, pady=(2, 12))

        # Password
        tb.Label(frame, text="Password", font=("Helvetica", 11),
                 bootstyle="secondary").pack(anchor=W)
        self.password_input = tb.Entry(
            frame, font=("Helvetica", 12), width=36,
            show="•",
        )
        if self.editing:
            self.password_input.configure({"show": "•"})
        self.password_input.pack(fill=X, pady=(2, 12))

        # Role
        tb.Label(frame, text="Role", font=("Helvetica", 11),
                 bootstyle="secondary").pack(anchor=W)
        self.role_var = tb.StringVar(value="staff")
        tb.Combobox(
            frame, textvariable=self.role_var,
            values=["manager", "location_admin", "front_desk",'finance_manager', 'maintenance_staff'],
            state="readonly", font=("Helvetica", 12), width=34,
        ).pack(fill=X, pady=(2, 18))

        # Submit
        tb.Button(
            frame,
            text="Save Changes" if self.editing else "Create User",
            bootstyle="primary",
            padding=(0, 9),
            command=self._submit,
        ).pack(fill=X)

    # ── Submit ────────────────────────────────────────────
    def _submit(self):
        username  = self.username_input.get().strip()
        password  = self.password_input.get()
        role      = self.role_var.get()
        full_name = self.full_name_input.get().strip()

        if not username:
            Messagebox.show_warning("Username is required.", title="Validation Error", parent=self)
            return
        if not password and not self.editing:
            Messagebox.show_warning("Password is required.", title="Validation Error", parent=self)
            return

        # Duplicate check (create only)
        exists = self.db.query(User).filter(User.username == username).first()
        if exists and not self.editing:
            Messagebox.show_warning(
                "That username already exists.", title="Duplicate Username", parent=self
            )
            return

        if not self.editing:
            from app.db.models import Role, RoleName
            role_record = self.db.query(Role).filter(Role.name == role).first()
            if not role_record:
                Messagebox.show_warning(f'Role {role} not found.', title='Error', parent=self)
                return
            
            new_user = User(
                username = username,
                password_hash = hash_password(password),
                role_id=role_record.id,
                full_name=full_name,
            )
            self.db.add(new_user)
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                Messagebox.show_warning('Username already exists!', title='Error', parent=self)
                return
            Messagebox.show_info('User created successfully!', title='Success',parent=self)   
        self.result_username  = username
        self.result_password  = password
        self.result_role      = role
        self.result_full_name = full_name
        self.submitted        = True
        self.destroy()