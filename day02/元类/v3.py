class MyType(type):
    pass
Foo = MyType("Foo", (object,), {"v1": 123, "func": lambda self: 123})

obj = Foo()
print(obj.v1)
print(obj.func())