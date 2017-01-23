from collections import deque

import logging
logger = logging.getLogger(__name__)

class RingBufferList:
    """
    Simple implementation of a ring buffer, that is basically
    just a thin wrapper around a deque.

    The reason to have this class at all is to capsule the implementation.
    """
    def __init__(self, max_buffer_size):
        """
        Constructor.
        :param max_buffer_size: The maximal size of the buffer. If more items
         are filled in, the oldest are removed.
        """
        self.buffers = deque(maxlen=max_buffer_size)

    def __getitem__(self, index):
        """
        Get an item with the given index.
        :param index: The index
        :return: The item at this index or an IndexError, if the index is invalid.
        """
        return self.buffers[index]

    def append(self, item):
        """
        Add a new element to the buffer.
        If the max_buffer_size is exceeded, the oldest item will be deleted.
        :param item: The item to add
        """
        self.buffers.append(item)


class OrderedBufferList:
    """
    More advanced implementation of a ring buffer for SoundBufferWithTime
    items, which is always sorted by the buffer_number of the sound buffers
    and duplicates are automatically deleted. Additionally, it raises an IndexError
    when the next element in the row was not stored before accessing.
    """
    def __init__(self, max_buffer_size):
        """
        Constructor.
        :param max_buffer_size: The maximal size of the buffer. If more items
         are filled in, the oldest are removed.
        """
        self._buffers = deque(maxlen=max_buffer_size)

        # Always keep the buffer the same length
        for i in range(max_buffer_size):
            self._buffers.append(None)

        # Store the index of the first buffer in the list
        self._start_index = None

    def append(self, item):
        """
        Append a new sound buffer to the list.
        If the buffer number is below the first buffer in this list,
        do not store it. If a buffer with the same buffer number is already in the list,
        it will be overwritten.
        :param item: The sound buffer to add.
        """
        item_buffer_number = item.buffer_number

        if self._start_index is None:
            self._start_index = item_buffer_number

        index_number = item_buffer_number - self._start_index
        if index_number >= 0:
            self._buffers[index_number] = item

    def pop(self):
        """
        Retrieve the next item from the list. 'Pop'ing will always give a
        continuous list of buffer numbers. If a buffer number can not be found in the
        list, an IndexError is raised.
        :return: The next buffer in the row.
        """
        return_buffer = self._buffers.popleft()

        self._start_index += 1

        assert self._buffers[0] is None or self._buffers[0].buffer_number == self._start_index

        # Always keep the buffer full
        self._buffers.append(None)

        # Raise an exception if the buffer was not stored into the list already
        if return_buffer:
            return return_buffer
        else:
            logger.debug("Buffer with buffer number {buffer_number} "
                         "is not in list with length {length} (after pop)."
                         .format(buffer_number=self._start_index - 1, length=len(self._buffers)))
            raise IndexError
