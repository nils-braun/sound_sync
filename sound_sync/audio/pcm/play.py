from sound_sync.audio.pcm.device import PCMDevice


class PCMPlay(PCMDevice):
    """
    The PCM device of the ALSA playback. The data to be played by this program is sent through
    this into the read sound device.
    """
    def __init__(self):
        PCMDevice.__init__(self)

    def initialize(self):
        """
        Set the PCM device with the usual parameters.
        """
        if self.pcm is not None:
            return

        self.initialize_pcm(card_name="default", capture_device=False)