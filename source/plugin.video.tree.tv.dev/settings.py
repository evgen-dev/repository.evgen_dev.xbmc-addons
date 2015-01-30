# -*- coding: utf-8 -*-
#очистка кеша

import sys, xbmc, xbmcaddon
sys.argv[0] = sys.argv[0].replace('/settings.py', '')
print sys.argv[0]
import os, xbmcup.app, xbmcup.system, xbmcup.db
from core.defines import *
from core.auth import Auth
import core.cover

__settings__ = xbmcaddon.Addon(id=sys.argv[0])

def Notificator(title, message, timeout = 500):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(title, message, timeout, core.cover.treetv))

if(sys.argv[1] == 'clear_cache'):
    CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))
    CACHE.flush()
    Notificator('Очистка кеша', 'Кеш успешно очищен', 3000)

if(sys.argv[1] == 'login'):
    is_logged = Auth().autorize()
    if(is_logged):
        Notificator('Авторизация', 'Вы успешно авторизованы', 3000)
    else:
        Notificator('Авторизация', 'Войти не удалось, проверьте логин и пароль', 3000)
    __settings__.openSettings()


if(sys.argv[1] == 'logout'):
    Auth().reset_auth()
    Notificator('Авторизация', 'Вы успешно вышли', 3000)
    __settings__.openSettings()

