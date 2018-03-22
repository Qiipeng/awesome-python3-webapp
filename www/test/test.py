# -- coding: utf-8 --


class ObjectCreator:
    def __init__(self, **kwargs):
        print(kwargs)
        # super(ObjectCreator, self).__init__()

    pass


# print(ObjectCreator)


def choose_class(name):
    if name == 'foo':
        class Foo:
            pass

        return Foo
    else:
        class Bar:
            pass

        return Bar


MyClass = choose_class('foo')
# print(MyClass)  # 返回类,而不是实例: <class '__main__.choose_class.<locals>.Foo'>
# print(MyClass())  # 返回实例: <__main__.choose_class.<locals>.Foo object at 0x057915D0>
print(ObjectCreator(name='A'))
# print(ObjectCreator())

t = type('ObjectCreator', (), {})
print(t())


class Foo:
    bar = True


class FooChild(Foo):
    pass


def echo_bar(self):
    print(self.bar)


fooChild = type('FooChild', (Foo,), {'echo_bar': echo_bar})
print(hasattr(Foo, 'echo_bar'))
print(hasattr(fooChild, 'echo_bar'))
