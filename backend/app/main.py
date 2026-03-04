import ttkbootstrap as tb
from app.ui.login_window import LoginWindow
from app.db.database import SessionLocal
from app.auth.login_service import authenticate_user


class ParagonApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Paragon — Property Management")
        self.resizable(True, True)
        self._current_frame = None
        self.show_login()

    # ── Login ──────────────────────────────────────────────
    def show_login(self):
        if self._current_frame:
            self._current_frame.destroy()
        self._center(440, 500)
        self._current_frame = LoginWindow(self, on_login_success=self._handle_login)

    def _handle_login(self, username: str, password: str, login_frame):
        db = SessionLocal()
        user = authenticate_user(db, username, password)
        
        if user:
            role_name = user.role.name
            db.close()
            login_frame.destroy()
            self._open_dashboard(role_name)
        else:
            db.close()
            login_frame.show_error('Invalid username or password. ')

    # ── Dashboard ──────────────────────────────────────────
    def _open_dashboard(self, role: str):
        from app.ui.main_window import MainWindow
        self._center(1050, 680)
        self.title(f"Paragon — {role.capitalize()} Dashboard")
        self._current_frame = MainWindow(self, role=role, show_login_callback=self.show_login)

    # ── Helpers ────────────────────────────────────────────
    def _center(self, w: int, h: int):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")


def main():
    app = ParagonApp()
    app.mainloop()


if __name__ == "__main__":
    main()