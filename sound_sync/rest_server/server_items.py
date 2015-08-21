import datetime

from sound_sync.rest_server.json import JSONPickleable

class Channel(JSONPickleable):
    def __init__(self, item_hash):
        JSONPickleable.__init__(self)

        self.start_time = datetime.datetime.now()
        self.name = ""
        self.description = ""
        self.now_playing = ""
        self.item_hash = item_hash


class Client(JSONPickleable):
    def __init__(self, item_hash):
        JSONPickleable.__init__(self)

        self.login_time = datetime.datetime.now()
        self.ip_address = None
        self.name = ""
        self.item_hash = item_hash