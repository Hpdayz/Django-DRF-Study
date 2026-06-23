class MyType(type):
    def __new__(cls, name, bases, attrs):
        print(name, bases, attrs)
        del attrs['v1']
        xx = super().__new__(cls, name, bases, attrs)
        return xx
class Foo(object, metaclass=MyType):
    v1 = 123
    def func(self):
        return 123

print(Foo.func)
# print(Foo.v1)


