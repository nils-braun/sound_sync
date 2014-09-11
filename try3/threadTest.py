#!/usr/bin/env python

import alsaaudio
import time
import wave
from threading import Thread # This is the right package name

WAITING_TIME = 200
FRAME_RATE = 44100
DEBUG = True


# Subclass of Thread
# Calls a function every WAITING_TIME ms
class UpdateThread(Thread):
    # Initialize the alsa device

    def __init__(self, call, waiting_time, delta):
        self.stopped = False
        self.call = call
        self.delta = delta
        self.waiting_time = waiting_time

        if DEBUG:
            self._dev = 0.0
            self._counter = 0

        # Call the super constructor
        Thread.__init__(self)

    def run(self):
        while not self.stopped:
            # in ms
            time_stamp = time.time() * 1000
            if int(time_stamp + self.delta) % WAITING_TIME == 0:

                self.call()

                if DEBUG:
                    deviation = time_stamp - int(time_stamp / WAITING_TIME) * WAITING_TIME
                    if deviation > 1:
                        deviation -= WAITING_TIME
                    self._dev += deviation

                    self._counter += 1

                    if self._counter == 10:
                        print(self._dev/10.0)
                        self._dev = 0
                        self._counter = 0
            else:
                time.sleep(1/10000.0)

    def start(self):
        Thread.start(self)


class Output:
    def __init__(self):
        self.device = alsaaudio.PCM(card="default")
        self.device.setchannels(2)
        self.device.setrate(FRAME_RATE)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.buffer_size = int(WAITING_TIME/1000.0 * FRAME_RATE)
        self.device.setperiodsize(self.buffer_size)

    def write(self, data):
        self.device.write(data)


class Input:
    def __init__(self, buffer_size):
        self.f = wave.open("../test.wav", "rb")
        self.buffer_size = buffer_size

    def read(self):
        return self.f.readframes(self.buffer_size)


# Main
# Initialize and start the updating thread
if __name__ == "__main__":

    output = Output()
    input = Input(output.buffer_size)

    thread = UpdateThread(lambda: output.write(input.read()), WAITING_TIME, 0)

    try:
        thread.start()
    except KeyboardInterrupt:
        thread.stopped = True






