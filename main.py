import threading

import adidas as ad
import sys
import time

if __name__ == "__main__":
    ad.AdidasThread.Settings.load_settings()
    threads: [threading.Thread] = []
    while True:
        thread1 = ad.AdidasThread(threading.active_count(), ad.TYPES.GET_ITEMS_LIST)
        thread1.start()
        thread1.join(0.1)

    ad.AdidasThread.Settings.save_settings()
