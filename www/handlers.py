# -*- coding: utf-8 -*-
import hashlib
import time
import re
import logging
import json

from aiohttp import web
from apis import APIValueError, APIError, APIPermissionError, Page
from config import configs
from coroweb import get
from coroweb import post
from models import User, next_id
from models import Blog

__author__ = 'Qp'

' url handlers '

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


# 首页
@get('/')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, ' \
              'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]
    cookie_str = request.cookies.get(COOKIE_NAME)
    user = ''
    if cookie_str:
        if 'deleted' in cookie_str:
            user = ''
        else:
            user = await cookie2user(cookie_str)
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        'user': user
    }


# 用户注册页面
@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }


# 用户注册
@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHAI.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email,
                password=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest)
    await user.save()
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


# 用户登出
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-delete-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


# 用户登陆页面
@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


# 用户登陆
@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', email)
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check password
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.password != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


# 日志创建页面
@get('/manage/blogs/create')
def manage_create_blog(request):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs',
        'user': request.__user__
    }


# 日志管理页面
@get('/manage/blogs')
def manage_blogs(request, *, page=1):
    return {
        '__template__': 'manage_blog.html',
        'page_index': get_page_index(page),
        'user': request.__user__
    }


# 日志列表
@get('/api/blogs')
async def api_blog(*, page=1):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    page = Page(num, page_index)
    if num == 0:
        return dict(page=page, blog=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return dict(page=page, blogs=blogs)


# 日志编辑
@get('/api/blogs/edit')
async def api_blog_edit():
    pass


# 日志创建
@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name can not be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary can not be emtpy.')
    if not content or not content.strip():
        raise APIValueError('content', 'content can not be empty')
    user = request.__user__
    blog = Blog(user_id=user.id, user_name=user.name, user_image=user.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog


# 邮箱验证
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHAI = re.compile(r'^[0-9a-f]{40}$')


# 计算加密cookie
def user2cookie(user, max_age):
    """
    Generate cookie str by user
    :param user:
    :param max_age:
    :return:
    """
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.password, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


# 解密cookie
async def cookie2user(cookie_str):
    """
    Parse cookie and load user if cookie is valid
    :param cookie_str:
    :return:
    """
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.password, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.password = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


# 检查是否是超级用户
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


# 获取页数
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        logging.exception(e)
    if p < 1:
        p = 1
    return p
