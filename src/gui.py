from lib import *

class gui_bs():
    def __init__(self):
        self.root = Tk()
        self.root.geometry("500x300")
        self.conn = sqlite3.connect('user.db')

        self.c = self.conn.cursor()
        ###
        self.new_client = StringVar()
        self.new_date = StringVar()
        self.new_number = StringVar()
        self.new_duration = StringVar()
        self.new_service = StringVar()
        
    def home_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.schedule_btn = Button(self.main_frame, text='Schedule', justify='center', width=7, height=2)
        self.schedule_btn.grid(row=0, column=0, padx=(145,0), pady=110)

        self.new_app = Button(self.main_frame, text='New \nAppoinment', command=self.new_appo)
        self.new_app.grid(row=0, column=1, padx=20, pady=100)

    def appoinment_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        ###
        self.new_user_label = Label(self.main_frame, text='User Name', justify='right')
        self.new_user_label.grid(row=0, column=0, sticky='e')

        self.new_user_entry = Entry(self.main_frame, textvariable=self.new_client)
        self.new_user_entry.grid(row=0, column=1)

        self.new_date_label = Label(self.main_frame, text='Date')
        self.new_date_label.grid(row=1, column=0, sticky='e')

        self.new_date_entry = Entry(self.main_frame, textvariable=self.new_date)
        self.new_date_entry.grid(row=1, column=1)

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

    def new_appo(self):
        self.destroy_widg(self.root)
        self.appoinment_ui()

    def back_root(self):
        self.destroy_widg(self.root)
        self.home_ui()

    def client_confirm(self):
        #self.loading_thread = threading.Thread(target=self.thread1, daemon=True)
        #self.loading_thread.start()
        #time.sleep(1)

        self.show_loading_screen()
        self.check_boxes()
        self.c.execute("INSERT INTO user_app (name, date, number) VALUES(?, ?, ?)", (self.new_client.get(), self.new_date.get(), self.new_number.get()))
        self.conn.commit()

        self.c.execute("SELECT * FROM user_app")
        self.conn.commit()
        self.conn.close()

        self.root.after(2000, lambda: self.destroy_widg(self.root))
        self.root.after(2000, lambda: self.home_ui())

    def thread1(self):
        self.show_loading_screen()
        ...

    def check_boxes(self):
        if self.new_client.get() != '' and self.new_client.get().isnumeric() != True:
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
