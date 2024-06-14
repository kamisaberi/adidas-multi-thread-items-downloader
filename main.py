import threading
from typing import Any
import adidas as ad
import sys
import time

# sys.stdout = open("logs/" + str(int(time.time())) + ".txt", "wt")


if __name__ == "__main__":
    ad.AdidasThread.Settings.load_settings()
    # print(ad.AdidasThread.Globals.assigned_items_indices)
    # exit(0)

    thread = ad.AdidasThread(0, ad.TYPES.GET_PREFERENCES, daemon=True)
    thread.start()
    thread.join()
    threads: [ad.AdidasThread] = []
    while True:
        if len(ad.AdidasThread.model_product_objects) < ad.AdidasThread.Globals.items_count:
            # if len(ad.AdidasThread.items) < ad.AdidasThread.Globals.items_count:
            # if threads.count(ad.TYPES.GET_ITEMS_LIST) < ad.AdidasThread.Globals.items_threads_count:
            cnt = threads.count({"thread_type": ad.TYPES.GET_ITEMS_LIST, "is_alive": True})
            print("CNT:", cnt)
            if cnt < ad.AdidasThread.Globals.items_threads_count:
                thread = ad.AdidasThread(len(threads) + 1, ad.TYPES.GET_ITEMS_LIST, daemon=True)
                thread.start()
                thread.join(0.1)
                threads.append(thread)
        if len(ad.AdidasThread.model_product_objects) > 0:
            cnt = threads.count({"thread_type": ad.TYPES.GET_REVIEWS, "is_alive": True})
            if cnt < ad.AdidasThread.Globals.items_threads_count:
                thread = ad.AdidasThread(len(threads) + 1, ad.TYPES.GET_REVIEWS, daemon=True)
                thread.start()
                thread.join(0.1)
                threads.append(thread)
    ad.AdidasThread.Settings.save_settings()
