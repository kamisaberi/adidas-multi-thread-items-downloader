from collections import namedtuple

r1 = namedtuple("Rectangle", ["width", "length"])(3, 4)
print(r1[0], r1.width)
r1.width = 5
