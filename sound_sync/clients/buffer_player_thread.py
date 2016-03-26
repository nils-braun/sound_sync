from datetime import timedelta
from threading import Thread

from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import sleep
from sound_sync.timing.timer import Timer


class BufferPlayerThread(Thread):
    def __init__(self, buffer_list, player):
        super(BufferPlayerThread, self).__init__()

        self.player = player
        self.buffer_list = buffer_list
        self.last_played_buffer_number = None
        self._should_run = True

    def run(self):
        while not self.last_played_buffer_number and self._should_run:
            start_index_in_buffer_list = self.buffer_list.get_start_index()
            if start_index_in_buffer_list > 0:
                self.last_played_buffer_number = start_index_in_buffer_list

        print("Finished initializing, starting with", self.last_played_buffer_number)

        while self._should_run:
            end_index_in_buffer_list = self.buffer_list.get_next_free_index() - 1

            if (end_index_in_buffer_list > 0 and (self.last_played_buffer_number < end_index_in_buffer_list)):
                next_buffer_number = self.last_played_buffer_number + 1
                print("Getting", next_buffer_number)
                sound_buffer = self.buffer_list.get_buffer(str(next_buffer_number))
                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(sound_buffer)

                assert sound_buffer_with_time.buffer_number == next_buffer_number

                self.start_play_timer(sound_buffer_with_time)
                self.last_played_buffer_number = next_buffer_number

    def start_play_timer(self, sound_buffer_with_time):
        def play():
            print("Playing", sound_buffer_with_time.buffer_number)
            #self.player.put(sound_buffer_with_time.sound_buffer)

        sound_buffer_with_time.buffer_time += timedelta(seconds=1)

        try:
            print("Starting player for", sound_buffer_with_time.buffer_number)
            timer = Timer(sound_buffer_with_time.buffer_time, play)
            timer.run()
        except ValueError:
            pass

    def terminate(self):
        self._should_run = False