import json
from collections import namedtuple


class Test:

    @staticmethod
    def load():
        print("asdsaaszdFgszdFsdaffdgh")
        with open("../threads/adidas/templates.json") as file:
            data = json.load(file)
            keys = list(data["urls"].keys())
            values = list(data["urls"].values())
            print(keys, values)
            return namedtuple("urls", keys)(*values)

    urls = load()


print(Test.urls.items)
