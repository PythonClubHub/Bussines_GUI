from lib import *

class gui_bs():
    def __init__(self):
        self.root = Tk()
        self.root.geometry("500x300")

    def build(self):
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=0, column=0)

        self.new_app = Button(self.main_frame, text='New Appoinment')
        self.new_app.grid(row=0, column=1)
    