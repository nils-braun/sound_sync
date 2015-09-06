from sound_sync.audio.pcm.device import PCMDevice
from sound_sync.audio.sound_device import SoundDevice


class PCMRecorder(PCMDevice, SoundDevice):
    def __init__(self):
        SoundDevice.__init__(self)
        PCMDevice.__init__(self)

    def initialize(self):
        """
        Set the PCM device with the usual parameters.
        """
        if self.pcm is not None:
            return

        self.assert_loopback_device()
        self.initialize_pcm(card_name="hw:Loopback,1,0", capture_device=True, blocking=True)

    def get(self):
        length = 0
        sound_buffer = r""
        for i in xrange(int(self.factor)):
            current_length, current_sound_buffer = PCMDevice.get(self)
            length += current_length
            sound_buffer += current_sound_buffer
        return sound_buffer, length
