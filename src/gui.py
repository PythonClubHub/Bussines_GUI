import sqlite3
import tkinter as tk
from tkinter import Entry, StringVar, Button, Label, Frame, Toplevel
from PIL import Image, ImageTk
from tkcalendar import *
from tkinter import ttk
import time
import pandas as pd

class GuiBs:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("500x300")
        self.conn = sqlite3.connect('user.db')
        self.c = self.conn.cursor()

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS user_app (
                name TEXT,
                date TEXT,
                number TEXT
            )
        ''')

        self.new_client = StringVar()
        self.new_date = StringVar()
        self.new_number = StringVar()
        self.new_duration = StringVar()
        self.new_service = StringVar()

        image_path = "/Users/timoothee/Desktop/Repos/Bussines_GUI/images/calendar.png"
        image = Image.open(image_path).resize((25, 25), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image)

    def close_db(self):
        self.conn.close()

    def home_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.schedule_btn = Button(self.main_frame, text='Schedule', justify='center', width=7, height=2, command=self.schedule)
        self.schedule_btn.grid(row=0, column=0, padx=(145,0), pady=110)

        self.new_app = Button(self.main_frame, text='New \nAppoinment', command=self.new_appo)
        self.new_app.grid(row=0, column=1, padx=20, pady=100)

    def appoinment_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.new_user_label = Label(self.main_frame, text='User Name', justify='right')
        self.new_user_label.grid(row=0, column=0, sticky='e')

        self.new_user_entry = Entry(self.main_frame, textvariable=self.new_client)
        self.new_user_entry.grid(row=0, column=1)

        self.new_date_label = Label(self.main_frame, text='Date')
        self.new_date_label.grid(row=1, column=0, sticky='e')

        self.new_date_entry = Entry(self.main_frame, textvariable=self.new_date)
        self.new_date_entry.grid(row=1, column=1)

        self.calendar_button = tk.Button(self.main_frame, image=self.photo, width=25, height=25, command=self.toplevel_wd)
        self.calendar_button.grid(row=1, column=2)

        self.new_number_label = Label(self.main_frame, text='Phone Number', justify='right')
        self.new_number_label.grid(row=2, column=0, sticky='e')

        self.new_number_entry = Entry(self.main_frame, textvariable=self.new_number)
        self.new_number_entry.grid(row=2, column=1)

        self.new_duration_label = Label(self.main_frame, text='Duration (h)', justify='right')
        self.new_duration_label.grid(row=3, column=0, sticky='e')

        self.new_duration_entry = Entry(self.main_frame, textvariable=self.new_duration)
        self.new_duration_entry.grid(row=3, column=1)

        self.new_sevice_label = Label(self.main_frame, text='Service', justify='right')
        self.new_sevice_label.grid(row=4, column=0, sticky='e')

        self.new_service_entry = Entry(self.main_frame, textvariable=self.new_service)
        self.new_service_entry.grid(row=4, column=1)

        self.back_btn = Button(self.main_frame, text='Back', command=self.back_root)
        self.back_btn.grid(row=5, column=0, pady=70)

        self.confirmation_btn = Button(self.main_frame, text='Confirm', command=self.client_confirm)
        self.confirmation_btn.grid(row=5, column=1, pady=70, sticky='w')

    def toplevel_wd(self):
        button_x = self.calendar_button.winfo_rootx()
        button_y = self.calendar_button.winfo_rooty()

        top_level = tk.Toplevel(self.root)
        top_level.geometry("230x160")

        new_x = button_x + 50
        new_y = button_y + 50  

        top_level.geometry(f"+{new_x}+{new_y}")
        cal = Calendar(top_level, selectmode="day", year=2023, month = 11, day=12)
        cal.grid()
        # to grab date.. cal.get_date()

    def schedule_form(self):
        table = ttk.Treeview(self.root, columns=('name','date','number'), show='headings')
        table.heading('name', text='Name')
        table.heading('date', text='Date')
        table.heading('number', text='Telephone Number')
        table.grid()

        with sqlite3.connect("user.db") as db:
            print('Inside')
            data_pd = pd.read_sql('SELECT * FROM user_app', db)
            #data_pd = list(data_pd)
            data_listed = data_pd.values.tolist()
        for i in range(len(data_listed)):
            table.insert(parent='', index=i, values=data_listed[i])

    def schedule(self):
        self.destroy_widg(self.root)
        self.schedule_form()

    def new_appo(self):
        self.destroy_widg(self.root)
        self.appoinment_ui()

    def back_root(self):
        self.destroy_widg(self.root)
        self.home_ui()

    def client_confirm(self):
        client_name = self.new_client.get()
        data = self.new_date.get()
        number = self.new_number.get()
        
        self.show_loading_screen()
        self.check_boxes()

        try:
            self.c.execute("INSERT INTO user_app (name, date, number) VALUES(?, ?, ?)", (client_name, data, number,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

        self.new_date.set("")
        self.new_client.set("")
        self.new_number.set("")

        self.c.execute("SELECT * FROM user_app")
        self.conn.commit()
        time.sleep(2)

        self.root.after(2000, lambda: self.destroy_widg(self.root))
        self.root.after(2000, lambda: self.home_ui())

    def check_boxes(self):
        if self.new_client.get():
            print("It's ok")
        else:
            print('Error')

    def destroy_widg(self, window):
        _list = window.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())
        for item in _list:
            item.destroy()

    def show_loading_screen(self):
        self.grey_out_window()
        loading_screen = Toplevel(self.root)
        loading_screen.geometry("200x100")
        loading_screen.transient(self.root)
        loading_screen.grab_set()
        loading_screen.title("Loading...")

        loading_label = Label(loading_screen, text="Loading, please wait...")
        loading_label.pack(pady=20)

        self.root.after(2000, lambda: loading_screen.destroy())

    def grey_out_window(self):
        overlay = Toplevel(self.root)
        overlay.attributes('-alpha', 0.5)
        overlay.geometry(self.root.geometry())
        overlay.transient(self.root)
        overlay.grab_set()
        self.root.after(2000, lambda: overlay.destroy())