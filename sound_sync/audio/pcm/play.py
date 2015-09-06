from sound_sync.audio.pcm.device import PCMDevice
from sound_sync.audio.sound_device import SoundDevice


class PCMPlay(SoundDevice, PCMDevice):
    # The PCM device of the ALSA-Loopback-Adapter. The data coming from the applications
    # is send through this loopback into the program. We need a frame rate of 44100 Hz and collect 10 ms of data
    # at once.

    def __init__(self):
        SoundDevice.__init__(self)
        PCMDevice.__init__(self)

    def initialize(self):
        """
        Set the PCM device with the usual parameters.
        """
        if self.pcm is not None:
            return

        self.initialize_pcm(card_name="default", capture_device=False, blocking=False)

    def put(self, sound_buffer):
        PCMDevice.put(self, sound_buffer)