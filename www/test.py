import orm
import asyncio
from models import User, Blog, Comment


async def test(loop):
    # 创建连接池
    db_dict = {'user': 'root', 'password': 'admin', 'database': 'awesome'}
    await orm.create_pool(loop=loop, **db_dict)
    u = User(name='Test', email='test@example.com', password='12345', image='about:blank', id='123')
    await u.save()
    await orm.close_pool()


loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
