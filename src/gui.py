import sqlite3
import tkinter as tk
from tkinter import Entry, IntVar, Listbox, OptionMenu, StringVar, Button, Label, Frame, Toplevel
from PIL import Image, ImageTk
from tkcalendar import *
from tkinter import ttk
import time
import pandas as pd
import os

class GuiBs:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("500x300")
        self.conn = sqlite3.connect('user.db')
        self.c = self.conn.cursor()
        db_ex = os.path.isfile('./user.db')

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
        self.choice_var = StringVar()
        self.choice_list = ("apple", "orange")
        self.choice_var.set("Select")
        self.user_quant_var = IntVar()
        self.user_quant_var.set("0")
        self.client_no = IntVar()
        self.client_no.set(0)
        if db_ex:
            try:
                last_row = self.c.execute('select * from user_app').fetchall()[-1]
                self.client_no.set(int(list(last_row)[0])+1)
            except:
                ...
        #print("typo", type(last_row), print(last_row))
        self.ct = 0
        self.client_ct = 0

    def close_db(self):
        self.conn.close()

    def home_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.schedule_btn = Button(self.main_frame, text='Schedule', justify='center', width=7, height=2, command=self.schedule)
        self.schedule_btn.grid(row=0, column=0, padx=(145,0), pady=110)

        self.new_app = Button(self.main_frame, text='New \nOrder', command=self.new_appo)
        self.new_app.grid(row=0, column=1, padx=20, pady=100)

        self.conf_item = Button(self.main_frame, text='conf', command=self.conf_ui)
        self.conf_item.grid(row=0, column=2)

    def appoinment_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)
        self.user_quant_var.set("0")
        self.choice_var.set("Select")
        self.ct = 0

        self.new_user_label = Label(self.main_frame, text='User No.', justify='right')
        self.new_user_label.grid(row=0, column=0, sticky='e')

        self.new_user_entry = Label(self.main_frame, text=self.client_no.get())
        self.new_user_entry.grid(row=0, column=1)

        self.user_choice_label = Label(self.main_frame, text='Type', justify='right')
        self.user_choice_label.grid(row=1, column=0, sticky='e')

        self.user_choice_list = OptionMenu(self.main_frame, self.choice_var, *self.choice_list)
        self.user_choice_list.config(width=5)
        self.user_choice_list.grid(row=1, column=1)

        self.user_quant_label = Label(self.main_frame, text="Quantity")
        self.user_quant_label.grid(row=2, column=0, sticky='e')
        
        self.user_quant = Label(self.main_frame, text = self.user_quant_var.get())
        self.user_quant.grid(row=2, column=1)
        
        self.add_btn = Button(self.main_frame, text='+', command=self.add)
        self.add_btn.grid(row=2, column=2, sticky='w')
        self.sub_btn = Button(self.main_frame, text='-', command=self.substract)
        self.sub_btn.grid(row=2, column=3, sticky='w')
        

        self.back_btn = Button(self.main_frame, text='Back', command=self.back_root)
        self.back_btn.grid(row=5, column=0, pady=70)

        self.confirmation_btn = Button(self.main_frame, text='Confirm', command=self.client_confirm)
        self.confirmation_btn.grid(row=5, column=1, pady=70, sticky='w')

    def add(self):
        self.ct = self.ct + 1
        self.user_quant_var.set(self.ct)
        self.user_quant.configure(text=self.user_quant_var.get())

    def substract(self):
        if self.ct != 0:
            self.ct = self.ct - 1
            self.user_quant_var.set(self.ct)
            self.user_quant.configure(text=self.user_quant_var.get())
        else:
            ...

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
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.sec_frame = Frame(self.root)
        self.sec_frame.grid(row=1, column=0, sticky='w')
        self.sh_table = ttk.Treeview(self.main_frame, columns=('No.','choice','quant'), show='headings')
        self.sh_table.bind('<Delete>', self.delete_item)
        self.sh_table.heading('No.', text='No.')
        self.sh_table.heading('choice', text='choice')
        self.sh_table.heading('quant', text='quant')
        self.sh_table.grid(row=0,column=0)

        with sqlite3.connect("user.db") as db:
            print('Inside')
            data_pd = pd.read_sql('SELECT * FROM user_app', db)
            #data_pd = list(data_pd)
            data_listed = data_pd.values.tolist()
            print("Here", data_listed)
        for i in range(len(data_listed)):
            self.sh_table.insert(parent='', index=i, values=data_listed[i])

        self.back_btn = Button(self.sec_frame, text='Back', command=self.back_root)
        self.back_btn.grid(row=1, column=0, pady=20, sticky='w')

        self.reset_table_btn = Button(self.sec_frame, text='Reset', command=self.reset)
        self.reset_table_btn.grid(row=1, column=1, pady=20, sticky='w')

    def reset(self):
        print("Before")
        delete_query = 'DELETE FROM user_app;'
        self.c.execute(delete_query)
        self.conn.commit()
        print("After")
        self.show_loading_screen()
        self.root.after(2000, lambda: self.destroy_widg(self.root))
        self.root.after(2000, lambda: self.home_ui())
        self.client_no.set(0)


    def delete_item(self):
        for i in self.sh_table.selection():
            self.sh_table.delete()

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
        client_number = self.client_no.get()
        choice = self.choice_var.get()
        quant = self.user_quant_var.get()
        
        self.show_loading_screen()
        self.check_boxes()

        try:
            self.c.execute("INSERT INTO user_app (name, date, number) VALUES(?, ?, ?)", (client_number, choice, quant,))
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

        #self.choice_var.set("")
        #self.user_quant_var.set("")
        self.client_ct = self.client_ct + 1
        self.client_no.set(self.client_ct)

        self.c.execute("SELECT * FROM user_app")
        self.conn.commit()

        #self.root.after(2000, lambda: self.destroy_widg(self.root))
        self.root.after(1000, lambda: self.new_appo())

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