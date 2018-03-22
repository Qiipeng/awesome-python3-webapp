# -- coding: utf-8 --

import asyncio
import threading


# asyncio: 从asyncio模块中获取EventLoop引用,然后把需要执行的协程丢到EventLoop中执行
@asyncio.coroutine
def hello():
    print('hello world (%s)' % threading.currentThread())
    r = yield from asyncio.sleep(1)
    print('hello again (%s)' % threading.currentThread())


# 获取EventLoop
loop = asyncio.get_event_loop()
tasks = [hello(), hello()]
# 执行coroutine
# loop.run_until_complete(hello())
loop.run_until_complete(asyncio.wait(tasks))  # 同一个线程并发执行
loop.close()
