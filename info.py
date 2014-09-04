# #-*- coding: UTF-8 -*-
#
# import sys
# import argparse
# from compass_inviter import CompassInviter
#
# def createParser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-i', '--ignore', default='')
#     return parser
#
# if __name__ == '__main__':
#     parser = createParser()
#     namespace = parser.parse_args(sys.argv[1:])
#     ignore_list = namespace.ignore.replace(' ', '').split(',')
#
#     ci = CompassInviter('angelica_sweet@lenta.ru', '22223333', ignore_list=ignore_list, auto_run=True)

from tkinter import *
from compass_inviter import CompassInviter
import os
import threading


class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.wm_title('RomanceCompass')
        self.master.geometry('320x210')
        self.master.resizable(False, False)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # login label and login box
        self.label_login = Label(self, text='Логин: ')
        self.label_login.pack()

        self.edit_login = Entry(self, width=30)
        self.edit_login.insert(0, 'angelica_sweet@lenta.ru')
        self.edit_login.pack()

        # pass label and pass box
        self.label_pass = Label(self, text='Пароль: ')
        self.label_pass.pack()

        self.edit_pass = Entry(self, width=30)
        self.edit_pass.insert(0, '22223333')
        self.edit_pass.pack()

        # start button
        self.btn = Button(self, text="Начать рассылку", width=30, height=2, bg="white", fg="black", command=self.start)
        self.btn.pack()

        # edit messages button
        self.btn2 = Button(self, text="Изменить сообщения", width=30, height=2, bg="white", fg="black", command=self.edit_messages)
        self.btn2.pack()

        # ignore list label and text box
        self.label = Label(self, text='ID игнорируемых, через запятую')
        self.label.pack()
        self.edit = Entry(self, width=50)
        self.edit.pack()

    def start(self):
        os.system('cls')
        self.master.wm_state('iconic')
        ignore_list = self.edit.get().replace(' ', '').split(',')
        ci = CompassInviter(self.edit_login.get(), self.edit_pass.get(), ignore_list=ignore_list, auto_run=True)
        # ci.authorize()
        # th = threading.Thread(name='th1', target=ci.run, args=())
        # th.start()

    def edit_messages(self):
        th2 = threading.Thread(name='th2', target=os.system, args=('txt\mess.txt',))
        th2.start()
        #os.system('txt\mess.txt')

root = Tk()
app = App(master=root)
app.mainloop()

