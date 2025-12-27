import os
import sqlite3
import subprocess
import platform
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QTextEdit, QFileDialog,
    QDateEdit, QTimeEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QDialog, QMessageBox, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QColor, QBrush, QFont

DB_FILE = "dental_appointments.db"

# ---------------- Helper Functions ----------------

def create_database():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                surname TEXT,
                date TEXT,
                time TEXT,
                phone TEXT,
                details TEXT,
                status TEXT,
                attachments TEXT
            )
        """)
        conn.commit()
        conn.close()

def save_to_db(data, update_id=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    attachments_str = ",".join(data["Attachments"]) if data["Attachments"] else ""
    if update_id:
        cursor.execute("""
            UPDATE appointments
            SET name=?, surname=?, date=?, time=?, phone=?, details=?, status=?, attachments=?
            WHERE id=?
        """, (
            data["Name"], data["Surname"], data["Date"], data["Time"],
            data["Phone"], data["Details"], data["Status"], attachments_str, update_id
        ))
    else:
        cursor.execute("""
            INSERT INTO appointments (
                name, surname, date, time, phone, details, status, attachments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["Name"], data["Surname"], data["Date"], data["Time"],
            data["Phone"], data["Details"], data["Status"], attachments_str
        ))
    conn.commit()
    conn.close()

