# -*- coding: utf-8 -*-
from coroweb import get

__author__ = 'Qp'

' url handlers '


@get('/')
async def index(request):
    return '<h1>Awesome</h1>'
