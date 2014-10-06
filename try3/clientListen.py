#!/usr/bin/env python
"""
This module implements the listener client.
"""

__author__ = "nilpferd1991"
__version__ = "1.0.0"

import socket
import alsaaudio
import time
from threading import Thread
import select
import sys
from clientBase import ClientBase


class PlayThread(Thread):
    """
    A class to handle the thread to play the audio from the buffers of the client.
    When running waits for the correct time (time + delta) % waiting_time == 0 and plays one buffer.
    Skips one buffer if it is "too late".
    """

    def _call(self):
        # The function to call when we play a buffer.
        if len(self.client.buffers) > 0:
            data = self.client.buffers.pop(0)
            self.client.device.write(bytes(data))
        else:
            print("no")
            return

    def _next(self):
        # The function to call when we skip a buffer
        if len(self.client.buffers) > 0:
            self.client.buffers.pop(0)

    def __init__(self, client):
        self.stopped = False
        self.delta = 0.1
        self.counter = 0
        self.client = client
	# Fill in some buffers before running
        self.started = False

        Thread.__init__(self)

    def run(self):
        """
        This function is called everytime the thread is executed. It waits for the correct time and plays an
        audio snippet or skipps one.
        """


	"""
	Folgende Probleme:
	1) Falls direkt das Paket gespielt wird, welches auch gerade ankommt, gibt es Probleme, weil das Paket vielleicht noch nicht da ist und call() läuft ins Leere.
	2) Falls sich immer nur ein Paket im Sound-Puffer befindet, kommt es zu "Klicken", da dann das nächste Paket vielleicht zu spät kommt (das Paket wird ja gerade erst abgerufen!). Dafür ist es dann synchron!

	Mögliche Lösungen:
	1) Zuerst mindestens 5 Pakete holen (schon implementiert)
	2a) Pakete immer direkt spielen, wenn sie kommen und nur den Start des ersten Pakets überprüfen. Nachteil: Synchronität nicht für die ganze Periode geklärt!
	2b) Neues Paket erst dann reinschrieben, wenn es dran kommen soll. Nachteil: ist zwar perfekt synchron, kann aber klicken. Warum klickts eigentlich? Weil das neue Paket noch nicht da ist oder weil noch keins in den Sound-Puffer geschoben wurde?
	2c) Neues Packet kurz vorher reinschieben. Muss getestet werden. Ne Quatsch, oder?
	2d) Immer mehrere Packete gleichzeitig reinschrieben. Klicken wäre nicht so oft. Muss getestet werden.
	2e) Synchronität laufend überprüfen (wie??) und wenn nötig Pausen einfügen
	"""

        while not self.stopped:

	    # Start only of the buffer is filled. (1)
            if len(self.client.buffers) > 5:
                self.started = True

	    # Every waiting_time do:
            time_stamp = int(time.time() * 1000 + self.delta)
            if time_stamp % self.client.waiting_time == 0:

		# time delta
		delta = self.waiting_time * int(time_stamp/self.waiting_time) - time_stamp
		print(delta)

		# Periods:
                tmp_counter = int(time_stamp / self.client.waiting_time)

                if self.counter == 0:
                    self.counter = tmp_counter
                else:
		    # we have skipped one period! Bad things...
                    while self.counter != tmp_counter + 1:
                        print("[Client] Going forward...", time_stamp - self.counter * self.waiting_time)
                        self._next()
                        self.counter += 1

                if self.started:
                    self._call()

                self.counter += 1
                if int(time_stamp + self.delta) % self.client.waiting_time == 0:
                    time.sleep(1/1000.0)

            # Just for debugging!
            i, _, _ = select.select([sys.stdin], [], [], 1/10000.0)
            for s in i:
                if s == sys.stdin:
                    test = sys.stdin.readline()
                    if test == "n\n":
                        print("next")
                        self._next()
                    if test == "a\n":
                        print("-10")
                        self.delta -= 10
                    if test == "d\n":
                        print("+10")
                        self.delta += 10

    def start(self):
        """
        Start the thread.
        """
        Thread.start(self)

    def stop(self):
        """
        Stop the thread.
        """
        self.stopped = True


class ClientListener (ClientBase):
    """
    A class to handle the listener client. Connects to the server, receives the correct values for frame rate and
    waiting time and starts receiving audio buffers.
    """
    def __init__(self):
        ClientBase.__init__(self)
        self.device = 0
        self.buffers = list()
        self.running = False

    def connect(self):
        """
        Connect to the server and get frame rate and waiting time. Then start the playing device.
        """
        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        # Tell the server we are a receiver
        self.client.sendall(b"receiver")

        # Get data from Server
        self.read_values_from_server()

        # Set the audio device
        self.device = alsaaudio.PCM(card="default")
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(self.frame_rate)
        self.device.setperiodsize(int(self.buffer_size/4))

        self.running = True

    def message_loop(self):
        """
        The message loop where the data is received from the server. Blocking!
        """
        while self.running:
            data = self.recv_exact()
            if data:
                self.buffers.append(data)
            else:
                print("[Client] No new data. Aborting!")
                self.running = False
                break


def main():
    """
    Main function
    Initialize a new instance of the client listener module
    and connect to the server.
    Then start the message loop (receive the data from the server).
    Also initialize a new thread to play the audio. Start waiting for the correct time.
    Repeat until Ctrl-C is hit.
    """
    client = ClientListener()
    client.connect()

    thread = PlayThread(client)
    thread.start()

    try:
        client.message_loop()
    except KeyboardInterrupt:
        pass
    finally:
        client.running = False
        client.close()
        thread.stop()


if __name__ == "__main__":
    main()
