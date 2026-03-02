from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,QMessageBox
)
from app.db.database import SessionLocal
from app.db.models import User
from app.ui.add_user_dialog import AddUserDialog
from app.auth.security import hash_password

class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add User button
        self.btn_add = QPushButton("Add User")
        layout.addWidget(self.btn_add)
        self.btn_add.clicked.connect(self.open_add_user_dialog)

        # User table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.btn_edit = QPushButton('Edit Selected User')
        self.btn_delete = QPushButton('Delete Selected User')
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_delete)
        
        self.btn_edit.clicked.connect(self.edit_selected_user)
        self.btn_delete.clicked.connect(self.delete_selected_user)
        self.btn_edit.setFixedHeight(40)
        self.btn_delete.setFixedHeight(40)
        layout.addStretch()
        self.load_users()
        

    def load_users(self):
        users = self.db.query(User).all()
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.role))
            
    def open_add_user_dialog(self):
        dialog = AddUserDialog()
        if dialog.exec():
            self.load_users()        
            
    def edit_selected_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "No user selected.")
            return

        user_id = int(self.table.item(selected, 0).text())
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # Open dialog IN EDIT MODE
        dialog = AddUserDialog(editing=True)
        dialog.username_input.setText(user.username)
        dialog.password_input.setPlaceholderText("Leave blank to keep old password")

        index = dialog.role_input.findText(user.role)
        dialog.role_input.setCurrentIndex(index)

        if not dialog.exec():
            return

        new_username = dialog.username_input.text().strip()
        new_password = dialog.password_input.text().strip()
        new_role = dialog.role_input.currentText()

        # --- CHECK IF USERNAME EXISTS (EXCEPT CURRENT USER) ---
        existing = (
            self.db.query(User)
            .filter(User.username == new_username, User.id != user.id)
            .first()
        )

        if existing:
            QMessageBox.warning(self, "Error", "This username already exists!")
            return

        try:
            # Update user
            user.username = new_username
            user.role = new_role

            if new_password:
                user.password_hash = hash_password(new_password)

            self.db.commit()

            QMessageBox.information(self, "Success", "User updated!")

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
            return

        self.load_users()
    def delete_selected_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self,'Error','No user selected.')      
            return  
        user_id = int(self.table.item(selected,0).text())
        confirm = QMessageBox.question(
            self,
            'Confirm Delete',
            'Are you sure you want to delete this user? ',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                self.db.delete(user)
                self.db.commit()
                self.load_users()