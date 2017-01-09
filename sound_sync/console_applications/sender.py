import argparse

from sound_sync.audio.pcm.record import PCMRecorder
from sound_sync.clients.base_sender import BaseSender


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--hostname",
                        default="localhost",
                        type=str,
                        help="Hostname of the management server.",
                        dest="hostname")
    parser.add_argument("-p", "--port",
                        default=8888,
                        type=int,
                        help="Port to send to on the server. Default 8887.",
                        dest="port")
    parser.add_argument("--hash",
                        default="1",
                        type=str,
                        help="Hash value. TODO",
                        dest="hash")
    parser.add_argument("-n", "--name",
                        default="Untitled",
                        type=str,
                        help="Name of this channel in the channel list. Default Untitled.",
                        dest="name")
    parser.add_argument("-d", "--description",
                        default="No Description",
                        type=str,
                        help="Description of this channel in the channel list. Default No Description.",
                        dest="description")

    args = parser.parse_args()
    sender = BaseSender(args.hostname, args.port, args.hash)
    sender.recorder = PCMRecorder()
    sender.name = args.name
    sender.description = args.description
    sender.initialize()
    try:
        sender.main_loop()
    finally:
        sender.terminate()


if __name__ == "__main__":
    main()
