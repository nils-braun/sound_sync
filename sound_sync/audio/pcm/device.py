import alsaaudio

from sound_sync.audio.sound_device import SoundDevice

import logging
logger = logging.getLogger(__name__)


class PCMDevice(SoundDevice):
    """
    Basic class for accessing the sound devices from ALSA via the alsaaudio
    library. Ha basic functionality for writing or reading sound data.
    """
    def __init__(self):
        """
        Constructor
        """
        SoundDevice.__init__(self)

        #: The handled PCM device.
        self.pcm = None

    def initialize_pcm(self, card_name, capture_device=False):
        """
        Set the PCM device with the given parameters.
        """
        if capture_device:
            pcm_type = alsaaudio.PCM_CAPTURE
        else:
            pcm_type = alsaaudio.PCM_PLAYBACK

        self.pcm = alsaaudio.PCM(device=card_name, type=pcm_type)

        self.pcm.setchannels(int(self.channels))
        self.pcm.setrate(int(self.frame_rate))
        self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(int(self.buffer_size))

        logging.debug("Initializing a PCM device on "
                      "{card_name} of type {pcm_type}".format(card_name=card_name, pcm_type=pcm_type))

    @staticmethod
    def assert_loopback_device():
        """
        Raise an error if there is no loopback device initialized
        """
        card_list = alsaaudio.cards()
        if "Loopback" not in card_list:
            raise ValueError("There is no Loopback module loaded by ALSA. Loopback is needed by the program. " +
                             "Try loading it via modprobe or add it to /etc/modules or to a file in /etc/modules.d/.")

    def terminate(self):
        """
        Terminate the device by closing the handled PCM resource.
        """
        if self.pcm:
            self.pcm.close()

        logging.debug("Closing PCM device.")

    def get(self):
        """
        Low-level get function to retrieve sound data from a PCM device.
        The device has to be opened in recording mode.
        :return: the sound data in bytes and the sound data length.
        """
        if self.pcm is None:
            raise ValueError("Device needs to be initialized first")

        try:
            current_length, current_sound_buffer = self.pcm.read()
            return current_sound_buffer, current_length
        except Exception as e:
            raise RuntimeError("Reading from the sound device failed: " + str(e))

    def put(self, sound_buffer):
        """
        Low-level put function to send sound data as bytes to
        the PCM device. The device has to be opened in playback mode.
        :param sound_buffer: the sound data in bytes to write to the device.
        """
        if self.pcm is None:
            raise ValueError("Device needs to be initialized first")

        assert isinstance(sound_buffer, bytes)

        try:
            self.pcm.write(sound_buffer)
        except Exception as e:
            raise RuntimeError("Writing to the sound device failed: " + str(e))
