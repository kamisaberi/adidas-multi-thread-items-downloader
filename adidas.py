import threading
import requests
import time
import enum
import os
import json
import sys

# headers = {
#     'authority': 'www.adidas.com',
#     'accept': '*/*',
#     # 'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
#     'content-type': 'application/json',
#     'user-agent': 'PostmanRuntime/7.35.0',
# }

product_ids = []

is_p_threads_done = False
lock = threading.Lock()


def print_progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + ('░' * (100 - int(percent)))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")


class TYPES(enum.Enum):
    NONE = 0
    PRODUCTS = 1
    REVIEWS = 2
    ITEM_LIST = 3
    PAGES = 4


class AdidasThread(threading.Thread):
    t_id = 0
    type = TYPES.NONE
    products_data = []
    pages = []

    model_product_objects = []

    # STATIC PROPERTIES
    item_list = []
    items_per_page = 0
    items_count = 0
    start_from = 0
    params = {
        'query': 'all',
        "start": start_from
    }
    headers = {
        'authority': 'www.adidas.at',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'content-type': 'application/json',
        'user-agent': 'PostmanRuntime/7.35.0',
    }
    items_url = "https://www.adidas.at/api/plp/content-engine/search?"

    def __init__(self, t_id, t_type, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.t_id = t_id
        self.type = t_type
        self.pages = []
        self.model_product_objects = []

    def read_file_contents(self, file_name):
        with lock:
            with open(str(self.t_id) + file_name, "r") as f:
                file_contents = json.loads(f.read())
                f.close()
            return file_contents

    # hesamiks

    def save_data(self, data, file_name):
        loaded = {
            "items": []
        }
        if os.path.exists(file_name):
            file_contents = self.read_file_contents(file_name)
            loaded["items"].extend(file_contents["items"])
        loaded["items"].append(data)
        with lock:
            with open(str(self.t_id) + file_name, "w") as f:
                json.dump(loaded, f)
        return

    def is_id_exist(self, item_id):
        if item_id not in product_ids:
            product_ids.append(item_id)
            return False
        return True

    @staticmethod
    def request_to_url(url, params=None):
        try:
            response = requests.get(url, headers=AdidasThread.headers, params=params)
            if response.status_code != 200:
                return
            return response
        except Exception as e:
            # print(f"error {url} is {e}")
            return

    # hesamiks

    def paginate_reviews(self, product_id, model_id, limit=5, offset=0):
        first_part = "https://www.adidas.at/api/models/"
        second_part = "/reviews?bazaarVoiceLocale=de_AT&feature&includeLocales=de%2A&limit="
        while True:
            url = f"{first_part}{model_id}{second_part}{limit}&offset={offset}&sort=newest"
            response = AdidasThread.request_to_url(url)
            if response is None:
                break
            if "totalResults" not in list(response.json().keys()):
                # print(f"this product with id {product_id} does not have totalResults")
                break
            else:
                if offset >= response.json()["totalResults"]:
                    break
                else:
                    data = {"reviews": response.json()["reviews"], "product_id": product_id}
                    self.save_data(data, "reviews.json")
                    offset += limit

        return

    # hesamiks

    @staticmethod
    def set_pages_item_list():

        response = AdidasThread.request_to_url(AdidasThread.items_url, params=AdidasThread.params)
        if response is None:
            AdidasThread.set_pages_item_list()

        response_json = response.json()
        if "raw" not in list(response_json.keys()):
            return
        if "itemList" not in list(response_json["raw"].keys()):
            return

        AdidasThread.item_list = response_json["raw"]["itemList"]
        # with (f1 := open("files/item_list.json", "wt")):
        #     f1.write(json.dumps(AdidasThread.item_list))
        # return response_json["raw"]["itemList"]

    @staticmethod
    def set_pages():
        # print(AdidasThread.item_list)
        item_list = AdidasThread.item_list
        pages_count = item_list["count"] // item_list["viewSize"]
        pages = [i for i in range(1, pages_count + 1)]
        AdidasThread.pages = pages

    def get_products_reviews(self):
        # total = AdidasThread.item_list["count"]
        # print_progress_bar(params["start"], total)
        print("man injammmamamamamammamamama")
        print(self.model_product_objects)
        print("ibjjaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        for item in self.model_product_objects:
            print(self.t_id, item)
            # self.paginate_reviews(product_id=item["product_id"], model_id=item["model_id"])

    # hesamiks

    def get_products(self, params):
        # total = AdidasThread.item_list["count"]
        # print_progress_bar(params["start"], total)

        params = {
            'query': 'all',
            "start": (self.t_id - 1) * 48
        }

        response = AdidasThread.request_to_url(AdidasThread.items_url, params=params)
        # with (f1 := open("files/products.json", "wt")):
        #     f1.write(json.dumps(response.json()))

        if response is None:
            return
        response_json = response.json()
        # TODO: (type error check,  try except)
        try:
            products = response_json["raw"]["itemList"]["items"]
        except KeyError:
            return
            # if "raw" not in list(response_json.keys()):
        #     return
        # if "itemList" not in list(response_json["raw"].keys()):
        #     return
        # if "items" not in list(response_json["raw"]["itemList"].keys()):
        #     return

        # products = response_json["raw"]["itemList"]["items"]

        for product in products:
            # if self.is_id_exist(product) == False:
            obj = {
                "product_id": product["productId"],
                "model_id": product["modelId"]
            }
            self.model_product_objects.append(obj)
            # inja inj ai janadfsdfdsh
            # print(self.model_product_objects)
            self.save_data(AdidasThread.products_data, file_name="products.json")

    def generate_products_url(self):
        print(self.t_id)
        params = {
            'query': 'all',
            "start": (self.t_id - 1) * 48
        }
        self.get_products(params)
        # print(params)

    def run(self):
        if self.type == TYPES.ITEM_LIST:
            AdidasThread.set_pages_item_list()

        if self.type == TYPES.PRODUCTS:
            if is_p_threads_done == False and len(AdidasThread.item_list) != 0:
                self.generate_products_url()

        if self.type == TYPES.REVIEWS:
            self.get_products_reviews()

        if self.type == TYPES.PAGES:
            AdidasThread.set_pages()
