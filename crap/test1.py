from collections import Counter, namedtuple

c = Counter(a=3, b=4, c=2)
d = Counter(b=1, d=2)
print(c)
print(list(c.elements()))
e = c + d
print(e)
ms = namedtuple("point", ["x", "y"])(3, 4)
print(ms)
print(ms[0])
print(ms.x)
ms.x = 5
