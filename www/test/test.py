# -- coding: utf-8 --


class ObjectDict(dict):
    def __init__(self, *args, **kwargs):
        super(ObjectDict, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        value = self[item]
        if isinstance(value, dict):
            value = ObjectDict(value)
        return value


if __name__ == '__main__':
    od = ObjectDict(asf={'a': 1}, d=True)
    print(od.asf)
    print(od.asf.a)
    print(od.d)
