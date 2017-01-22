from sound_sync.console_applications import listener, sender, server

from multiprocessing import Pool

from sound_sync.timing.time_utils import sleep
from multiprocessing.context import TimeoutError

if __name__ == '__main__':
    results = []
    with Pool(3) as pool:
        results.append(pool.apply_async(server.main))
        sleep(0.1)
        results.append(pool.apply_async(sender.main))
        sleep(0.1)
        results.append(pool.apply_async(listener.main))

        pool.close()

        while True:
            for result in results:
                try:
                    result.get(timeout=0)
                except TimeoutError:
                    pass

            sleep(0.1)

        pool.join()