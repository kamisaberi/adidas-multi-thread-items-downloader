class ItemInfo:

    def __init__(self, **kwargs):
        # print(dir(self))
        # print(getattr(self, "reviews_done"))
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattribute__(self, name):
        k = self.__dict__.setdefault(name)
        # print(name , k , end="\t\t")
        return k
