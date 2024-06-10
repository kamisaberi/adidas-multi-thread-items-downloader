import threading
import requests
import time
import enum
import os
import json
import sys

product_ids = []

is_p_threads_done = False

# lock = threading.Lock()

should_load_settings = threading.Event()
should_load_settings.set()
should_update_settings = threading.Event()
should_update_settings.clear()



class TYPES(enum.Enum):
    NONE = 0
    GET_ITEMS_LIST = 1
    GET_REVIEWS = 2


class AdidasThread(threading.Thread):
    id: int = 0
    type: TYPES = TYPES.NONE
    products_data: list[dict] = []
    # board : list[list[Piece]] = []

    # STATIC PROPERTIES
    items: list[dict] = []
    model_product_objects: list[tuple[str, str]] = list()

    def __init__(self, id, type, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.id = id
        self.type = type
        # self.model_product_objects = list()

    def read_file_contents(self, file_name):
        with threading.Lock():
            with open(str(self.id) + file_name, "r") as f:
                file_contents = json.loads(f.read())
                f.close()
            return file_contents

    def save_data(self, data, file_name):
        loaded = {
            "items": []
        }
        if os.path.exists(file_name):
            file_contents = self.read_file_contents(file_name)
            loaded["items"].extend(file_contents["items"])
        loaded["items"].append(data)
        with threading.Lock:
            with open(str(self.id) + file_name, "w") as f:
                json.dump(loaded, f)
        return

    def paginate_reviews(self, product_id, model_id, limit=5, offset=0):
        while True:
            url = str.format(AdidasThread.Globals.reviews_url, model_id=model_id, limit=limit, offset=offset)
            response = requests.get(url)
            if response is None or "totalResults" not in (res := response.json()):
                break
            if offset >= res["totalResults"]:
                break
            data = {"reviews": res["reviews"], "product_id": product_id}
            self.save_data(data, "reviews.json")
            offset += limit
        return

    def get_reviews(self):
        for model, product in self.model_product_objects:
            self.paginate_reviews(product_id=product, model_id=model)

    def retrieve_items(self):
        if should_load_settings.is_set():
            # print("CHECK")
            AdidasThread.Globals.params["start"] = AdidasThread.Settings.start_from
            should_load_settings.clear()
            should_update_settings.set()
        else:
            AdidasThread.Globals.params["start"] = AdidasThread.Globals.last_start_point
            print("START:", AdidasThread.Globals.params["start"])
            # print("START FROM :", AdidasThread.Globals.params["start"])
        response = requests.get(
            AdidasThread.Globals.items_url,
            headers=AdidasThread.Globals.headers,
            params=AdidasThread.Globals.params)
        if response is None or response.status_code != 200:
            return
        response_json = response.json()
        try:
            products = response_json["raw"]["itemList"]["items"]
        except KeyError:
            return
        data = response_json["raw"]["itemList"]
        if should_update_settings.is_set():
            AdidasThread.Settings.update_settings(data)
            should_update_settings.clear()
        AdidasThread.Globals.last_start_point += data["viewSize"]
        # print(AdidasThread.items)
        AdidasThread.items.extend(data["items"])
        # print(AdidasThread.items)

        # with threading.Lock():
        for product in products:
            AdidasThread.model_product_objects.append((product["modelId"], product["productId"]))

        #     with open(
        #             os.path.join(
        #                 AdidasThread.Globals.product_files_path,
        #                 AdidasThread.Globals.product_file_name_prefix + str(self.id) + ".json"), "wt") as f1:
        #         f1.write(json.dumps(AdidasThread.items))

        print(self.id, ":", len(AdidasThread.model_product_objects), len(set(AdidasThread.model_product_objects)))

        # self.save_data(AdidasThread.products_data, file_name="products.json")

    def run(self):
        print(self.id, self.type)
        if self.type == TYPES.GET_ITEMS_LIST:
            self.retrieve_items()
        if self.type == TYPES.GET_REVIEWS:
            self.paginate_reviews(0, 0, 0)

    class Globals:
        last_start_point: int = 0
        settings_file_path: str = "files/settings.json"
        product_file_name_prefix: str = "pr-"
        product_files_path: str = "files"
        params: dict = {
            'query': 'all',
            "start": 0,
            "sort": "newest-to-oldest"
        }
        headers: dict = {
            'authority': 'www.adidas.at',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
            'content-type': 'application/json',
            'user-agent': 'PostmanRuntime/7.35.0',
        }
        items_url: str = "https://www.adidas.at/api/plp/content-engine/search?"
        reviews_url: str = "https://www.adidas.at/api/models/{model_id}/reviews?bazaarVoiceLocale=de_AT&feature&includeLocales=de%2A&limit={limit}&offset={offset}&sort=newest"

    class Settings:
        items_per_page = 0
        items_count = 0
        start_from = 0
        reminder_from_last_check = 0

        @staticmethod
        def load_settings():
            with open(AdidasThread.Globals.settings_file_path, "rt") as f1:
                settings = json.loads(f1.read())
                AdidasThread.Settings.items_per_page = settings["items_per_page"]
                AdidasThread.Settings.items_count = settings["items_count"]
                AdidasThread.Settings.start_from = settings["start_from"]
                AdidasThread.Settings.reminder_from_last_check = settings["reminder_from_last_check"]

        @staticmethod
        def update_settings(data):
            AdidasThread.Settings.items_count = data["count"]
            AdidasThread.Settings.reminder_from_last_check = data["count"] - AdidasThread.Settings.items_count
            AdidasThread.Settings.items_per_page = data["viewSize"]
            # AdidasThread.Settings.start_from += data["viewSize"]

        @staticmethod
        def save_settings():
            with open(AdidasThread.Globals.settings_file_path, "wt") as f1:
                settings = {
                    "start_from": AdidasThread.Settings.start_from,
                    "items_per_page": AdidasThread.Settings.items_per_page,
                    "items_count": AdidasThread.Settings.items_count,
                    "reminder_from_last_check": AdidasThread.Settings.reminder_from_last_check
                }
                f1.write(json.dumps(settings))
