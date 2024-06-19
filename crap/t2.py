from collections import namedtuple

r1 = namedtuple("Rectangle", ["width", "length", "items"])(3, 4, list())
print(r1[0], r1.width)
r1.items.append(15)


class Human:
    name: str = ""
    family: str = ""
    items: list = None

    def __new__(cls):
        Human.items = []
        return super().__new__(cls)


Human.items.append("ali")
