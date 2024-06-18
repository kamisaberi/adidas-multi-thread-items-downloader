class Foo(object):
    def __getattr__(self, name):
        # return super(Foo, self).__getattribute__(name)

        # print(name)
        return self.__dict__.setdefault(name)