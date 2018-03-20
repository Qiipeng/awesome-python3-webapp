# -- UTF-8 --
import logging
import asyncio
# import os
# import json
# import time
# from datetime import datetime
from aiohttp import web

# async web application

__author__ = 'Qp'

logging.basicConfig(level=logging.INFO)


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', headers={'content-type': 'text/html'})


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 8088)
    logging.info('server started at http://127.0.0.1:8088...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
