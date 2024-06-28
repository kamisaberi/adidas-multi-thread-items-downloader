import copy
import threading
import requests
import enum
import os
import json
from typing import Union, Any
from collections import namedtuple
from threads.base.types import ItemInfo
import preset
import time
import math

lock = threading.Lock()
items_should_update = threading.Event()
items_should_update.clear()


class TYPES(enum.Enum):
    NONE = 0
    CHECK_PREFERENCES = 1
    GET_ITEMS_LIST = 2
    GET_REVIEWS = 3
    DOWNLOAD_PRODUCT_MEDIA = 4
    CHECK_NEW_REVIEWS = 5


class Adidas(threading.Thread):
    items_should_update = threading.Event()

    items: list[dict] = list()
    items_info: dict[tuple[str, str]: ItemInfo] = dict()
    items_per_page: int = 0
    items_count: int = 0
    items_threads_count: int = 0
    reviews_threads_count: int = 0
    threads: list['Adidas'] = list()

    def __init__(self, thread_id, thread_type: TYPES, group=None, target=None, name=None, args=(), kwargs=None, *,
                 daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.thread_id: int = thread_id
        self.thread_type: TYPES = thread_type
        self.item_start: int = 0
        self.limit: int = 0

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

    def _create_params(self, sort=preset.SORT_NEWEST):
        params = copy.deepcopy(preset.TEMPLATES.params)
        params["start"] = self.item_start
        params["sort"] = sort
        return params

    def _sort_items_info_based_on_order(self) -> None:
        Adidas.items_info = dict(list(sorted(list(Adidas.items_info.items()), key=lambda item: item[1].order)))

    def _extract_orders_from_items_info(self) -> list[int]:
        self._sort_items_info_based_on_order()
        orders = [item.order for key, item in Adidas.items_info.items()]
        return sorted(orders)

    def _fill_items_info_with_bulk_data(self) -> None:
        items_info = copy.deepcopy(Adidas.items_info)
        for i in range(self.item_start, self.item_start + self.limit + 1):
            items_info[(f"M{i}", f"P{i}")] = ItemInfo(order=i)
        Adidas.items_info = items_info

    def _remove_bulk_data_from_items_info(self) -> None:
        items_info = copy.deepcopy(Adidas.items_info)
        for i in range(self.item_start, self.item_start + self.limit + 1):
            items_info.pop((f"M{i}", f"P{i}"))
        Adidas.items_info = items_info

    def _replace_bulk_using_data_in_items_info(self, items: list, reorder: bool = True) -> None:
        self._remove_bulk_data_from_items_info()
        items_info = copy.deepcopy(Adidas.items_info)
        for index, order in enumerate(list(range(self.item_start, self.item_start + self.limit + 1))):
            items_info.items_info.update({(items[index]["modelId"], items[index]["productId"]): ItemInfo(order=order)})

        Adidas.items_info = items_info
        if reorder:
            self._sort_items_info_based_on_order()

    def _get_next_start_point(self) -> (int, int):
        orders = self._extract_orders_from_items_info()
        if orders[0] != 0:
            return 0, orders[0] - 1
        try:
            for i, order in enumerate(orders):
                if orders[i] + 1 != orders[i + 1]:
                    return orders[i], orders[i + 1] - orders[i] - 1
        except:
            return orders[-1], Adidas.items_per_page

    def _download_items(self, url: str, headers: dict = None, sort=preset.SORT_NEWEST) -> (dict, dict):
        try:
            params = self._create_params()
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()["raw"]["itemList"]
            info = dict(list(data.items())[:6])
            return info, data["items"]
        except (requests.exceptions.RequestException, KeyError, ValueError):
            return None, None

    def _update_items_info_orders(self, count):
        for key in Adidas.items_info.keys():
            Adidas.items_info[key].order += count

    def _get_changed_items(self) -> (int, int, list[dict], dict[tuple[str, str]: ItemInfo]):
        if len(list(Adidas.items_info.keys())) == 0:
            info, items = self._download_items(preset.URLS.items, preset.TEMPLATES.headers)
            return -1, -1, items, None
        while True:
            info, items = self._download_items(preset.URLS.items, preset.TEMPLATES.headers)
            for new_index, item in enumerate(items):
                obj = (item["modelId"], item["productId"])
                if obj in list(Adidas.items_info.keys()):
                    gotten_index = list(Adidas.items_info.keys()).index(obj)
                    self.item_start = 0
                    return new_index, gotten_index, items[:new_index + 1], dict(
                        list(Adidas.items_info.items())[:gotten_index + 1])
                self.item_start += Adidas.items_per_page

    def _retrieve_preferences(self):
        new_index, gotten_index, new_items, removed_items = -1, -1, [], []
        while True:
            if not Adidas.items_should_update.is_set():
                new_index, gotten_index, new_items, removed_items = self._get_changed_items()
                if new_index != -1 or gotten_index != -1:
                    Adidas.items_should_update.set()
            if Adidas.items_should_update.is_set():
                while True:
                    if Adidas.threads.count({"is_alive": True}) != 0:
                        time.sleep(0.2)
                        continue
                    break

                with lock:
                    self._update_items_info_orders(new_index + 1)
                    Adidas.items_should_update.clear()

            time.sleep(preset.CHECK_PREFERENCES_INTERVAL)

    def _retrieve_items(self) -> bool:
        self.item_start, self.limit = self._get_next_start_point()

        # fill bulk data to items_info
        with lock:
            self._fill_items_info_with_bulk_data()

        info, items = self._download_items(preset.URLS.items, preset.TEMPLATES.headers)
        if info is None and items is None:
            with lock:
                self._remove_bulk_data_from_items_info()
            return False

        with lock:
            Adidas.items.extend(items)
            self._replace_bulk_using_data_in_items_info(items)
        print(self.thread_id, len(list(Adidas.items_info.keys())))
        return True

    def _download_reviews(self, model_id, limit, offset) -> dict | None:
        try:
            url = str.format(preset.URLS.reviews, model_id=model_id, limit=limit, offset=offset)
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
            res = self._download_reviews(model_id=model_id, limit=limit, offset=offset)
            if res is None or offset >= res["totalResults"]:
                break
            data["reviews"].extend(res["reviews"])
            offset += limit
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
            name, extension = link.split("/")[-1].split(".")
            with open(name + "." + extension, "wb") as f1:
                f1.write(response.content)

    def _check_reviews(self):
        while True:
            info, items = self._download_items(preset.URLS.items, preset.TEMPLATES.headers,
                                               sort=preset.SORT_TOP_SELLERS)

            time.sleep(preset.CHECK_PREFERENCES_INTERVAL)

    def run(self):
        print(self.thread_id, self.thread_type)
        match self.thread_type:
            case TYPES.CHECK_PREFERENCES:
                self._retrieve_preferences()
            case TYPES.GET_ITEMS_LIST:
                self._retrieve_items()
            case TYPES.GET_REVIEWS:
                self._retrieve_reviews(0, 0, 0)
            case TYPES.DOWNLOAD_PRODUCT_MEDIA:
                self._download_images(dict())
            case TYPES.CHECK_NEW_REVIEWS:
                self._check_reviews()

    class Settings:
        """
            Static Methods :
                load_settings :
                update_settings :
                save_settings :
        """

        @staticmethod
        def load_settings():
            with open(preset.PATHS.settings_file_path, "rt") as f1:
                settings = json.loads(f1.read())
                Adidas.items_per_page = settings["items_per_page"]
                Adidas.items_count = settings["items_count"]
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
            with open(preset.PATHS.settings_file_path, "wt") as f1:
                settings = {
                    "items_per_page": Adidas.items_per_page,
                    "items_count": Adidas.items_count,
                    "reminder_from_last_check": Adidas.reminder_from_last_check,
                    "assigned_items_indices": Adidas.assigned_items_indices
                }
                f1.write(json.dumps(settings))
