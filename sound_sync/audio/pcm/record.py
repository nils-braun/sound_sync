from sound_sync.audio.pcm.device import PCMDevice
from sound_sync.audio.sound_device import SoundRecorder


class PCMRecorder(PCMDevice, SoundRecorder):
    def initialize(self):
        """
        Set the PCM device with the usual parameters.
        """
        if self.pcm is not None:
            return

        self.assert_loopback_device()
        self.initialize_pcm(card_name="hw:Loopback,1,0", capture_device=True, blocking=True)

    def get(self):
        if self.pcm is None:
            raise ValueError("Recorder needs to be initialized first")

        length = 0
        sound_buffer = r""
        for i in xrange(int(self.factor)):
            current_length, current_sound_buffer = self.pcm.read()
            length += current_length
            sound_buffer += current_sound_buffer
        return sound_buffer, length
