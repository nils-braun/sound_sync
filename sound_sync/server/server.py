from sound_sync.networking.connection import Proxy, Message
from sound_sync.entities.buffer_list import RingBufferList


class Server:
    def __init__(self, publisher_port, subscriber_port, cache_length=10):
        self.proxy = Proxy(publisher_port, subscriber_port, self.frontend_method, self.backend_method)

        # Store last instance of each topic in a cache
        self.cache = dict()
        self.parameters = dict()
        self.cache_length = cache_length

    def backend_method(self):
        message = self.proxy.backend.recv()

        # Event is one byte 0 = unsub or 1 = sub, followed by topic
        if message[0] == 1:
            topic = message[1:]
            if topic in self.cache:
                # Resend the parameters of this channel for the newcomer
                parameter_message = Message(topic, "parameters", self.parameters[topic])
                parameter_message.send(self.proxy.backend)

                # Resend the cached buffers of this channel for the newcomer
                for content_message in self.cache[topic]:
                    content_message.send(self.proxy.backend)

    def frontend_method(self):
        message = Message.recv(self.proxy.frontend)

        if message.message_type == b"content":
            # Do only accept messages if the client has correctly identified itself
            if message.topic in self.cache:
                self.cache[message.topic].append(message)
        elif message.message_type == b"control":
            if message.message_body == b"add":
                self.cache[message.topic] = RingBufferList(self.cache_length)
            elif message.message_body == b"delete":
                del self.cache[message.topic]
            else:
                RuntimeError(message)
        elif message.message_type == b"parameters":
            self.parameters[message.topic] = message.message_body
        else:
            RuntimeError(message)

        message.send(self.proxy.backend)

    def main_loop(self):
        while True:
            self.proxy.poll()

    def initialize(self):
        pass

    def terminate(self):
        pass