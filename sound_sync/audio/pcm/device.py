from sound_sync.audio.sound_device import SoundDevice
import alsaaudio


class PCMDevice(SoundDevice):
    def __init__(self):
        SoundDevice.__init__(self)
        self.pcm = None

    def initialize_pcm(self, card_name, capture_device=False, blocking=False):
        """
        Set the PCM device with the given parameters.
        """
        if capture_device:
            pcm_type = alsaaudio.PCM_CAPTURE
        else:
            pcm_type = alsaaudio.PCM_PLAYBACK

        if not blocking:
            self.pcm = alsaaudio.PCM(device=card_name, type=pcm_type, mode=alsaaudio.PCM_NONBLOCKING)
        else:
            self.pcm = alsaaudio.PCM(device=card_name, type=pcm_type)

        self.pcm.setchannels(int(self.channels))
        self.pcm.setrate(int(self.frame_rate))
        self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(int(self.buffer_size))

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
        if self.pcm:
            self.pcm.close()