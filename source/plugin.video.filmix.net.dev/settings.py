# -*- coding: utf-8 -*-
#очистка кеша

import sys, xbmc, xbmcaddon
from core.defines import *
sys.argv[0] = PLUGIN_ID
import os, xbmcup.app, xbmcup.system, xbmcup.db, xbmcup.gui

from core.auth import Auth
import core.cover

def openAddonSettings(addonId, id1=None, id2=None):
    xbmc.executebuiltin('Addon.OpenSettings(%s)' % addonId)
    if id1 != None:
        xbmc.executebuiltin('SetFocus(%i)' % (id1 + 200))
    if id2 != None:
        xbmc.executebuiltin('SetFocus(%i)' % (id2 + 100))

if(sys.argv[1] == 'clear_cache'):
    CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))
    CACHE.flush()
    SQL = xbmcup.db.SQL(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))
    try:
        SQL.set('DELETE FROM search')
    except:
        pass
    xbmcup.gui.message('Кеш успешно очищен')

if(sys.argv[1] == 'login'):
    is_logged = Auth().autorize()
    if(is_logged):
        xbmcup.gui.message('Вы успешно авторизованы')
    else:
        xbmcup.gui.message('Войти не удалось, проверьте логин и пароль')
    openAddonSettings(PLUGIN_ID, 1, 0)


if(sys.argv[1] == 'logout'):
    Auth().reset_auth(True)
    xbmcup.gui.message('Вы успешно вышли')
    openAddonSettings(PLUGIN_ID, 1, 0)

