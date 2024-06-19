import json
from collections import namedtuple


class Test:

    @staticmethod
    def load():
        print("asdsaaszdFgszdFsdaffdgh")
        with open("../threads/adidas/templates.json") as file:
            data = json.load(file)
            return namedtuple("urls", list(data["urls"].keys()))(list(data["urls"].values()))

    urls = load()

print(Test.urls["items"])
