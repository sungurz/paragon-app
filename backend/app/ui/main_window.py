from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt
from app.ui.users_page import UsersPage

class MainWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Dashboard - {role}")
        self.resize(900, 600)

        # --- Root container ---
        root = QWidget()
        root_layout = QHBoxLayout(root)

        # --- Sidebar ---
        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)

        btn_home = QPushButton("Home")
        btn_users = QPushButton("Users")
        btn_settings = QPushButton("Settings")

        sidebar.addWidget(btn_home)
        sidebar.addWidget(btn_users)
        sidebar.addWidget(btn_settings)
        sidebar.addStretch()

        # --- Pages (Stack) ---
        self.stack = QStackedWidget()

        # Home page
        home_page = QLabel(f"Welcome, {role}!")
        home_page.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Users page
        self.user_page = UsersPage()

        # Settings page
        settings_page = QLabel("Settings Page")
        settings_page.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add pages
        self.stack.addWidget(home_page)        # index 0
        self.stack.addWidget(self.user_page)   # index 1
        self.stack.addWidget(settings_page)    # index 2

        # REMOVE Users page for non-admin roles
        if role != "admin":
            users_tab_index = self.stack.indexOf(self.user_page)
            self.stack.removeWidget(self.user_page)
            btn_users.setEnabled(False)

        # Button actions
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_users.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        # Add sidebar + stack to layout
        root_layout.addLayout(sidebar, 1)
        root_layout.addWidget(self.stack, 4)

        self.setCentralWidget(root)