import json
from collections import deque
from datetime import timedelta

from sound_sync.clients.connection import Subscriber
from sound_sync.entities.buffer_list import OrderedBufferList
from sound_sync.entities.channel import Channel
from sound_sync.entities.json_pickable import JSONPickleable
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import get_current_date
from sound_sync.timing.timer import Timer


class BaseListener:
    def __init__(self, host, port, channel_hash):
        #: The player to send the data to. Will be used by the player_thread
        self.player = None

        #: The buffer list
        self.buffer_list = OrderedBufferList(max_buffer_size=100)

        self.chunksize = 10

        self.timer_list = []

        #: The connection to the rest server
        self.connection = Subscriber(host, port, channel_hash)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The channel we are listening to
        self._connected_channel = None

        self.current_delta = timedelta()

    def use_settings(self, channel_information):
        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def initialize(self):
        self.player.initialize()

    def terminate(self):
        for timer in self.timer_list:
            timer.stop()

        # TODO: This seems to hang. Why?
        #self.player.terminate()

    def start_play(self):
        print("Started player thread")

        deltas = deque(maxlen=100)

        while True:
            next_buffer = self.buffer_list.pop()

            time_distance = self.play_next_buffer(next_buffer)
            deltas.append(time_distance)

            average_delta = sum(deltas, timedelta()) / len(deltas)

            print(time_distance, average_delta)

            if average_delta.total_seconds() > 0.001 and len(deltas) > 10:
                # schedule 10th buffer with new delta
                self.current_delta += average_delta

                assert self.buffer_list.is_continuous_until(self.chunksize)

                next_playable_buffers = [self.buffer_list.pop() for _ in range(self.chunksize)]
                self.start_player_thread_on_buffer(self.buffer_list.glimpse())

                # play remaining buffers buffers
                for next_buffer in next_playable_buffers[:-1]:
                    self.play_next_buffer(next_buffer)

                break

    def play_next_buffer(self, next_buffer):
        print("Playing", next_buffer.buffer_number)
        self.player.put(next_buffer.sound_buffer)
        start_time = self.calculate_start_time(next_buffer)
        current_date = get_current_date()

        return current_date - start_time

    def main_loop(self):
        while True:
            message = self.connection.receive()

            if message.message_type == b"control":
                print("Got control message", message)
            elif message.message_type == b"parameters":
                print("Got settings", message)
                if self._connected_channel is None:
                    parameters = json.loads(str(message.message_body, encoding="utf8"))
                    self.use_settings(parameters)
                else:
                    print("Not implemented in the moment")
            elif message.message_type == b"content":
                # print("Got content", message)
                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(
                    str(message.message_body, encoding="utf8"))

                self.buffer_list.append(sound_buffer_with_time)

                if len(self.timer_list) == 0:
                    self.start_player_thread_on_buffer(sound_buffer_with_time)

            else:
                raise ValueError(message)

            for timer in self.timer_list:
                if not timer._should_run:
                    timer.join()

    def start_player_thread_on_buffer(self, sound_buffer_with_time):
        timer_time = self.calculate_start_time(sound_buffer_with_time) - self.current_delta
        print("Starting first player at", timer_time, "for", sound_buffer_with_time.buffer_number)
        next_timer = Timer(timer_time,
                           self.start_play)
        next_timer.start()
        self.timer_list.append(next_timer)

    def calculate_start_time(self, sound_buffer_with_time):
        return sound_buffer_with_time.buffer_time + timedelta(seconds=3)