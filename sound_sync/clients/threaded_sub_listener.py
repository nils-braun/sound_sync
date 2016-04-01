from threading import Thread


class ThreadedSubListener(Thread):
    def __init__(self, parent_listener):
        super(ThreadedSubListener, self).__init__()

        #: The parent listener instance we talk to
        self.parent_listener = parent_listener
        self._should_run = True

    def terminate(self):
        self._should_run = False