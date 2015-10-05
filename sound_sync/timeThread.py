from threading import Thread
import time


class HandleCorrectStartTimeThread(Thread):
    """
    :type listener Listener
    """
    def __init__(self, listener):
        self.listener = listener
        self.is_running = False
        self.is_audio_playing = False

        self.next_playable_buffer_index = None

        Thread.__init__(self)

    def run(self):

        self.clear_audio_queue_and_reset_sound_buffer_list()

        while self.is_running and not self.is_audio_playing:
            time_stamp = int(time.time() * 1000 + self.delta)
            if self.is_correct_time_and_sound_buffer_is_full(time_stamp):
                self.set_current_playable_buffer_index(time_stamp)
                self.try_filling_audio_queue()

            time.sleep(1/1000.0)

    def clear_audio_queue_and_reset_sound_buffer_list(self):
        if self.listener.static_sound_buffer_list.current_buffer_index != -1:
            time_until_audio_queue_is_empty = self.calculate_time_until_audio_queue_is_empty()

            self.listener.static_sound_buffer_list.current_buffer_index = -1
            self.listener.is_audio_playing = False

            time.sleep(time_until_audio_queue_is_empty / 1000.0)

    def set_current_playable_buffer_index(self, time_stamp):
        real_sound_buffer_index = int((time_stamp - self.listener.player.start_time*1000.0) /
                                      self.listener.player.waiting_time)
        current_buffer_index = real_sound_buffer_index - self.listener.full_buffer_size
        self.listener.static_sound_buffer_list.current_buffer_index = current_buffer_index

    def try_filling_audio_queue(self):
        if ClientListener.static_sound_buffer_list.current_buffer_index + 5 < \
                ClientListener.static_sound_buffer_list.end_buffer_index:
            for _ in xrange(ClientListener.static_sound_buffer_list.end_buffer_index -
                    ClientListener.static_sound_buffer_list.current_buffer_index - 5):
                self.listener.play_next_playable_buffer()
            self.listener.is_audio_playing = True

    def calculate_time_until_audio_queue_is_empty(self):
        time_stamp = int(time.time() * 1000 + self.listener.player.added_delay)
        real_sound_buffer_index = int((time_stamp - self.listener.player.start_time * 1000.0) / self.listener.player.waiting_time)
        current_buffer_index = real_sound_buffer_index - self.listener.full_buffer_size
        current_waiting_time = (self.listener.buffer.next_free_address -
                                current_buffer_index) * self.listener.player.waiting_time
        return current_waiting_time

    def is_correct_time_and_sound_buffer_is_full(self, time_stamp):
        return (len(self.listener.incoming_buffer_list) > self.full_buffer_size
                and time_stamp % self.listener.waiting_time == 0)