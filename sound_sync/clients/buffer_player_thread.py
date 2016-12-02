from datetime import timedelta

from sound_sync.clients.threaded_sub_listener import ThreadedSubListener
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.timer import Timer


class BufferPlayerThread(ThreadedSubListener):
    def __init__(self, parent_listener):
        super(BufferPlayerThread, self).__init__(parent_listener)

        self.last_played_buffer_number = None

    def run(self):
        while not self.last_played_buffer_number and self._should_run:
            start_index_in_buffer_list = self.parent_listener.buffer_list.get_start_index()
            if start_index_in_buffer_list > 0:
                self.last_played_buffer_number = start_index_in_buffer_list

        print("Finished initializing, starting with", self.last_played_buffer_number)

        while self._should_run:
            end_index_in_buffer_list = self.parent_listener.buffer_list.get_next_free_index() - 1

            if (end_index_in_buffer_list > 0 and (self.last_played_buffer_number < end_index_in_buffer_list)):
                next_buffer_number = self.last_played_buffer_number + 1
                print("Getting", str(next_buffer_number))
                sound_buffer = self.parent_listener.buffer_list.get_buffer(str(next_buffer_number - 1))
                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(sound_buffer)

                print(sound_buffer_with_time.buffer_number, next_buffer_number)
                #assert sound_buffer_with_time.buffer_number == next_buffer_number

                self.start_play_timer(sound_buffer_with_time)
                self.last_played_buffer_number = next_buffer_number

    def start_play_timer(self, sound_buffer_with_time):
        def play():
            print("Playing", sound_buffer_with_time.buffer_number)
            self.parent_listener.player.put(sound_buffer_with_time.sound_buffer)

        sound_buffer_with_time.buffer_time += timedelta(seconds=23)
        print(sound_buffer_with_time.buffer_time)

        print("Starting player for", sound_buffer_with_time.buffer_number)
        try:
            timer = Timer(sound_buffer_with_time.buffer_time, play)
            timer.run()
        except ValueError:
            print("Value error")
            pass
