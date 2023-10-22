from lib import *

class gui_bs():
    def __init__(self):
        self.root = Tk()
        self.root.geometry("500x300")

        ###
        self.new_client = StringVar()
        self.new_date = StringVar()

    def home_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.new_app = Button(self.main_frame, text='New Appoinment', command=self.new_appo)
        self.new_app.grid(row=0, column=1)

    def appoinment_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        ###
        self.new_user_label = Label(self.main_frame, text='New Entry')
        self.new_user_label.grid(row=0, column=0)

        self.new_user_entry = Entry(self.main_frame, textvariable=self.new_client)
        self.new_user_entry.grid(row=0, column=1)

        self.new_date_label = Label(self.main_frame, text='Date')
        self.new_date_label.grid(row=1, column=0)

        self.new_date_entry = Entry(self.main_frame, textvariable=self.new_date)
        self.new_date_entry.grid(row=1, column=1)

        self.back_btn = Button(self.main_frame, text='Back', command=self.back_root)
        self.back_btn.grid(row=2, column=0)

    def new_appo(self):
        self.destroy_widg(self.root)
        self.appoinment_ui()

    def back_root(self):
        self.destroy_widg(self.root)
        self.home_ui()

    def destroy_widg(self, window):
        _list = window.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())
        for item in _list:
            item.destroy()
