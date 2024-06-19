ms = {(12, 15), (2, 5), (2, 5), (12, 15), (8, 4), (9, 2), (6, 3)}
print(ms)

students = {
    ("ali", "rezaei"),
    ("reza", "alinia"),
    ("ali", "alinia"),
    ("reza", "rezaei"),
    ("ali", "rezaei"),
    ("ali", "alinia")
}

print(students)


class Student:
    name = ""
    family = ""

    def __init__(self, name, family):
        self.name = name
        self.family = family
        self.average = 15.5

    def say_hello(self):
        print("hello world")

    def test(self):
        print(dir(self))
        print(getattr(self, "name"))
        print(getattr(self, "average"))
        print(getattr(self, "age", None))
        print("-----------------")
        print(callable(getattr(self, "say_hello")))
        print(getattr(self, "say_hello"))
        print(getattr(self, "say_hello")())
        print("-----------------")


class Teacher:
    name = ""
    family = ""

    def __init__(self, name, family):
        self.name = name
        self.family = family
        self.average = 15.5

    def test(self):
        print(dir(self))
        print(getattr(self, "name"))
        print(getattr(self, "average"))
        print(getattr(self, "age", None))
        # for attr in dir(self):


s1 = Student("ali", "rezaei")
s2 = Student("ali", "rezaei")
t1 = Teacher("ali", "rezaei")
s1.test()
print(type(s1) == type(s2))
print(type(t1) == type(s2))
print(type(s1) is type(s2))
print(type(t1) is type(s2))
print(isinstance(s1, s2.__class__))
print(isinstance(t1, s2.__class__))