def fetch_all_appointments():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, surname, date, time, details, status, attachments
        FROM appointments
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_appointment_by_id(app_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE id=?", (app_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def open_file(path):
    if platform.system() == "Darwin":
        subprocess.call(("open", path))
    elif platform.system() == "Windows":
        os.startfile(path)
    else:
        subprocess.call(("xdg-open", path))

# ---------------- Patient Details Window ----------------

class PatientDetailsWindow(QDialog):
    def __init__(self, appointment_id):
        super().__init__()
        self.setWindowTitle("Patient Details")
        self.setGeometry(200, 200, 450, 550)
        layout = QFormLayout()
        self.setLayout(layout)

        row = fetch_appointment_by_id(appointment_id)
        if not row:
            layout.addRow(QLabel("Appointment not found"))
            return

        labels = ["ID", "Name", "Surname", "Date", "Time", "Phone",
                  "Details", "Status", "Attachments"]

        for idx, label_text in enumerate(labels):
            value = row[idx]
            if label_text == "Attachments" and value:
                files = [f.strip() for f in value.split(",")]
                for f in files:
                    if f:
                        btn = QPushButton(f"📎 {os.path.basename(f)}")
                        btn.clicked.connect(lambda _, path=f: open_file(path))
                        layout.addRow("Attachment:", btn)
                continue
            elif value is None:
                value = ""
            display = QTextEdit(value) if label_text == "Details" else QLineEdit(str(value))
            display.setReadOnly(True)
            if label_text == "Details":
                display.setFixedHeight(80)
            layout.addRow(f"{label_text}:", display)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            background-color: #C0392B; color: white; padding: 10px; border-radius: 8px;
        """)
        close_button.clicked.connect(self.close)
        layout.addRow(close_button)

# ---------------- GUI Main Class ----------------

class HomeDent(QWidget):
    def __init__(self):
        super().__init__()

        # ---------------- Icon setup ----------------
        import platform
        from PyQt5.QtGui import QIcon
        icon_path = "stomadent_icon.ico" if platform.system() == "Windows" else "stomadent_icon.icns"
        self.setWindowIcon(QIcon(icon_path))

        # ---------------- Window setup ----------------
        self.setWindowTitle("StomaDent")
        self.setGeometry(100, 100, 800, 600)

        create_database()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.current_edit_id = None
        self.attached_files = []
        self.show_home_view()

    def clear_layout(self, layout=None):
        if layout is None:
            layout = self.layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    # ---------------- Home View ----------------
    def show_home_view(self):
        self.clear_layout()

        clinic_label = QLabel("STOMADENT")
        clinic_font = QFont("Pacifico", 36, QFont.Bold)
        clinic_label.setFont(clinic_font)
        clinic_label.setStyleSheet("color: #2E86C1;")
        clinic_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(clinic_label)

        btn_layout = QHBoxLayout()
        self.layout.addLayout(btn_layout)

        appointment_button = QPushButton("🗓 Appointment")
        appointment_button.setStyleSheet("""
            font-size: 18px; padding: 15px; background-color: #3498DB;
            color: white; border-radius: 10px;
        """)
        appointment_button.clicked.connect(self.show_appointment_view)
        btn_layout.addWidget(appointment_button)

        db_button = QPushButton("📋 Database")
        db_button.setStyleSheet("""
            font-size: 18px; padding: 15px; background-color: #1ABC9C;
            color: white; border-radius: 10px;
        """)
        db_button.clicked.connect(self.show_database_view)
        btn_layout.addWidget(db_button)

    # ---------------- Appointment View ----------------
    def show_appointment_view(self, edit_id=None):
        self.clear_layout()
        self.current_edit_id = edit_id
        self.attached_files = []

        form_group = QGroupBox("Appointment Details")
        form_group.setStyleSheet("""
            QGroupBox {
                font-size: 20px; font-weight: bold; color: #2E86C1;
                border: 2px solid #2E86C1; border-radius: 10px; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }
        """)
        form_layout = QFormLayout()
        form_group.setLayout(form_layout)
        self.layout.addWidget(form_group)

        self.name_entry = QLineEdit()
        form_layout.addRow("Name:", self.name_entry)

        self.surname_entry = QLineEdit()
        form_layout.addRow("Surname:", self.surname_entry)

        self.date_entry = QDateEdit()
        self.date_entry.setCalendarPopup(True)
        self.date_entry.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_entry)

        self.time_entry = QTimeEdit()
        self.time_entry.setTime(QTime.currentTime())
        form_layout.addRow("Time:", self.time_entry)

        self.phone_entry = QLineEdit()
        form_layout.addRow("Phone Number:", self.phone_entry)

        self.details_entry = QTextEdit()
        self.details_entry.setFixedHeight(100)
        form_layout.addRow("Details:", self.details_entry)

        self.status_entry = QComboBox()
        self.status_entry.addItems(["Scheduled", "Completed", "Cancelled"])
        form_layout.addRow("Status:", self.status_entry)

        self.attach_layout = QVBoxLayout()
        self.attach_button = QPushButton("📎 Attach Files / Photos")
        self.attach_button.setStyleSheet("""
            background-color: #F39C12; color: white; border-radius: 8px; padding: 5px;
        """)
        self.attach_button.clicked.connect(self.attach_files)
        self.attach_layout.addWidget(self.attach_button)
        form_layout.addRow("Attachments:", self.attach_layout)

        btn_layout = QHBoxLayout()
        save_button = QPushButton("💾 Save Appointment")
        save_button.setStyleSheet("""
            background-color: #27AE60; color: white; padding: 10px; font-size: 16px; border-radius: 8px;
        """)
        save_button.clicked.connect(self.save_appointment)
        btn_layout.addWidget(save_button)

        back_button = QPushButton("⬅ Back to Home")
        back_button.setStyleSheet("""
            background-color: #E67E22; color: white; padding: 10px; font-size: 16px; border-radius: 8px;
        """)
        back_button.clicked.connect(self.show_home_view)
        btn_layout.addWidget(back_button)

        self.layout.addLayout(btn_layout)

        if edit_id:
            row = fetch_appointment_by_id(edit_id)
            if row:
                self.name_entry.setText(row[1])
                self.surname_entry.setText(row[2])
                self.date_entry.setDate(QDate.fromString(row[3], "yyyy-MM-dd"))
                self.time_entry.setTime(QTime.fromString(row[4], "HH:mm"))
                self.phone_entry.setText(row[5])
                self.details_entry.setText(row[6])
                self.status_entry.setCurrentText(row[7])
                if row[8]:
                    self.attached_files = [f.strip() for f in row[8].split(",")]
                self.show_attached_files()

    # ---------------- Attachments ----------------
    def show_attached_files(self):
        while self.attach_layout.count() > 1:
            item = self.attach_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        for f in self.attached_files:
            h_layout = QHBoxLayout()
            lbl = QLabel(os.path.basename(f))
            btn = QPushButton("Open")
            btn.setMaximumWidth(60)
            btn.clicked.connect(lambda _, path=f: open_file(path))
            remove_btn = QPushButton("Remove")
            remove_btn.setMaximumWidth(60)
            remove_btn.clicked.connect(lambda _, path=f: self.remove_attachment(path))
            h_layout.addWidget(lbl)
            h_layout.addWidget(btn)
            h_layout.addWidget(remove_btn)
            self.attach_layout.addLayout(h_layout)

    def remove_attachment(self, path):
        if path in self.attached_files:
            self.attached_files.remove(path)
            self.show_attached_files()

    def attach_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files or Photos")
        if files:
            self.attached_files.extend(files)
            self.show_attached_files()

    # ---------------- Database View ----------------
    def show_database_view(self):
        self.clear_layout()
        all_appointments = fetch_all_appointments()
        self.appointments = sorted(
            all_appointments,
            key=lambda r: datetime.strptime(f"{r[3]} {r[4]}", "%Y-%m-%d %H:%M"),
            reverse=True
        )

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Patient Name", "Date", "Time", "Cause", "Attachment?"])
        self.table.setRowCount(len(self.appointments))

        now = datetime.now()
        focus_index = None
        min_delta = None

        for row_idx, row in enumerate(self.appointments):
            app_id, name, surname, date_str, time_str, details, status, attachments = row
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            self.table.setItem(row_idx, 0, QTableWidgetItem(f"{name} {surname}"))
            self.table.setItem(row_idx, 1, QTableWidgetItem(date_str))
            self.table.setItem(row_idx, 2, QTableWidgetItem(time_str))
            self.table.setItem(row_idx, 3, QTableWidgetItem(details))
            self.table.setItem(row_idx, 4, QTableWidgetItem("Yes" if attachments else "No"))

            # Grey out past/completed
            if dt < now or status == "Completed":
                for col in range(5):
                    self.table.item(row_idx, col).setForeground(QBrush(QColor("gray")))
            else:
                delta = (dt - now).total_seconds()
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    focus_index = row_idx

        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 14px; gridline-color: #BDC3C7; }
            QHeaderView::section { font-weight: bold; background-color: #3498DB; color: white; }
        """)
        self.table.resizeColumnsToContents()
        self.layout.addWidget(self.table)

        # Past/future focus colors
        pastel_green = QColor(198, 239, 206)
        if focus_index is not None:
            for col in range(5):
                self.table.item(focus_index, col).setBackground(QBrush(pastel_green))

        self.table.cellDoubleClicked.connect(self.open_patient_details)

        delete_button = QPushButton("🗑 Delete Appointment")
        delete_button.setStyleSheet("background-color: #C0392B; color: white; padding: 10px; border-radius: 8px;")
        delete_button.clicked.connect(self.delete_selected_appointment)
        self.layout.addWidget(delete_button)

        edit_button = QPushButton("✏ Edit Appointment")
        edit_button.setStyleSheet("background-color: #F1C40F; color: white; padding: 10px; border-radius: 8px;")
        edit_button.clicked.connect(self.edit_selected_appointment)
        self.layout.addWidget(edit_button)

        back_button = QPushButton("⬅ Back to Home")
        back_button.setStyleSheet("""
            background-color: #E67E22; color: white; padding: 10px; border-radius: 8px;
        """)
        back_button.clicked.connect(self.show_home_view)
        self.layout.addWidget(back_button)

    def open_patient_details(self, row, column):
        app_id = self.appointments[row][0]
        details_window = PatientDetailsWindow(app_id)
        details_window.exec_()

    def delete_selected_appointment(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an appointment to delete.")
            return
        row = selected_items[0].row()
        app_id = self.appointments[row][0]

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this appointment?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id=?", (app_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Deleted", "Appointment deleted successfully.")
            self.show_database_view()

    def edit_selected_appointment(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an appointment to edit.")
            return
        row = selected_items[0].row()
        app_id = self.appointments[row][0]
        self.show_appointment_view(edit_id=app_id)

    def save_appointment(self):
        data = {
            "Name": self.name_entry.text(),
            "Surname": self.surname_entry.text(),
            "Date": self.date_entry.date().toString("yyyy-MM-dd"),
            "Time": self.time_entry.time().toString("HH:mm"),
            "Phone": self.phone_entry.text(),
            "Details": self.details_entry.toPlainText(),
            "Status": self.status_entry.currentText(),
            "Attachments": self.attached_files
        }
        save_to_db(data, update_id=self.current_edit_id)
        self.current_edit_id = None
        self.attached_files = []
        self.show_home_view()
