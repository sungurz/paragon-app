from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)
from app.db.database import SessionLocal
from app.db.models import User
from app.auth.security import hash_password


class AddUserDialog(QDialog):
    def __init__(self,editing=False):
        super().__init__()
        self.setWindowTitle("Add User")
        self.resize(300, 200)
        self.editing = editing

        self.db = SessionLocal()

        layout = QVBoxLayout()

        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Password
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Role
        layout.addWidget(QLabel("Role:"))
        self.role_input = QComboBox()
        self.role_input.addItems(["admin", "manager", "staff"])
        layout.addWidget(self.role_input)

        # Submit button
        self.btn_submit = QPushButton("Create User")
        layout.addWidget(self.btn_submit)

        self.setLayout(layout)

        # connect
        self.btn_submit.clicked.connect(self.create_user)

    def create_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()

        if not username:
            QMessageBox.warning(self, "Error", "username is required.")
            return
        if not password and not self.editing:
            QMessageBox.warning(self,'Error', 'Password is required.')

        # Check existing
        exists = self.db.query(User).filter(User.username == username).first()
        if exists:
            QMessageBox.warning(self, "Error", "Username already exists!")
            return

        new_user = User(
            username=username,
            password_hash=hash_password(password),
            role=role
        )

        self.db.add(new_user)
        self.db.commit()

        QMessageBox.information(self, "Success", "User created successfully!")
        self.accept()