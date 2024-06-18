import threading
import requests
import time
import enum
import os
import json
import sys
from typing import Union, Dict, List, Any, NamedTuple
from collections import namedtuple
from types import ItemInfo


class TYPES(enum.Enum):
    NONE = 0
    GET_PREFERENCES = 1
    GET_ITEMS_LIST = 2
    GET_REVIEWS = 3
    DOWNLOAD_PRODUCT_MEDIA = 4


class Adidas(threading.Thread):
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

    @staticmethod
    def load_templates():
        with open("prefs/templates.json") as file:
            data = json.load(file)
            named_tuples = []
            for key, value in data.items():
                nt = namedtuple("urls", list(value.keys()))(*list(value.values()))
                named_tuples.append(nt)
            return named_tuples

    @staticmethod
    def initialize_events():
        should_load_settings = threading.Event()
        should_load_settings.set()
        should_update_settings = threading.Event()
        should_update_settings.clear()
        return (namedtuple("events", ["should_load_settings", "should_update_settings"])
                (should_load_settings, should_update_settings))

    @staticmethod
    def initialize_items_info():

        return NamedTuple("items_info",
                          [("next_start_point", int),
                           ("items", dict[tuple[str, str]: ItemInfo]),
                           ("model_product_objects", list[tuple[str, str]]),
                           ("assigned_items_indices", list[tuple[int, int]])])(
            0, dict(), list(), list())

    # STATIC PROPERTIES
    events: namedtuple = initialize_events()
    urls, paths, templates = load_templates()

    items: list[dict] = list()
    model_product_objects: list[tuple[str, str]] = list()
    next_start_point: int = 0
    assigned_items_indices: list[tuple[int, int]] = list()
    items_info: NamedTuple = initialize_items_info()
    # assigned_items_indices: list[dict[tuple[int, int]: int]] = list()
    items_per_page: int = 0
    items_count: int = 0
    reminder_from_last_check: int = 0
    items_threads_count: int = 0
    reviews_threads_count: int = 0

    def __init__(self, thread_id, thread_type, group=None, target=None, name=None, args=(), kwargs=None, *,
                 daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.thread_id = thread_id
        self.thread_type = thread_type
        self.item_start: int = 0
        self.item_end: int = 0

    def __eq__(self, other: Union['Adidas', TYPES, dict]):
        if isinstance(other, enum.Enum):
            return self.thread_type == other
        elif isinstance(other, Adidas):
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

    def _download_items(self, url: str, headers: dict = None, params: dict = None) -> (dict, dict):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()["raw"]["itemList"]
            info = dict(list(data.items())[:6])
            return info, data["items"]
        except (requests.exceptions.RequestException, KeyError, ValueError):
            return None, None

    def _retrieve_preferences(self):
        if self.events.should_load_settings.is_set():
            self.events.should_load_settings.clear()
            self.events.should_update_settings.set()

        self.templates.params["start"] = 0
        preset, items = self._download_items(self.urls.items, self.templates.headers, self.templates.params)
        Adidas.assigned_items_indices = Helper.update_items_count(Adidas.model_product_objects,
                                                                  Adidas.assigned_items_indices, items)

    def _retrieve_items(self) -> bool:
        self.item_start = Adidas.next_start_point
        self.item_end = min(Adidas.next_start_point + Adidas.items_per_page, Adidas.items_count)
        Adidas.templates.params["start"] = self.item_start
        Adidas.assigned_items_indices.append((self.item_start, self.item_end))
        Adidas.next_start_point += Adidas.items_per_page
        # print(AdidasThread.Globals.gotten_items_list)

        preset, items = self._download_items(self.urls.items, self.templates.headers, self.templates.params)
        if preset is None and items is None:
            Adidas.assigned_items_indices.remove((self.item_start, self.item_end))
            # TODO BUG-#10
            return False

        if Adidas.events.should_update_settings.is_set():
            Adidas.Settings.update_settings(preset)
            Adidas.events.should_update_settings.clear()

        Adidas.next_start_point += preset["viewSize"]
        Adidas.items.extend(items)

        with threading.Lock():
            Adidas.model_product_objects.extend([(product["modelId"], product["productId"]) for product in items])

        print(self.thread_id, len(Adidas.model_product_objects), len(set(Adidas.model_product_objects)))
        return True

    def _download_reviews(self, url: str) -> dict | None:
        try:
            response = requests.get(url)
            response.raise_for_status()
            if response is None or "totalResults" not in response.json():
                return None
            return response.json()
        except (requests.exceptions.RequestException, ValueError, KeyError):
            return None

    def _retrieve_reviews(self, product_id, model_id, limit=5, offset=0) -> dict[str, list[Any] | Any]:
        data = {"product_id": product_id, "reviews": []}
        while True:
            url = str.format(Adidas.urls.reviews, model_id=model_id, limit=limit, offset=offset)
            res = self._download_reviews(url)
            if res is None or offset >= res["totalResults"]:
                break
            data["reviews"].extend(res["reviews"])
            offset += limit

        # self.save_data(data, "reviews.json")
        return data

    def _get_links(self, item_data: dict) -> list[str]:
        links = [item_data["image"]["src"], item_data["secondaryImage"]["src"]]
        for image in item_data["image"]:
            links.append(image["src"])
        return links

    def _download_images(self, item_data: dict):
        links = self._get_links(item_data)
        for link in links:
            response = requests.get(link)
            name, extension = link.splite("/")[-1].split(".")
            with open(name + "." + extension, "wb") as f1:
                f1.write(response.content)

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
                self._retrieve_reviews(0, 0, 0)
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
        with open(Adidas.paths.settings_file_path, "rt") as f1:
            settings = json.loads(f1.read())
            Adidas.items_per_page = settings["items_per_page"]
            Adidas.items_count = settings["items_count"]
            Adidas.next_start_point = settings["start_from"]
            Adidas.reminder_from_last_check = settings["reminder_from_last_check"]
            Adidas.items_threads_count = settings["items_threads_count"]
            Adidas.reviews_threads_count = settings["reviews_threads_count"]
            Adidas.assigned_items_indices = [tuple(pair) for pair in settings["assigned_items_indices"]]

    @staticmethod
    def update_settings(data):
        Adidas.items_count = data["count"]
        Adidas.reminder_from_last_check = data["count"] - Adidas.items_count
        Adidas.items_per_page = data["viewSize"]
        # AdidasThread.Globals.start_from += data["viewSize"]

    @staticmethod
    def save_settings():
        with open(Adidas.paths.settings_file_path, "wt") as f1:
            settings = {
                "items_per_page": Adidas.items_per_page,
                "items_count": Adidas.items_count,
                "reminder_from_last_check": Adidas.reminder_from_last_check,
                "assigned_items_indices": Adidas.assigned_items_indices
            }
            f1.write(json.dumps(settings))


class Helper:
    @staticmethod
    def update_items_count(model_product_objects, assigned_items_indices, new_items):
        """
        TODO update assigned_items_indices values using reminder
        :param model_product_objects:
        :param new_items:
        :param assigned_items_indices:
        :return:
        """
        # TODO first i should check , i need to get new reminder or not  ??????
        if (reminder := Helper._get_reminder_count(model_product_objects, new_items)) != -1:
            for i in range(len(assigned_items_indices)):
                assigned_items_indices[i] = (
                    assigned_items_indices[i][0] + reminder, assigned_items_indices[i][1] + reminder)

        return assigned_items_indices

    @staticmethod
    def _get_reminder_count(model_product_objects: list, new_items: list) -> int:
        """
            TODO should find which of downloaded item from model_product_objects
            TODO is in new items and calculate the differences number
        :param model_product_objects:
        :param new_items:
        :return:
        """
        for new_item in new_items:
            obj = (new_item["modelId"], new_item["productId"])
            if obj in model_product_objects:
                ind = model_product_objects.index(obj)
                return ind
        return -1
