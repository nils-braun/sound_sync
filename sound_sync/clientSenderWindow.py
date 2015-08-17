__author__ = 'nilpferd'

import subprocess


class PactHelper:
    ALSA_CARD_NAME_PROPERTY_NAME = "alsa.card_name = "
    APPLICATION_NAME_PROPERTY_NAME = "application.name = "

    def __init__(self):
        self.sinks = dict()
        self.sink_inputs = dict()

        self.get_all_pulse_inputs()
        self.get_all_pulse_sinks()

    def get_all_pulse_sinks(self):
        sink_list_data = subprocess.check_output(["pactl", "list", "sinks"])
        sink_list_data = sink_list_data.splitlines()
        current_sink = 0
        self.sinks = dict()
        for line in sink_list_data:
            if line.startswith("\t"):
                if line.strip().startswith(self.ALSA_CARD_NAME_PROPERTY_NAME):
                    self.sinks[current_sink] = line.strip()[len(self.ALSA_CARD_NAME_PROPERTY_NAME):].strip('"')
            elif line.strip() is not "":
                current_sink += 1
                self.sinks[current_sink] = None

    def get_all_pulse_inputs(self):
        sink_list_data = subprocess.check_output(["pactl", "list", "sink-inputs"])
        sink_list_data = sink_list_data.splitlines()
        current_sink_input = 0
        self.sink_inputs = dict()
        for line in sink_list_data:
            if line.startswith("\t"):
                if line.strip().startswith(self.APPLICATION_NAME_PROPERTY_NAME):
                    self.sink_inputs[current_sink_input] = line.strip()[len(self.APPLICATION_NAME_PROPERTY_NAME):].strip('"')
            elif line.strip() is not "":
                current_sink_input += 1
                self.sink_inputs[current_sink_input] = ""

    def get_id_of_loopback_sink(self):
        id_of_loopback_sink = [x for (x, y) in self.sinks.items() if y == "Loopback"][0]
        return id_of_loopback_sink

pact = PactHelper()
print(pact.get_id_of_loopback_sink())
print(pact.sink_inputs)

#"pactl move-sink-input"
#"pactl list sink-inputs"
#"pactl list sinks"
