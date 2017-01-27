from sound_sync.networking.connection import Proxy, Message
from sound_sync.entities.buffer_list import RingBufferList

import logging
logger = logging.getLogger(__name__)

# Event is one byte 0 = unsub or 1 = sub, followed by topic
SUBSCRIBE_MESSAGE = 1


class Server:
    """
    Class for representing a server to receive and send messages from/to the clients.

    Has an input (for the senders) and and output (for the listeners) side. All content
    messages from the sender side will be send to the listener and cached in case a new
    listener wants to connect (to send the latest history). Also, all parameters are stored
    and send to the newly connecting listeners.
    """
    def __init__(self, publisher_port, subscriber_port, cache_length=50):
        # The both sockets fro in and output calling the both member functions each time a new message arrives
        self.proxy = Proxy(publisher_port, subscriber_port, self.input_method, self.output_method)

        # Store last instance of each topic in a cache
        self.cache = dict()

        # Store the parameters of each topic in another cache
        self.parameters = dict()

        # How many messages should be cached
        self.cache_length = cache_length

    def output_method(self):
        message = self.proxy.output_socket.recv()

        if message[0] == SUBSCRIBE_MESSAGE:
            topic = message[1:]

            logger.debug("New connected listener on topic {topic}".format(topic=topic))

            if topic in self.cache:
                # Resend the parameters of this channel for the newcomer
                parameter_message = Message(topic, "parameters", self.parameters[topic])
                parameter_message.send(self.proxy.output_socket)

                # Resend the cached buffers of this channel for the newcomer
                for content_message in self.cache[topic]:
                    content_message.send(self.proxy.output_socket)

    def input_method(self):
        message = Message.recv(self.proxy.input_socket)

        if message.message_type == b"content":
            # Do only accept messages if the client has correctly identified itself
            if message.topic in self.cache:
                self.cache[message.topic].append(message)
        elif message.message_type == b"control":
            logger.debug("Received control message: {message}".format(message=message))

            if message.message_body == b"add":
                self.cache[message.topic] = RingBufferList(self.cache_length)
            elif message.message_body == b"delete":
                del self.cache[message.topic]
            else:
                RuntimeError(message)
        elif message.message_type == b"parameters":
            logger.debug("Received parameter message: {message}".format(message=message))

            self.parameters[message.topic] = message.message_body
        else:
            logger.error("Do not now how to cope with the message: ".format(message=message))
            RuntimeError(message)

        # In all cases, give the message to the listeners
        message.send(self.proxy.output_socket)

    def main_loop(self):
        logger.debug("Starting server")

        while True:
            self.proxy.poll()

    def initialize(self):
        logger.debug("Initializing server")

        pass

    def terminate(self):
        logger.debug("Terminating server")

        # Send a goodbye to every client
        for channel_hash in self.cache:
            bye_message = Message(channel_hash, b"control", b"delete")
            bye_message.send(self.proxy.output_socket)
