import adidas as ad
import sys
import time

if __name__ == "__main__":
    ad.AdidasThread.Settings.load_settings()
    # while True:
    #     pass
    #
    # i = 1
    # while True:
    thread1 = ad.AdidasThread(1, ad.TYPES.GET_ITEMS_LIST)
    thread1.start()
    thread1.join()
    # time.sleep(10)

    # thread2 = ad.AdidasThread(2, ad.TYPES.GET_REVIEWS)
    # thread2.start()
    # thread2.join()
    # thread.join()
    # i += 1

    ad.AdidasThread.Settings.save_settings()
