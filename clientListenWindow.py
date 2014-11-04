#!/usr/bin/env python

__author__ = 'nilpferd'
__version__ = '1.0.0'

import clientListen
import Tkinter
from threading import Thread


class ControlThread(Thread):
    def __init__(self):
        self.client = None
        self.thread = None
        Thread.__init__(self)

    def run(self):
        self.client = clientListen.ClientListener()
        self.client.connect()
        self.thread = clientListen.HandleCorrectStartTimeThread(self.client)
        self.thread.start()
        self.client.message_loop()

    def stop(self):
        self.client.is_running = False
        self.client = None
        self.thread = None


class App:
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.title("sound-sync")
        self.root.geometry("400x70+0+0")

        frame = Tkinter.Frame(self.root)
        frame.pack()

        label = Tkinter.Label(frame, text="sound-sync listener client")
        label.grid(row=0, column=0, columnspan=2)

        self.button_start = Tkinter.Button(frame, text="start listening", command=self.start)
        self.button_start.grid(row=1, column=0)

        self.button_stop = Tkinter.Button(frame, text="stop listening", command=self.stop, state=Tkinter.DISABLED)
        self.button_stop.grid(row=1, column=1)

        self.status_label = Tkinter.Label(frame, text="Not started yet.")
        self.status_label.grid(row=2, column=0, columnspan=2)

        self.thread = ControlThread()

    def start(self):
        self.thread.start()

        self.status_label.config(text="Catching data. Please wait.")
        self.button_start.config(state=Tkinter.DISABLED)
        self.button_stop.config(state=Tkinter.DISABLED)
        self.root.update()

        while self.thread.client is None:
            pass

        while self.thread.client.is_running and not self.thread.client.is_audio_playing:
            pass

        if self.thread.client.is_running:

            self.status_label.config(text="Done catching data. Playing %d now." %
                                          self.thread.client.static_sound_buffer_list.current_buffer_index)

            self.button_start.config(state=Tkinter.DISABLED)
            self.button_stop.config(state=Tkinter.NORMAL)

        else:
            self.status_label.config(text="There is no sender playing data. Please exit the program.")

            self.button_start.config(state=Tkinter.DISABLED)
            self.button_stop.config(state=Tkinter.NORMAL)

    def stop(self):
        self.thread.stop()

        self.status_label.config(text="Closing stream. Please wait.")
        self.button_start.config(state=Tkinter.DISABLED)
        self.button_stop.config(state=Tkinter.DISABLED)

        self.root.update()

        while self.thread.client is not None:
            pass

        exit()

    def mainloop(self):
        self.root.mainloop()
        if not self.thread.client is None:
            self.thread.client.is_running = False


app = App()
app.mainloop()