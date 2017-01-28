import json

from sound_sync.entities.channel import Channel
from sound_sync.entities.json_pickable import JSONPickleable
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.listener.player_client import PlayerClient
from sound_sync.networking.connection import Subscriber

import logging
logger = logging.getLogger(__name__)


class BaseListener(PlayerClient):
    """
    Base class for listening to the published sound buffers of a sender
    and play them at the exact buffer time.

    The listener has four main actions:
    (1) Receive messages from the sender via the server, e.g. new sound buffers or control messages
    (2) Schedule the playing of buffers
    (3) Get the current time from the server
    (4) Test, if the sound buffers were played at the correct time and reschedule if needed

    To save resources, it does not schedule the playing of buffers for each buffer independently,
    but tries to play as much buffers in a row as possible.

    All the play logic is handled in the base class, this implementation does only
    fetch the messaged from the server.
    """
    def __init__(self, host, port, channel_hash):
        super().__init__(host)

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
                if message.message_body == "remove":
                    logger.error("Sender disconnected from the server.")
                    return

            elif message.message_type == b"parameters":
                if self._connected_channel is None:
                    parameters = json.loads(str(message.message_body, encoding="utf8"))
                    self.use_settings(parameters)

                    logger.debug("Received the parameters of the sender: {parameters}"
                                 .format(parameters=parameters))
                else:
                    # TODO
                    logger.warning("This functionality is not implemented in the moment!")

            elif message.message_type == b"content":
                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(
                    str(message.message_body, encoding="utf8"))

                self.buffer_list.append(sound_buffer_with_time)

                if len(self.timer_list) == 0:
                    logger.debug("Trying to schedule the first buffer...")
                    if not self.start_playing_at_time(sound_buffer_with_time.buffer_time, sound_buffer_with_time.buffer_number):
                        self.buffer_list.pop()
            else:
                logger.error("Can not handle the message {message}.".format(message=message))
                raise ValueError(message)

            for timer in self.timer_list:
                if timer.is_finished():
                    timer.join()

            self.timer_list = [timer for timer in self.timer_list if not timer.is_finished()]

