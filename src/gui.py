import os
import sqlite3
import subprocess
import platform
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QTextEdit, QFileDialog,
    QDateEdit, QTimeEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QDialog, QMessageBox, QHBoxLayout, QStyle
)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QColor, QBrush, QFont, QIcon

DB_FILE = "stomadent.db"
APP_VERSION = "1.0.3"
CONTACT_EMAIL = "timotei.sandru2022@gmail.com"


# ---------------- Baza de date ----------------

def create_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            phone TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            time TEXT,
            details TEXT,
            status TEXT,
            attachments TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)
    conn.commit()
    conn.close()


def open_file(path):
    if not os.path.exists(path):
        QMessageBox.warning(None, "Fișier lipsă", f"Fișierul nu a fost găsit:\n{path}")
        return
    if platform.system() == "Darwin":
        subprocess.call(("open", path))
    elif platform.system() == "Windows":
        os.startfile(path)
    else:
        subprocess.call(("xdg-open", path))


# ---------------- Dialog Despre aplicație ----------------

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Despre aplicație")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        title = QLabel("StomaDent")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(
            f"Versiune: {APP_VERSION}\n\n"
            "Aplicație pentru gestionarea pacienților și programărilor\n"
            "în cabinet stomatologic.\n\n"
            "Contact:\n"
            f"{CONTACT_EMAIL}"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        close_btn = QPushButton("Închide")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


# ---------------- Dialog Adăugare Pacient ----------------

class AddPatientDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă pacient nou")
        self.setMinimumWidth(300)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.surname_edit = QLineEdit()
        self.phone_edit = QLineEdit()

        layout.addRow("Nume:", self.name_edit)
        layout.addRow("Prenume:", self.surname_edit)
        layout.addRow("Telefon:", self.phone_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Salvează")
        cancel_btn = QPushButton("Anulează")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return (
            self.name_edit.text().strip(),
            self.surname_edit.text().strip(),
            self.phone_edit.text().strip()
        )


# ---------------- Dialog Detalii Programare ----------------

class AppointmentDetailsDialog(QDialog):
    def __init__(self, appointment_row):
        super().__init__()
        self.setWindowTitle("Detalii programare")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        labels = ["Data", "Ora", "Detalii", "Status"]
        for i, text in enumerate(labels):
            layout.addWidget(QLabel(text))
            box = QTextEdit(appointment_row[i])
            box.setReadOnly(True)
            box.setFixedHeight(80 if text == "Detalii" else 30)
            layout.addWidget(box)

        attachments = appointment_row[4]
        layout.addWidget(QLabel("Atașamente:"))

        if attachments:
            for f in attachments.split(","):
                f = f.strip()
                if f:
                    btn = QPushButton(os.path.basename(f))
                    btn.clicked.connect(lambda _, p=f: open_file(p))
                    layout.addWidget(btn)
        else:
            layout.addWidget(QLabel("Nu există atașamente"))

        close_btn = QPushButton("Închide")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


# ---------------- Interfață principală ----------------

class HomeDent(QWidget):
    def __init__(self):
        super().__init__()

        icon_path = "stomadent_icon.ico" if platform.system() == "Windows" else "stomadent_icon.icns"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("StomaDent")
        self.setGeometry(100, 100, 900, 600)

        create_database()

        self.layout = QVBoxLayout(self)
        self.current_patient_id = None
        self.current_appointment_id = None
        self.attached_files = []

        self.show_home_view()

    def clear_layout(self, layout=None):
        if layout is None:
            layout = self.layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    # ---------------- Home ----------------

    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec_()

    def show_home_view(self):
        self.clear_layout()

        self.layout.addStretch(2)

        clinic_label = QLabel("STOMADENT")
        clinic_label.setFont(QFont("Arial", 36, QFont.Bold))
        clinic_label.setStyleSheet("color: #2E86C1;")
        clinic_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(clinic_label, alignment=Qt.AlignCenter)

        self.layout.addStretch(3)

        btn_container = QVBoxLayout()

        btn = QPushButton(" Pacienți")
        btn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        btn.setStyleSheet("padding:15px; font-size:18px; background:#3498DB; color:white; border-radius:10px;")
        btn.clicked.connect(self.show_patients_view)
        btn_container.addWidget(btn)

        add_btn = QPushButton(" Adaugă pacient nou")
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_btn.setStyleSheet("padding:15px; font-size:18px; background:#1ABC9C; color:white; border-radius:10px;")
        add_btn.clicked.connect(self.add_patient)
        btn_container.addWidget(add_btn)

        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addLayout(btn_container)
        btn_wrapper.addStretch()
        self.layout.addLayout(btn_wrapper)

        self.layout.addSpacing(10)

        info_btn = QPushButton(" Informații")
        info_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        info_btn.setStyleSheet("""
            background: transparent;
            color: #7F8C8D;
            font-size: 12px;
            border: none;
            text-decoration: underline;
        """)
        info_btn.clicked.connect(self.show_about_dialog)
        self.layout.addWidget(info_btn, alignment=Qt.AlignRight)

    # ---------------- Pacienți ----------------

    def show_patients_view(self):
        self.clear_layout()

        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Caută după nume, prenume, telefon sau dată (YYYY-MM-DD)...")
        self.filter_edit.textChanged.connect(self.apply_patient_filter)

        search_icon = QLabel()
        search_icon.setPixmap(self.style().standardIcon(QStyle.SP_FileDialogContentsView).pixmap(16, 16))
        filter_layout.addWidget(search_icon)
        filter_layout.addWidget(self.filter_edit)
        self.layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nume", "Prenume", "Telefon", "Următoarea programare"])
        self.layout.addWidget(self.table)

        self.load_patients("")

        self.table.cellDoubleClicked.connect(self.open_patient_file)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton(" Adaugă pacient")
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_btn.clicked.connect(self.add_patient)
        btn_layout.addWidget(add_btn)

        delete_btn = QPushButton(" Șterge pacient")
        delete_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_btn.setStyleSheet("background:#C0392B; color:white; padding:10px; border-radius:8px;")
        delete_btn.clicked.connect(self.delete_selected_patient)
        btn_layout.addWidget(delete_btn)
        self.layout.addLayout(btn_layout)

        back_btn = QPushButton(" Înapoi la meniu")
        back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_btn.setStyleSheet("background:#E67E22; color:white; padding:10px; border-radius:8px;")
        back_btn.clicked.connect(self.show_home_view)
        self.layout.addWidget(back_btn)

    def load_patients(self, filter_text=""):
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("""
            SELECT 
                p.id, p.name, p.surname, p.phone,
                MIN(a.date || ' ' || a.time) AS next_dt
            FROM patients p
            LEFT JOIN appointments a 
                ON p.id = a.patient_id AND (a.date || ' ' || a.time) >= ?
            WHERE 
                p.name LIKE ? OR 
                p.surname LIKE ? OR
                p.phone LIKE ? OR
                a.date LIKE ?
            GROUP BY p.id
            ORDER BY p.name COLLATE NOCASE, p.surname COLLATE NOCASE
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            f"%{filter_text}%",
            f"%{filter_text}%",
            f"%{filter_text}%",
            f"%{filter_text}%"
        )).fetchall()
        conn.close()

        self.patients = rows
        self.table.setRowCount(len(rows))

        for r, (pid, name, surname, phone, next_dt) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(name))
            self.table.setItem(r, 1, QTableWidgetItem(surname))
            self.table.setItem(r, 2, QTableWidgetItem(phone))
            self.table.setItem(r, 3, QTableWidgetItem(next_dt if next_dt else "—"))

    def apply_patient_filter(self, text):
        self.load_patients(text)

    def add_patient(self):
        dialog = AddPatientDialog()
        if dialog.exec_() == QDialog.Accepted:
            name, surname, phone = dialog.get_data()
            if not name or not surname:
                QMessageBox.warning(self, "Eroare", "Numele și prenumele sunt obligatorii.")
                return

            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO patients (name, surname, phone) VALUES (?, ?, ?)", (name, surname, phone))
            conn.commit()
            conn.close()

            self.show_patients_view()

    def delete_selected_patient(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ștergere", "Selectează un pacient.")
            return

        row = selected[0].row()
        patient_id = self.patients[row][0]

        reply = QMessageBox.question(
            self, "Confirmare",
            "Sigur vrei să ștergi pacientul și toate programările lui?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_FILE)
            conn.execute("DELETE FROM appointments WHERE patient_id=?", (patient_id,))
            conn.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            conn.commit()
            conn.close()
            self.show_patients_view()

    def confirm_back_from_appointment(self):
        has_data = (
            self.details_entry.toPlainText().strip() != "" or
            self.attached_files
        )

        if has_data:
            reply = QMessageBox.question(
                self,
                "Confirmare",
                "Dacă te întorci, modificările nesalvate se vor pierde.\n"
                "Sigur vrei să mergi înapoi?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self.show_patient_appointments_view()

    # ---------------- Dosar pacient ----------------

    def open_patient_file(self, row, col):
        self.current_patient_id = self.patients[row][0]
        self.show_patient_appointments_view()

    def show_patient_appointments_view(self):
        self.clear_layout()

        conn = sqlite3.connect(DB_FILE)
        patient = conn.execute("SELECT name, surname, phone FROM patients WHERE id=?", (self.current_patient_id,)).fetchone()
        appointments = conn.execute("""
            SELECT id, date, time, details, status, attachments
            FROM appointments
            WHERE patient_id=?
            ORDER BY date DESC, time DESC
        """, (self.current_patient_id,)).fetchall()
        conn.close()

        header = QLabel(f"{patient[0]} {patient[1]} – {patient[2]}")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        self.layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Ora", "Detalii", "Status", "Atașamente?"])
        self.layout.addWidget(self.table)

        self.table.cellDoubleClicked.connect(self.open_appointment_details)

        self.appointments = appointments
        self.table.setRowCount(len(appointments))

        for r, (aid, d, t, details, status, attachments) in enumerate(appointments):
            self.table.setItem(r, 0, QTableWidgetItem(d))
            self.table.setItem(r, 1, QTableWidgetItem(t))
            self.table.setItem(r, 2, QTableWidgetItem(details))
            self.table.setItem(r, 3, QTableWidgetItem(status))
            self.table.setItem(r, 4, QTableWidgetItem("Da" if attachments else "Nu"))

        btn_layout = QHBoxLayout()

        add_btn = QPushButton(" Adaugă programare")
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_btn.clicked.connect(self.show_add_appointment_view)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton(" Editează programare")
        edit_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        edit_btn.clicked.connect(self.edit_selected_appointment)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton(" Șterge programare")
        delete_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_btn.setStyleSheet("background:#C0392B; color:white; padding:10px; border-radius:8px;")
        delete_btn.clicked.connect(self.delete_selected_appointment)
        btn_layout.addWidget(delete_btn)

        self.layout.addLayout(btn_layout)

        back_btn = QPushButton(" Înapoi la pacienți")
        back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_btn.setStyleSheet("background:#E67E22; color:white; padding:10px; border-radius:8px;")
        back_btn.clicked.connect(self.show_patients_view)
        self.layout.addWidget(back_btn)

    def open_appointment_details(self, row, col):
        appointment = self.appointments[row]
        dialog = AppointmentDetailsDialog(appointment[1:])
        dialog.exec_()

    def edit_selected_appointment(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Editare", "Selectează o programare.")
            return

        row = selected[0].row()
        self.current_appointment_id = self.appointments[row][0]
        self.show_add_appointment_view(edit_id=self.current_appointment_id)

    def delete_selected_appointment(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ștergere", "Selectează o programare.")
            return

        row = selected[0].row()
        appointment_id = self.appointments[row][0]

        reply = QMessageBox.question(
            self, "Confirmare",
            "Sigur vrei să ștergi această programare?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_FILE)
            conn.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            conn.commit()
            conn.close()
            self.show_patient_appointments_view()

    # ---------------- Adăugare / Editare programare ----------------

    def show_add_appointment_view(self, edit_id=None):
        self.clear_layout()
        self.attached_files = []
        self.current_appointment_id = edit_id

        form = QFormLayout()

        self.date_entry = QDateEdit()
        self.date_entry.setCalendarPopup(True)
        self.date_entry.setDate(QDate.currentDate())
        form.addRow("Data:", self.date_entry)

        self.time_entry = QTimeEdit()
        self.time_entry.setTime(QTime.currentTime())
        form.addRow("Ora:", self.time_entry)

        self.details_entry = QTextEdit()
        form.addRow("Detalii:", self.details_entry)

        self.status_entry = QComboBox()
        self.status_entry.addItems(["Programată", "Finalizată", "Anulată"])
        form.addRow("Status:", self.status_entry)

        attach_btn = QPushButton(" Atașează fișiere")
        attach_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        attach_btn.clicked.connect(self.attach_files)
        form.addRow("Atașamente:", attach_btn)

        self.layout.addLayout(form)

        if edit_id:
            conn = sqlite3.connect(DB_FILE)
            row = conn.execute("""
                SELECT date, time, details, status, attachments
                FROM appointments WHERE id=?
            """, (edit_id,)).fetchone()
            conn.close()

            if row:
                self.date_entry.setDate(QDate.fromString(row[0], "yyyy-MM-dd"))
                self.time_entry.setTime(QTime.fromString(row[1], "HH:mm"))
                self.details_entry.setPlainText(row[2])
                self.status_entry.setCurrentText(row[3])
                if row[4]:
                    self.attached_files = row[4].split(",")

        save_btn = QPushButton(" Salvează")
        save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        save_btn.clicked.connect(self.save_appointment)
        self.layout.addWidget(save_btn)

        back_btn = QPushButton(" Înapoi")
        back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_btn.setStyleSheet("background:#E67E22; color:white; padding:10px; border-radius:8px;")
        back_btn.clicked.connect(self.confirm_back_from_appointment)
        self.layout.addWidget(back_btn)

    def attach_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selectează fișiere")
        if files:
            self.attached_files.extend(files)

    def save_appointment(self):
        conn = sqlite3.connect(DB_FILE)

        if self.current_appointment_id:
            conn.execute("""
                UPDATE appointments
                SET date=?, time=?, details=?, status=?, attachments=?
                WHERE id=?
            """, (
                self.date_entry.date().toString("yyyy-MM-dd"),
                self.time_entry.time().toString("HH:mm"),
                self.details_entry.toPlainText(),
                self.status_entry.currentText(),
                ",".join(self.attached_files),
                self.current_appointment_id
            ))
            self.current_appointment_id = None
        else:
            conn.execute("""
                INSERT INTO appointments (patient_id, date, time, details, status, attachments)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.current_patient_id,
                self.date_entry.date().toString("yyyy-MM-dd"),
                self.time_entry.time().toString("HH:mm"),
                self.details_entry.toPlainText(),
                self.status_entry.currentText(),
                ",".join(self.attached_files)
            ))

        conn.commit()
        conn.close()
        self.show_patient_appointments_view()