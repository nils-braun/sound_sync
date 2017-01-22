import json
from collections import deque
from datetime import timedelta

from sound_sync.networking.connection import Subscriber
from sound_sync.entities.buffer_list import OrderedBufferList
from sound_sync.entities.channel import Channel
from sound_sync.entities.json_pickable import JSONPickleable
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import get_current_date
from sound_sync.timing.timer import Timer


class PlayerClient:
    def __init__(self):
        #: The player to send the data to. Will be used by the player_thread
        self.player = None

        self.measure_chunksize = 10
        self.restart_chunksize = 3

        self.current_delta = timedelta()

        self.timer_list = []

        self.time_shift = None

        #: The buffer list
        self.buffer_list = OrderedBufferList(max_buffer_size=100)

        self.deltas = deque(maxlen=self.measure_chunksize)

        self.maximum_delta = timedelta(seconds=0.001)

        self.connection_time = timedelta(seconds=0.1)

    def initialize(self):
        self.player.initialize()

        self.time_shift = self.restart_chunksize * (self.player.get_waiting_time() + self.connection_time)

        print(self.time_shift)

    def terminate(self):
        for timer in self.timer_list:
            timer.cancel()

        # TODO: This seems to hang. Why?
        #self.player.terminate()

    def play_loop(self, buffer_number):
        print("Will now restart")
        self.deltas.clear()

        while True:
            next_buffer = self.buffer_list.pop()

            assert next_buffer.buffer_number == buffer_number or buffer_number is None

            buffer_number = None

            time_distance = self._play_and_measure_delta(next_buffer)
            self.deltas.append(time_distance)

            if not self._check_time_delta(next_buffer):
                break

    def start_playing_at_time(self, buffer_time, buffer_number):
        buffer_time += self.time_shift
        buffer_time -= self.current_delta

        try:
            next_timer = Timer(buffer_time, self.play_loop, buffer_number=buffer_number)
            next_timer.start()
            self.timer_list.append(next_timer)
        except ValueError:
            pass

    def _check_time_delta(self, next_buffer):
        if self.average_delta < self.maximum_delta or len(self.deltas) < self.measure_chunksize:
            return True

        print("Need to schedule a restart, because delta of", self.average_delta, "is too large")

        # schedule buffer with new delta
        self.current_delta += self.average_delta

        buffer_time_after_that = next_buffer.buffer_time + (self.restart_chunksize + 1) * self.player.get_waiting_time()
        buffer_number_after_that = next_buffer.buffer_number + self.restart_chunksize + 1
        self.start_playing_at_time(buffer_time_after_that, buffer_number_after_that)

        # play remaining buffers
        for _ in range(self.restart_chunksize - 1):
            next_buffer = self.buffer_list.pop()
            self._play_and_measure_delta(next_buffer)

        # Skip last buffer
        self.buffer_list.pop()

        return False

    def _play_and_measure_delta(self, next_buffer):
        self.player.put(next_buffer.sound_buffer)

        # We want to compare to the real buffer time, to no current_delta in here!
        buffer_time = next_buffer.buffer_time + self.time_shift
        current_time = get_current_date()

        return current_time - buffer_time

    @property
    def average_delta(self):
        return sum(self.deltas, timedelta()) / len(self.deltas)


class BaseListener(PlayerClient):
    def __init__(self, host, port, channel_hash):
        super().__init__()

        #: The connection to the rest server
        self.connection = Subscriber(host, port, channel_hash)

        #: The channel we are listening to
        self._connected_channel = None

    def use_settings(self, channel_information):
        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def main_loop(self):
        while True:
            message = self.connection.receive()

            if message.message_type == b"control":
                # TODO
                print("Got control message", message)

            elif message.message_type == b"parameters":
                if self._connected_channel is None:
                    parameters = json.loads(str(message.message_body, encoding="utf8"))
                    self.use_settings(parameters)
                else:
                    # TODO
                    print("Not implemented in the moment")

            elif message.message_type == b"content":
                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(
                    str(message.message_body, encoding="utf8"))

                self.buffer_list.append(sound_buffer_with_time)

                if len(self.timer_list) == 0:
                    self.start_playing_at_time(sound_buffer_with_time.buffer_time, sound_buffer_with_time.buffer_number)

            else:
                raise ValueError(message)

            for timer in self.timer_list:
                if timer.is_finished():
                    timer.join()

            self.timer_list = [timer for timer in self.timer_list if not timer.is_finished()]

