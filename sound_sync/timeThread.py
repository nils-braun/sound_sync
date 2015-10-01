import time

__author__ = 'nils'


class HandleCorrectStartTimeThread(Thread):
    """
    A class to handle the thread to play the audio from the buffers of the client.
    When running waits for the correct time (time + delta) % waiting_time == 0 and starts playing the correct buffer.
    After that, move all incoming buffers to the sound queue.
    """

    def __init__(self, client):
        self.delta = 0.1        # The delta in ms to correct for wrong timing. Not very useful at the moment?
        assert isinstance(client, ClientListener)
        self.client = client

        Thread.__init__(self)

    def run(self):

        self.clear_audio_queue_and_reset_sound_buffer_list()

        while self.client.is_running and not self.client.is_audio_playing:
            time_stamp = int(time.time() * 1000 + self.delta)
            if self.is_correct_time_and_sound_buffer_is_full(time_stamp):
                self.set_current_playable_buffer_index(time_stamp)
                self.try_filling_audio_queue()

            time.sleep(1/1000.0)

    def clear_audio_queue_and_reset_sound_buffer_list(self):
        if self.client.static_sound_buffer_list.current_buffer_index != -1:
            time_until_audio_queue_is_empty = self.calculate_time_until_audio_queue_is_empty()

            self.client.static_sound_buffer_list.current_buffer_index = -1
            self.client.is_audio_playing = False

            time.sleep(time_until_audio_queue_is_empty / 1000.0)

    def set_current_playable_buffer_index(self, time_stamp):
        real_sound_buffer_index = int((time_stamp - self.client.start_time*1000.0) /
                                      ClientListener.clientInformation.waiting_time)
        current_buffer_index = real_sound_buffer_index - ClientListener.clientInformation.full_sound_buffer_size
        self.client.static_sound_buffer_list.current_buffer_index = current_buffer_index

    def try_filling_audio_queue(self):
        if ClientListener.static_sound_buffer_list.current_buffer_index + 5 < \
                ClientListener.static_sound_buffer_list.end_buffer_index:
            for _ in xrange(ClientListener.static_sound_buffer_list.end_buffer_index -
                    ClientListener.static_sound_buffer_list.current_buffer_index - 5):
                self.client.play_next_playable_buffer()
            self.client.is_audio_playing = True

    def calculate_time_until_audio_queue_is_empty(self):
        time_stamp = int(time.time() * 1000 + self.delta)
        real_sound_buffer_index = int((time_stamp - self.client.start_time * 1000.0) /
                                      ClientListener.clientInformation.waiting_time)
        current_buffer_index = real_sound_buffer_index - ClientListener.clientInformation.full_sound_buffer_size
        current_waiting_time = (self.client.static_sound_buffer_list.current_buffer_index -
                                current_buffer_index) * ClientListener.clientInformation.waiting_time
        return current_waiting_time

    def is_correct_time_and_sound_buffer_is_full(self, time_stamp):
        return len(self.client.static_sound_buffer_list.buffers) > \
               ClientListener.clientInformation.full_sound_buffer_size \
               and time_stamp % ClientListener.clientInformation.waiting_time == 0