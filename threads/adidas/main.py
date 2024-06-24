import adidas as ad

import preset

if __name__ == "__main__":
    ad.Adidas.Settings.load_settings()
    # print(ad.AdidasThread.Globals.assigned_items_indices)
    # exit(0)
    thread = ad.Adidas(0, ad.TYPES.CHECK_PREFERENCES, daemon=True)
    thread.start()
    thread.join(preset.INITIAL_CHECK_PREFERENCES_DELAY)
    while True:

        if not ad.Adidas.items_should_update.is_set():
            if len(ad.Adidas.model_product_objects) < ad.Adidas.items_count:
                cnt = ad.Adidas.threads.count({"thread_type": ad.TYPES.GET_ITEMS_LIST, "is_alive": True})
                if cnt < ad.Adidas.items_threads_count:
                    thread = ad.Adidas(len(ad.Adidas.threads) + 1, ad.TYPES.GET_ITEMS_LIST, daemon=True)
                    thread.start()
                    thread.join(0.1)
                    ad.Adidas.threads.append(thread)
            if len(ad.Adidas.model_product_objects) > 0:
                cnt = ad.Adidas.threads.count({"thread_type": ad.TYPES.GET_REVIEWS, "is_alive": True})
                if cnt < ad.Adidas.items_threads_count:
                    thread = ad.Adidas(len(ad.Adidas.threads) + 1, ad.TYPES.GET_REVIEWS, daemon=True)
                    thread.start()
                    thread.join(0.1)
                    ad.Adidas.threads.append(thread)
