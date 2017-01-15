from sound_sync.console_applications import listener, sender, server

from multiprocessing import Pool

from sound_sync.timing.time_utils import sleep

if __name__ == '__main__':
    with Pool(3) as pool:
        pool.apply_async(server.main)
        sleep(0.1)
        pool.apply_async(sender.main)
        sleep(0.1)
        pool.apply_async(listener.main)

        pool.close()
        pool.join()