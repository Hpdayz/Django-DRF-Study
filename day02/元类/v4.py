# 默认基于type来创建类
class MyType(type):
    def __new__(cls, *args, **kwargs):
        xx = super().__new__(cls, *args, **kwargs)
        print("创建类",xx)
        return xx
class Foo(object, metaclass=MyType):
    v1 = 123
    def func(self):
        return 123
# print(Foo)