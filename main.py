#!/usr/bin/env python

import os
import Tkinter


class SoundSync():

    def __init__(self):

        self.send_module_id = 0
        self.recv_module_id = 0
        self.null_module_id = 0

        self.get_null_module_id()
        self.get_send_module_id()
        self.get_recv_module_id()

    def main(self, action):
        if action == "stop_sender":
            self.stop_null_module()
            self.null_module_id = -1
            self.stop_send_module()
            self.send_module_id = -1

        elif action == "stop_receiver":
            self.stop_recv_module()
            self.recv_module_id = -1

        elif action == "start_sender":
            if self.send_module_id != -1:
                print "Sender already running..."
            else:
                self.null_module_id = self.start_null_module()
                self.send_module_id = self.start_send_module()

        elif action == "start_receiver":
            if self.recv_module_id != -1:
                print "Receiver already running..."
            else:
                self.recv_module_id = self.start_recv_module()

        else:
            print "Can't process " + action

    def get_recv_module_id(self):
        """
            Get receiver module id from pactl
        """
        self.recv_module_id = os.popen(
            'pactl list modules short | grep "module-rtp-recv" | awk \'{print $1}\' ').read()
        if self.recv_module_id == "":
            self.recv_module_id = -1
        else:
            self.recv_module_id = int(self.recv_module_id)

    def get_null_module_id(self):
        """
            Get null sink module id from pactl
        """
        self.null_module_id = os.popen(
            'pactl list modules short | grep "module-null-sink.*sink_name=rtp" | awk \'{print $1}\' ').read()
        if self.null_module_id == "":
            self.null_module_id = -1
        else:
            self.null_module_id = int(self.null_module_id)

    def get_send_module_id(self):
        """
            Get sender module id from pactl
        """
        self.send_module_id = os.popen(
            'pactl list modules short | grep "module-rtp-send.*source=rtp\.monitor" | awk \'{print $1}\' ').read()
        if self.send_module_id == "":
            self.send_module_id = -1
        else:
            self.send_module_id = int(self.send_module_id)

    def stop_send_module(self):
        """
            Stop all sender modules
        """
        print "Quitting sender"
        os.popen3('pactl unload-module ' + str(self.send_module_id))
        print "Sender quited"
        self.send_module_id = -1

    def stop_recv_module(self):
        """
            Stop all receiver modules
        """
        print "Quitting receiver"
        os.popen3('pactl unload-module ' + str(self.recv_module_id))
        print "Receiver quited"
        self.recv_module_id = -1

    def stop_null_module(self):
        """
            Stop all null sink modules
        """
        print "Quitting null module"
        os.popen3('pactl unload-module ' + str(self.null_module_id))
        print "Null module quited"
        self.null_module_id = -1

    def start_send_module(self):
        """
            Start the sender module
        """
        print "Starting sender"
        self.send_module_id = os.popen(
            'pactl load-module module-rtp-send source=rtp.monitor loop=true destination=127.0.0.1 port=46998').read()
        print "Sender started"

    def start_recv_module(self):
        """
            Start the receiver module
        """
        print "Starting receiver"
        self.recv_module_id = os.popen('pactl load-module module-rtp-recv').read()
        print "Receiver started"

    def start_null_module(self):
        """
            Start the nll sink module
        """
        print "Starting null module"
        self.null_module_id = os.popen('pactl load-module module-null-sink sink_name=rtp format=s16be ' +
                                  'channels=2 rate=44100 ' +
                                  'sink_properties="device.description=\'RTP\'"').read()
        print "Null module started"


if __name__ == "__main__":

    soundSync = SoundSync()
    top = Tkinter.Tk()

    senderButton = Tkinter.Button(top, text="")
    receiverButton = Tkinter.Button(top, text="")

    def set_labels():
        if soundSync.send_module_id == -1:
            senderButton["text"] = "Sender is not running."
        else:
            senderButton["text"] = "Sender is running."
        if soundSync.recv_module_id == -1:
            receiverButton["text"] = "Receiver is not running."
        else:
            receiverButton["text"] = "Receiver is running."

    def toggle_sender():
        if soundSync.send_module_id == -1:
            soundSync.start_null_module()
            soundSync.start_send_module()
        else:
            soundSync.stop_null_module()
            soundSync.stop_send_module()

        set_labels()

    def toggle_receiver():
        if soundSync.recv_module_id == -1:
            soundSync.start_recv_module()
        else:
            soundSync.stop_recv_module()

        set_labels()

    senderButton["command"] = toggle_sender
    receiverButton["command"] = toggle_receiver
    set_labels()

    senderButton.pack()
    receiverButton.pack()
    top.mainloop()

