import json

import collections
import zmq as zmq


class Message:
    def __init__(self, topic, message_type, message_body):
        self.topic = self.as_buffer(topic)
        self.message_type = self.as_buffer(message_type)
        self.message_body = self.as_buffer(message_body)

    def send(self, socket):
        print("Sending to", self.topic, "a", self.message_type, "message")
        socket.send_multipart([self.as_buffer(self.topic),
                               self.as_buffer(self.message_type),
                               self.as_buffer(self.message_body)])

    @staticmethod
    def recv(socket):
        message = socket.recv_multipart()
        return Message(*message)

    @staticmethod
    def as_buffer(x):
        if isinstance(x, bytes):
            return x

        try:
            return x.encode()
        except AttributeError:
            try:
                return str(x).encode()
            except TypeError:
                return x

    def __str__(self):
        return "{self.message_type} ({self.topic}): {self.message_body}".format(self=self)


class Socket:
    def __init__(self, context=None):
        if not context:
            self.context = zmq.Context.instance()
        else:
            self.context = self.context

    @staticmethod
    def as_uuid(subscription):
        return Message.as_buffer("%03d" % int(subscription))

    def get_socket(self, socket_type, url, bind, options=None):
        socket = self.context.socket(socket_type)

        if bind:
            socket.bind(url)
        else:
            socket.connect(url)

        if options:
            for key, value in options.items():
                socket.setsockopt(key, value)

        return socket

    def get_bound_socket(self, socket_type, url, options=None):
        return self.get_socket(socket_type=socket_type, url=url, bind=True, options=options)

    def get_connected_socket(self, socket_type, url, options=None):
        return self.get_socket(socket_type=socket_type, url=url, bind=False, options=options)


class Publisher(Socket):
    """
    Class to handle the connection to the sound sync server from a client.
    """

    def __init__(self, host, port, topic, context=None):
        # Publisher is connected to publisher port of host
        super().__init__(context)

        self._publisher = self.get_connected_socket(socket_type=zmq.PUB,
                                                    url="tcp://{host}:{port}".format(host=host, port=port))

        # Initialise topic by translating it to a correctly formatted topic
        self.topic = self.as_uuid(topic)

    def _send_content(self, content):
        message = Message(self.topic, "content", content)
        message.send(self._publisher)

    def _send_control(self, control_flag):
        message = Message(self.topic, "control", str(control_flag))
        message.send(self._publisher)

    def _send_parameters(self, parameters):
        message = Message(self.topic, "parameters", json.dumps(parameters))
        message.send(self._publisher)

    def add_channel_to_server(self):
        self._send_control("add")

    def remove_channel_from_server(self):
        self._send_control("remove")

    def set_name_and_description_of_channel(self, name, description):
        parameters = {"name": name, "description": description}
        self._send_parameters(parameters)

    def add_buffer(self, sound_buffer):
        self._send_content(sound_buffer.to_string())


class Subscriber(Socket):
    """
    Class to handle the connection to the sound sync server from a client.
    """

    def __init__(self, host, port, topic, context=None):
        #: The port of the manager host
        super().__init__(context)

        # Initialise topic by translating it to a correctly formatted topic
        self.topic = self.as_uuid(topic)

        self.subscriber = self.get_connected_socket(socket_type=zmq.SUB,
                                                    url="tcp://{host}:{port}".format(host=host, port=port),
                                                    options={zmq.SUBSCRIBE: self.topic})

    def receive(self):
        message = Message.recv(self.subscriber)
        assert message.topic == self.topic

        return message


class Proxy(Socket):
    def __init__(self, publisher_port, subscriber_port, cache_length=100, context=None):
        super().__init__(context)

        self.frontend = self.context.socket(zmq.SUB)
        self.frontend.bind("tcp://*:{port}".format(port=publisher_port))
        self.backend = self.context.socket(zmq.XPUB)
        self.backend.bind("tcp://*:{port}".format(port=subscriber_port))

        # Subscribe to every single topic from publisher
        self.frontend.setsockopt(zmq.SUBSCRIBE, b"")

        # Listen to all new subscriptions
        self.backend.setsockopt(zmq.XPUB_VERBOSE, True)

        # Store last instance of each topic in a cache
        self.cache = collections.defaultdict(lambda: collections.deque(maxlen=cache_length))

        self.poller = zmq.Poller()

        self.dict_of_pollers = {self.frontend: self.frontend_method, self.backend: self.backend_method}

        for poll_item in self.dict_of_pollers.keys():
            self.poller.register(poll_item, zmq.POLLIN)

    def backend_method(self):
        event = self.backend.recv()

        print("Server backend:", event)

        # Event is one byte 0=unsub or 1=sub, followed by topic
        if event[0] == 1:
            topic = event[1:]
            if topic in self.cache:
                print("Sending cached topic %s" % topic)
                for message in self.cache[topic]:
                    message.send(self.backend)

    def frontend_method(self):
        message = Message.recv(self.frontend)

        print("Server frontend:", message)

        self.cache[message.topic].append(message)

        message.send(self.backend)

    def poll(self):
        events = dict(self.poller.poll())

        for poll_item, poll_function in self.dict_of_pollers.items():
            if poll_item in events:
                poll_function()