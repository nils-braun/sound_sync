from datetime import timedelta
from functools import partial

from sound_sync.entities.buffer_list import BufferList
from sound_sync.listener.downloader_thread import DownloaderThread
from sound_sync.timing.time_utils import sleep
from sound_sync.timing.timer import Timer


class BaseListener:
    def __init__(self, host, port, channel_hash):
        #: The player to send the data to. Will be used by the player_thread
        self.player = None

        #: The buffer list over which the threads communicate TODO: Implement this with zeromq?
        self.buffer_list = BufferList(max_buffer_size=100)

        #: The thread used for downloading the buffers from the server
        self.downloader_thread = DownloaderThread(parent=self, host=host, port=port, channel_hash=channel_hash)

        self.chunksize = 3

        self.timer_list = []

    def initialize(self):
        self.player.initialize()

    def terminate(self):
        for timer in self.timer_list:
            timer.stop()

        self.downloader_thread.stop()

        self.player.terminate()

    def start_play(self):
        while len(self.buffer_list) <= self.chunksize:
            sleep(0.01)

        next_buffers = [self.buffer_list.pop() for _ in range(self.chunksize)]
        start_time = next_buffers[0].buffer_time + timedelta(seconds=3)
        end_time = next_buffers[-1].buffer_time
        try:
            play_timer = Timer(start_time, partial(self.play, buffer_list=next_buffers))
            play_timer.start()
            self.timer_list.append(play_timer)
        except ValueError:
            pass

        next_timer = Timer(end_time, self.start_play, always_run=True)
        next_timer.start()

        self.timer_list.append(next_timer)

    def play(self, buffer_list):
        for buffer in buffer_list:
            self.player.put(buffer.sound_buffer)

    def main_loop(self):
        self.downloader_thread.start()

        self.start_play()

        for timer in self.timer_list:
            timer.join()