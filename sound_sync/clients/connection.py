import json
import urllib

import zmq as zmq

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from tornado import httpclient

__author__ = 'nils'


class SoundSyncConnection:
    """
    Class to handle the connection to the sound sync server from a client.
    """

    def __init__(self, host=None, manager_port=None):
        #: The port of the manager host
        self.manager_port = manager_port

        #: The address of the manager host
        self.host = host

        #: A http client to use (for free ;-)
        self.http_client = httpclient.HTTPClient()

        #: A different manager string, only used for testing
        self._manager_string = None

    @property
    def manager_string(self):
        if self._manager_string is not None:
            return self._manager_string
        else:
            return "http://" + str(self.host) + ":" + str(self.manager_port)

    @manager_string.setter
    def manager_string(self, mock_url):
        self._manager_string = mock_url

    def send_to_url(self, url, content=None, method="POST"):
        if content:
            body = urllib.parse.urlencode(content)
            response = self.http_client.fetch(self.manager_string + url, body=body, method=method)
        else:
            response = self.http_client.fetch(self.manager_string + url)

        response.rethrow()
        return response

    def add_channel_to_server(self):
        response = self.send_to_url("/channels/add")
        channel_hash = str(response.body, encoding="utf8")
        return channel_hash

    def add_client_to_server(self):
        response = self.send_to_url("/clients/add")
        client_hash = str(response.body, encoding="utf8")
        return client_hash

    def remove_channel_from_server(self, channel_hash):
        self.send_to_url("/channels/delete/{channel_hash}".format(channel_hash=channel_hash))

    def remove_client_from_server(self, client_hash):
        self.send_to_url("/clients/delete/{client_hash}".format(client_hash=client_hash))

    def get_channel_information(self, channel_hash):
        response = self.send_to_url("/channels/get/{channel_hash}".format(channel_hash=channel_hash))
        response_dict = json.loads(str(response.body, encoding="utf8"))
        return response_dict

    def get_channels(self):
        response = self.send_to_url("/channels/get")
        response_dict = json.loads(str(response.body, encoding="utf8"))
        return response_dict

    def get_clients(self):
        response = self.send_to_url("/clients/get")
        response_dict = json.loads(str(response.body, encoding="utf8"))
        return response_dict

    def set_name_and_description_of_channel(self, name, description, channel_hash):
        parameters = {"name": name, "description": description}
        self.set_parameters_of_channel(parameters, channel_hash)

    def set_parameters_of_channel(self, parameters, channel_hash):
        self.send_to_url("/channels/set/{channel_hash}".format(channel_hash=channel_hash), parameters)

    def set_name_of_client(self, name, client_hash):
        parameters = {"name": name}
        self.send_to_url("/clients/set/{channel_hash}".format(channel_hash=client_hash), parameters)

    def add_buffer(self, sound_buffer, channel_hash):
        parameters = {"buffer": sound_buffer.to_string()}
        self.send_to_url("/buffers/{channel_hash}/add".format(channel_hash=channel_hash), parameters)

    def get_buffer(self, buffer_number, channel_hash):
        buffer = self.get_buffer_raw(buffer_number, channel_hash)
        return SoundBufferWithTime.construct_from_string(buffer)

    def get_buffer_raw(self, buffer_number, channel_hash):
        buffer = self.send_to_url("/buffers/{channel_hash}/get/{buffer_number}".format(channel_hash=channel_hash,
                                                                                       buffer_number=buffer_number))
        return str(buffer.body, encoding="utf8")

    def get_start_index(self, channel_hash):
        return self.get_buffer_index("start", channel_hash)

    def get_end_index(self, channel_hash):
        return self.get_buffer_index("end", channel_hash)

    def get_buffer_index(self, start_or_end, channel_hash):
        return int(self.send_to_url("/buffers/{channel_hash}/{start_or_end}".format(channel_hash=channel_hash,
                                                                                    start_or_end=start_or_end)).body)


class Message:
    def __init__(self, topic, message_type, message_body):
        self.topic = self.as_buffer(topic)
        self.message_type = self.as_buffer(message_type)
        self.message_body = self.as_buffer(message_body)

    def send(self, socket):
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