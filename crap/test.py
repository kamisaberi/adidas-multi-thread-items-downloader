from threads.base import ItemInfo
a1 = ItemInfo(order=1, done=True)
print(a1.order)
print(a1.reviews_done)
a2 = ItemInfo(order=1001 , reviews_count=1000)
print(a2.media_done)
# from foo import Foo
#
# f1 = Foo(first_name="ali")
# print(f1.first_name)
# print(f1.last_name)
# # print(dir(f1))
