# -- coding:utf8 --

import asyncio


# python3.5 之后的新语法,代替@asyncio.conroutine
async def hello():
    print('hello world')
    # await代替yield from
    await asyncio.sleep(3)
    print('hello again')


# 获取EventLoop
loop = asyncio.get_event_loop()
loop.run_until_complete(hello())
loop.close()
