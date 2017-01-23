from sound_sync.audio.pcm.device import PCMDevice


class PCMRecorder(PCMDevice):
    """
    The PCM device of the ALSA-Loopback-Adapter. The data coming from the applications
    is sent through this loopback into the program.
    """
    def __init__(self):
        PCMDevice.__init__(self)

    def initialize(self):
        """
        Set the PCM device with the usual parameters.
        """
        if self.pcm is not None:
            return

        self.assert_loopback_device()
        self.initialize_pcm(card_name="hw:Loopback,1,0", capture_device=True)

    def get(self):
        """
        Overwritten get function to retrieve not only one, but self.factor
        sound buffers from the sound device.
        :return: the sound data in bytes and the sound data length.
        """
        length = 0
        sound_buffer = bytes()
        for i in range(int(self.factor)):
            current_sound_buffer, current_length = PCMDevice.get(self)
            length += current_length
            sound_buffer += current_sound_buffer
        return sound_buffer, length
