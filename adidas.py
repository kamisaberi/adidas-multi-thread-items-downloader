import threading
import requests
import time
import enum
import os
import json
import sys
from typing import Union

product_ids = []

is_p_threads_done = False


# lock = threading.Lock()


class TYPES(enum.Enum):
    NONE = 0
    GET_PREFERENCES = 1
    GET_ITEMS_LIST = 2
    GET_REVIEWS = 3
    DOWNLOAD_PRODUCT_MEDIA = 4


class AdidasThread(threading.Thread):
    """
        Instance Members:
            thread_id: int = 0
            thread_type: TYPES = TYPES.NONE
            products_data: list[dict] = []
            item_start = 0
            item_end = 0
        Static Members :
            items: list[dict] = []
            model_product_objects: list[tuple[str, str]] = list()
    """
    thread_id: int = 0
    thread_type: TYPES = TYPES.NONE
    products_data: list[dict] = list()
    item_start: int = 0
    item_end: int = 0

    # STATIC PROPERTIES
    items: list[dict] = list()
    model_product_objects: set[tuple[str, str]] = set()

    class Events:
        """
            Static Members :
                should_load_settings :
                should_update_settings :
        """
        # Static Members
        should_load_settings = threading.Event()
        should_load_settings.set()
        should_update_settings = threading.Event()
        should_update_settings.clear()

    class Globals:
        """
            Static Members:
                next_start_point:
                settings_file_path:
                product_file_name_prefix:
                product_files_path:
                gotten_items_list:
                params:
                headers:
                items_url:
                reviews_url:
                items_per_page:
                items_count:
                start_from:
                reminder_from_last_check:
                items_threads_count:
                reviews_threads_count:
        """
        next_start_point: int = 0
        settings_file_path: str = "files/settings.json"
        product_file_name_prefix: str = "pr-"
        product_files_path: str = "files"
        assigned_items_indices: list[tuple[int, int]] = list()
        # gotten_items_list: list[dict[tuple[int, int]: int]] = list()
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

        # Moved from Settings class
        items_per_page: int = 0
        items_count: int = 0
        start_from: int = 0
        reminder_from_last_check: int = 0
        items_threads_count: int = 0
        reviews_threads_count: int = 0

    def __init__(self, thread_id, thread_type, group=None, target=None, name=None, args=(), kwargs=None, *,
                 daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.thread_id = thread_id
        self.thread_type = thread_type

        # self.model_product_objects = list()

    def __eq__(self, other: Union['AdidasThread', TYPES, dict]):
        if isinstance(other, enum.Enum):
            return self.thread_type == other
        elif isinstance(other, AdidasThread):
            return self.thread_type == other.thread_type
        elif isinstance(other, dict):
            for key, value in other.items():
                v = getattr(self, key, None)
                if v is None:
                    return False
                if not callable(v) and (type(v) is not type(value) or v != value):
                    return False
                if callable(v) and v() != value:
                    return False
            return True
        return False

    def __hash__(self):
        return hash(self.thread_type)

    def _retrieve_preferences(self):
        if AdidasThread.Events.should_load_settings.is_set():
            AdidasThread.Events.should_load_settings.clear()
            AdidasThread.Events.should_update_settings.set()
        AdidasThread.Globals.params["start"] = 0
        response = requests.get(
            AdidasThread.Globals.items_url,
            headers=AdidasThread.Globals.headers,
            params=AdidasThread.Globals.params)
        if response is None or response.status_code != 200:
            return
        try:
            AdidasThread.Settings.update_settings(response.json()["raw"]["itemList"])
        except:
            return

    def _retrieve_items(self):
        self.item_start = AdidasThread.Globals.next_start_point
        self.item_end = min(AdidasThread.Globals.next_start_point + AdidasThread.Globals.items_per_page,
                            AdidasThread.Globals.items_count)
        AdidasThread.Globals.params["start"] = self.item_start
        AdidasThread.Globals.assigned_items_indices.append((self.item_start, self.item_end))
        AdidasThread.Globals.next_start_point += AdidasThread.Globals.items_per_page
        # print(AdidasThread.Globals.gotten_items_list)

        response = requests.get(AdidasThread.Globals.items_url,
                                headers=AdidasThread.Globals.headers,
                                params=AdidasThread.Globals.params)
        if response is None or response.status_code != 200:
            AdidasThread.Globals.assigned_items_indices.remove((self.item_start, self.item_end))
            # TODO needs to revert next_start_point
            return
        response_json = response.json()
        try:
            products = response_json["raw"]["itemList"]["items"]
        except KeyError:
            AdidasThread.Globals.assigned_items_indices.remove((self.item_start, self.item_end))
            # TODO needs to revert last_start_point
            return
        data = response_json["raw"]["itemList"]
        if AdidasThread.Events.should_update_settings.is_set():
            AdidasThread.Settings.update_settings(data)
            AdidasThread.Events.should_update_settings.clear()
        AdidasThread.Globals.next_start_point += data["viewSize"]
        # print(AdidasThread.items)
        AdidasThread.items.extend(data["items"])
        # print(AdidasThread.items)

        with threading.Lock():
            AdidasThread.model_product_objects.update(
                [(product["modelId"], product["productId"]) for product in products]
            )

        #     with open(
        #             os.path.join(
        #                 AdidasThread.Globals.product_files_path,
        #                 AdidasThread.Globals.product_file_name_prefix + str(self.id) + ".json"), "wt") as f1:
        #         f1.write(json.dumps(AdidasThread.items))

        print(self.thread_id, ":", len(AdidasThread.model_product_objects),
              len(set(AdidasThread.model_product_objects)))

        # self.save_data(AdidasThread.products_data, file_name="products.json")

    def _paginate_reviews(self, product_id, model_id, limit=5, offset=0):
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

    def _get_reviews(self):
        for model, product in self.model_product_objects:
            self._paginate_reviews(product_id=product, model_id=model)

    def _download_images(self, item_data: dict):
        pass

    def read_file_contents(self, file_name):
        with threading.Lock():
            with open(str(self.thread_id) + file_name, "r") as f:
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
            with open(str(self.thread_id) + file_name, "w") as f:
                json.dump(loaded, f)
        return

    def run(self):
        print(self.thread_id, self.thread_type)
        match self.thread_type:
            case TYPES.GET_PREFERENCES:
                self._retrieve_preferences()
            case TYPES.GET_ITEMS_LIST:
                self._retrieve_items()
            case TYPES.GET_REVIEWS:
                self._paginate_reviews(0, 0, 0)
            case TYPES.DOWNLOAD_PRODUCT_MEDIA:
                self._download_images(dict())

    class Settings:
        """
            Static Methods :
                load_settings :
                update_settings :
                save_settings :
        """

        @staticmethod
        def load_settings():
            with open(AdidasThread.Globals.settings_file_path, "rt") as f1:
                settings = json.loads(f1.read())
                AdidasThread.Globals.items_per_page = settings["items_per_page"]
                AdidasThread.Globals.items_count = settings["items_count"]
                AdidasThread.Globals.start_from = settings["start_from"]
                AdidasThread.Globals.reminder_from_last_check = settings["reminder_from_last_check"]
                AdidasThread.Globals.items_threads_count = settings["items_threads_count"]
                AdidasThread.Globals.reviews_threads_count = settings["reviews_threads_count"]
                AdidasThread.Globals.assigned_items_indices = [tuple(pair) for pair in
                                                               settings["assigned_items_indices"]]

        @staticmethod
        def update_settings(data):
            AdidasThread.Globals.items_count = data["count"]
            AdidasThread.Globals.reminder_from_last_check = data["count"] - AdidasThread.Globals.items_count
            AdidasThread.Globals.items_per_page = data["viewSize"]
            # AdidasThread.Globals.start_from += data["viewSize"]

        @staticmethod
        def save_settings():
            with open(AdidasThread.Globals.settings_file_path, "wt") as f1:
                settings = {
                    "start_from": AdidasThread.Globals.start_from,
                    "items_per_page": AdidasThread.Globals.items_per_page,
                    "items_count": AdidasThread.Globals.items_count,
                    "reminder_from_last_check": AdidasThread.Globals.reminder_from_last_check,
                    "assigned_items_indices": AdidasThread.Globals.assigned_items_indices
                }
                f1.write(json.dumps(settings))
