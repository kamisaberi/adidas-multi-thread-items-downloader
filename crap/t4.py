class Student:
    family = "rezaei"

    def __init__(self):
        self.name = "ali"

    def print_data(self):
        print(self.name)
        print(self.family)

    @classmethod
    def print_data2(cls):
        print(cls.family)


s1 = Student()
s1.print_data()
s1.print_data2()
