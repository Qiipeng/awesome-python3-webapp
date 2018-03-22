# -*- coding: utf-8 -*-
import time

from coroweb import get
from models import User
from models import Blog

__author__ = 'Qp'

' url handlers '


@get('/')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, ' \
              'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]

    user = await User.find(123)
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        'user': user
    }
