from collections import namedtuple
from typing import  NamedTuple

p1:NamedTuple = NamedTuple("Point", [("x", int), ("y", int)])(3, 4)
print(p1)
print(p1.x)
p1 = p1._replace(x=5)
print(p1)


Point = NamedTuple("Point", [('x', int), ('y', int)])