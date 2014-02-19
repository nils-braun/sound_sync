#!/usr/bin/env python3

import subprocess
import tkinter
import os


class SoundSync():
    def __init__(self):

        self.send_module_id = 0
        self.null_module_id = 0
        self.recv_pid = 0
        self.format_pid = 0

        self.multicast_address = "225.0.0.1"
        self.multicast_port = "12345"
        self.local_port = "46998"

        self.format_string = 'cvlc rtp://@127.0.0.1:' + self.local_port + ' ' \
                             '":sout=#transcode{acodec=mp3,ab=256,channels=2}:' \
                             'duplicate{dst=rtp{dst=' + self.multicast_address + \
                             ',mux=ts,port=' + self.multicast_port + '}}"'

        self.recv_string = 'cvlc rtp://@' + self.multicast_address + ':' + self.multicast_port

        self.get_null_module_id()
        self.get_send_module_id()
        self.get_recv_pid()
        self.get_format_pid()

    def get_null_module_id(self):
        """
            Get null sink module id from pactl
        """
        self.null_module_id = subprocess.Popen('pactl list modules short | '
                                               'grep "module-null-sink.*sink_name=rtp" | '
                                               'awk \'{print $1}\' ',
                                               stdout=subprocess.PIPE, shell=True).stdout.read().decode("utf-8")
        if self.null_module_id == "":
            self.null_module_id = -1
        else:
            self.null_module_id = int(self.null_module_id)

    def get_send_module_id(self):
        """
            Get sender module id from pactl
        """
        self.send_module_id = subprocess.Popen('pactl list modules short | '
                                               'grep "module-rtp-send.*source=rtp\.monitor" | '
                                               'awk \'{print $1}\' ', stdout=subprocess.PIPE,
                                               shell=True).stdout.read().decode("utf-8")
        if self.send_module_id == "":
            self.send_module_id = -1
        else:
            self.send_module_id = int(self.send_module_id)

    def get_recv_pid(self):
        """
            Get pid of receiver cvlc
        """
        temp = subprocess.Popen('ps a | grep "vlc.*' + self.multicast_address + ':' + self.multicast_port + '"',
                                stdout=subprocess.PIPE, shell=True).stdout.readlines()

        temp = [y[0] for y in [x.decode("utf-8").split() for x in temp] if "grep" not in y]

        if len(temp) == 0:
            self.recv_pid = -1
        else:
            self.recv_pid = int(temp[0])

    def get_format_pid(self):
        """
            Get pid of format cvlc
        """
        temp = subprocess.Popen('ps a | grep "vlc.*' + self.local_port + '.*sout.*dst=' +
                                self.multicast_address + '.*port=' + self.multicast_port + '"',
                                stdout=subprocess.PIPE, shell=True).stdout.readlines()

        temp = [y[0] for y in [x.decode("utf-8").split() for x in temp] if "grep" not in y]

        if len(temp) == 0:
            self.format_pid = -1
        else:
            self.format_pid = int(temp[0])

    def stop_send_module(self):
        """
            Stop all sender modules
        """
        print("Quitting sender")
        subprocess.Popen('pactl unload-module ' + str(self.send_module_id), shell=True)
        print("Sender quited")
        self.send_module_id = -1

    def stop_format_p(self):
        """
            Stop the format process
        """
        if self.format_pid != -1:
            print("Quitting format")
            subprocess.Popen('kill -9 ' + str(self.format_pid), shell=True)
            print("Format quited")
            self.format_pid = -1

    def stop_recv_p(self):
        """
            Stop the receiver process
        """
        if self.recv_pid != -1:
            print("Quitting receiver")
            subprocess.Popen('kill -9 ' + str(self.recv_pid), shell=True)
            print("Receiver quited")
            self.recv_pid = -1

    def stop_null_module(self):
        """
            Stop all null sink modules
        """
        print("Quitting null module")
        subprocess.Popen('pactl unload-module ' + str(self.null_module_id), shell=True)
        print("Null module quited")
        self.null_module_id = -1

    def start_send_module(self):
        """
            Start the sender module
        """
        print("Starting sender")
        self.send_module_id = subprocess.Popen('pactl load-module '
                                               'module-rtp-send source=rtp.monitor '
                                               'loop=true destination=127.0.0.1 port=' +
                                               self.local_port, stdout=subprocess.PIPE,
                                               shell=True).stdout.read().decode("utf-8")
        print("Sender started")

    def start_null_module(self):
        """
            Start the nll sink module
        """
        print("Starting null module")
        self.null_module_id = subprocess.Popen('pactl load-module module-null-sink '
                                               'sink_name=rtp format=s16be channels=2 '
                                               'rate=44100 sink_properties="device.description=\'RTP\'"',
                                               stdout=subprocess.PIPE, shell=True).stdout.read().decode("utf-8")
        print("Null module started")

    def start_recv_p(self):
        subprocess.Popen(self.recv_string + ' &',
                         shell=True, stdout=subprocess.DEVNULL, preexec_fn=os.setpgrp, stderr=subprocess.DEVNULL)

        self.get_recv_pid()

    def start_format_p(self):
        subprocess.Popen(self.format_string + ' &',
                         shell=True, stdout=subprocess.DEVNULL, preexec_fn=os.setpgrp, stderr=subprocess.DEVNULL)

        self.get_format_pid()

if __name__ == "__main__":

    soundSync = SoundSync()
    top = tkinter.Tk()

    senderButton = tkinter.Button(top, text="")
    receiverButton = tkinter.Button(top, text="")

    def set_labels():
        if soundSync.send_module_id == -1:
            senderButton["text"] = "Sender is not running."
        else:
            senderButton["text"] = "Sender is running."
        if soundSync.recv_pid == -1:
            receiverButton["text"] = "Receiver is not running."
        else:
            receiverButton["text"] = "Receiver is running."

    def toggle_sender():
        if soundSync.send_module_id == -1:
            soundSync.start_null_module()
            soundSync.start_send_module()
            soundSync.start_format_p()
        else:
            soundSync.stop_null_module()
            soundSync.stop_send_module()
            soundSync.stop_format_p()

        set_labels()

    def toggle_receiver():
        if soundSync.recv_pid == -1:
            soundSync.start_recv_p()
        else:
            soundSync.stop_recv_p()

        set_labels()

    senderButton["command"] = toggle_sender
    receiverButton["command"] = toggle_receiver
    set_labels()

    senderButton.pack()
    receiverButton.pack()
    top.mainloop()

