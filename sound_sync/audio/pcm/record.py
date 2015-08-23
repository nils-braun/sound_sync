from sound_sync.audio.sound_device import SoundRecorder
import alsaaudio


class PCMRecorder(SoundRecorder):
    def __init__(self):
        SoundRecorder.__init__(self)
        self.card_name = "hw:Loopback,1,0"
        self.pcm = None

    def initialize(self):
        """
        Set the PCM device with the usual parameters.
        """
        if self.pcm is not None:
            return

        self.assert_loopback_device()

        self.pcm = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, device=self.card_name)

        self.pcm.setchannels(int(self.channels))
        self.pcm.setrate(int(self.frame_rate))
        self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(int(self.buffer_size))

    @staticmethod
    def assert_loopback_device():

        card_list = alsaaudio.cards()
        if "Loopback" not in card_list:
            raise ValueError("There is no Loopback module loaded by ALSA. Loopback is needed by the program. " +
                             "Try loading it via modprobe or add it to /etc/modules or to a file in /etc/modules.d/.")

    def terminate(self):
        if self.pcm:
            self.pcm.close()

    def get(self):
        if self.pcm is None:
            raise ValueError("Recorder needs to be initialized first")

        length, sound_buffer = self.pcm.read()
        return sound_buffer, length