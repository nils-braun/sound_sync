#!/usr/bin/env python

__author__ = 'nils'
__version__ = '1.0.0'

import clientListen
import Tkinter
from threading import Thread


class ControlThread(Thread):
    def __init__(self):
        self.client = clientListen.ClientListener()
        self.thread = 0
        Thread.__init__(self)

    def run(self):
        self.client.connect()
        self.thread = clientListen.PlayThread(self.client)
        self.thread.start()
        self.client.message_loop()

    def stop(self):
        self.client.is_running = False
        self.thread.stop()


class App:
    def __init__(self):
        self.thread = 0

        self.root = Tkinter.Tk()
        self.root.title("sound-sync")
        self.root.geometry("400x60+0+0")

        frame = Tkinter.Frame(self.root)
        frame.pack()

        label = Tkinter.Label(frame, text="sound-sync listener client")
        label.pack()

        self.button_start = Tkinter.Button(frame, text="start listening", command=self.start)
        self.button_start.pack(side=Tkinter.LEFT)

        self.button_stop = Tkinter.Button(frame, text="stop listening", command=self.stop, state=Tkinter.DISABLED)
        self.button_stop.pack(side=Tkinter.LEFT)

    def start(self):
        self.thread = ControlThread()
        self.thread.start()
        self.button_start.config(state=Tkinter.DISABLED)
        self.button_stop.config(state=Tkinter.NORMAL)

    def stop(self):
        self.thread.stop()
        self.button_start.config(state=Tkinter.NORMAL)
        self.button_stop.config(state=Tkinter.DISABLED)

    def mainloop(self):
        self.root.mainloop()
        if self.thread != 0:
            self.thread.stop()


app = App()
app.mainloop()