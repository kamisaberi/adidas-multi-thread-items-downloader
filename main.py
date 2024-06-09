import threading
from typing import Any

import adidas as ad
import sys
import time

if __name__ == "__main__":
    ad.AdidasThread.Settings.load_settings()
    threads: [threading.Thread] = []
    while True:
        if len(ad.AdidasThread.items) < ad.AdidasThread.Settings.items_count:
            thread = ad.AdidasThread(len(threads) + 1, ad.TYPES.GET_ITEMS_LIST)
            thread.start()
            thread.join(0.1)
            threads.append(thread)
        if len(ad.AdidasThread.model_product_objects) > 0:
            thread = ad.AdidasThread(len(threads) + 1, ad.TYPES.GET_REVIEWS)
            thread.start()
            thread.join(0.1)
            threads.append(thread)

    ad.AdidasThread.Settings.save_settings()
