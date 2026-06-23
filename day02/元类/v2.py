# 创建类：方法1
# class Foo:
#     v1 = 123
#     def func(self):
#         return 123


# 创建类：方法2
# 类名 = type("类名", (父类, ), { 成员 })
Foo = type("Foo", (object,), {"v1": 123, "func": lambda self: 123})

obj = Foo()
print(obj.v1)
print(obj.func())