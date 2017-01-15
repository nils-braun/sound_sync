import argparse

from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.listener.base_listener import BaseListener


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
                        help="Port of the listen to on the server. Default 8888.",
                        dest="port")
    parser.add_argument("-c", "--channel_hash",
                        default="1",
                        type=str,
                        help="Channel hash to listen to.",
                        dest="channel_hash")
    args = parser.parse_args()

    listener = BaseListener(args.hostname, args.port, args.channel_hash)
    listener.player = PCMPlay()
    listener.initialize()

    try:
        listener.main_loop()
    finally:
        listener.terminate()


if __name__ == "__main__":
    main()
