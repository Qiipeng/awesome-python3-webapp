# -- UTF-8 --
import asyncio

import orm


# 测试orm
# User实体类
class User(orm.Model):
    __table__ = 'users'  # 设定操作数据库表
    id = orm.IntegerField(primary_key=True)  # 设定列属性
    name = orm.StringField()


async def main(loop):
    await orm.create_pool(loop, **database)
    print(type(User()))
    user = User()
    user.id = 1
    user.name = 'A君'
    user.insert()
    # users = User.findAll()
    # for user in users:
    #     print(user)


loop = asyncio.get_event_loop()
database = {
    'host': 'localhost',  # 数据库的地址
    'user': 'root',
    'password': 'admin',
    'db': 'python_test'
}

task = asyncio.ensure_future(main(loop))

res = loop.run_until_complete(task)
print(res)
