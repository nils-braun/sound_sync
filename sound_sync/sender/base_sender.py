from sound_sync.networking.connection import Publisher
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.entities.channel import Channel
from sound_sync.timing.time_utils import get_current_date

import logging

from sound_sync.tp.ntp_client import NTPClient
from sound_sync.tp.ptp_client import PTPClient

logger = logging.getLogger(__name__)


class BaseSender(Channel):
    """
    Base class for a sender client.
    The client has two tasks:
    (1) Get the correct time from the server
    (2) Record sound packages from the loopback device and send (=publish) them to the server.

    Each sender is classified by a unique hash, where all listener can connect to.
    It also needs the host and the port of the server to connect and publish to.
    """
    def __init__(self, host, port, hash):
        Channel.__init__(self)

        #: The connection to the rest server
        self.connection = Publisher(host, port, hash)

        #: The recorder used for recording the sound data
        self.recorder = None

        # The hash of this channel which is used to identify on the server
        self.channel_hash = hash

        # The client we will use to get the current time from the server
        self.time_client = PTPClient(host=host)

    def initialize(self):
        logger.debug("Initializing sender")

        self.connection.add_channel_to_server()
        self.connection.set_name_and_description_of_channel(self.name, self.description)

        # TODO: Send sound settings

        self.recorder.initialize()

        self.time_client.start()

    def main_loop(self):
        logger.debug("Starting sender")

        starting_time = get_current_date()
        buffer_number = 0

        while True:
            sound_buffer, length = self.recorder.get()
            # TODO: Better use the real time here?
            buffer_time = starting_time + self.recorder.get_waiting_time() * buffer_number
            buffer_time += self.time_client.offset

            send_buffer = SoundBufferWithTime(sound_buffer=sound_buffer,
                                              buffer_number=buffer_number,
                                              buffer_time=buffer_time)

            logger.debug("Sending buffer with number "
                         "{buffer.buffer_number} to start at {buffer.buffer_time}".format(buffer=send_buffer))

            self.connection.add_buffer(send_buffer)
            buffer_number += 1

    def terminate(self):
        logger.debug("Terminating sender")
        self.connection.remove_channel_from_server()