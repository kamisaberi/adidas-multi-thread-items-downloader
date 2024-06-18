class Foo(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, name):
        # return super(Foo, self).__getattribute__(name)

        # print(name)
        return self.__dict__.setdefault(name)
