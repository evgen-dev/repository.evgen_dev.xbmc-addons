# -*- coding: utf-8 -*-
#очистка кеша

import sys, xbmc, xbmcaddon
from core.defines import *
sys.argv[0] = PLUGIN_ID
import os, xbmcup.app, xbmcup.system, xbmcup.db, xbmcup.gui

from core.auth import Auth
from core.http import HttpData
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

if(sys.argv[1] == 'activation'):
    headers = {
        'User-agent' : 'KODI'
    }
    response = xbmcup.net.http.get('http://treetv.tk/get_settings.php?key='+xbmcup.app.setting['activate_code'], headers=headers)
    if response.text == 'error':
        xbmcup.gui.message('Не удалось выполнить активацию, проверьте код.')
    else:
        xbmcup.app.setting['is_activated'] = 'true'
        file = xbmcup.system.fs('sandbox://fingerprint.json')
        xbmcup.gui.message('Плагин успешно активирован!')
        f = open(file, 'w')
        f.write(response.text)
        f.close()
        xbmc.executebuiltin('Container.Refresh()')
    openAddonSettings(PLUGIN_ID, 0, 3)

if(sys.argv[1] == 'reset_activation'):
    xbmcup.app.setting['is_activated'] = 'false'
    xbmcup.system.fs.delete('sandbox://fingerprint.json')
    xbmcup.gui.message('Активация успешно сброшена!')
    xbmcup.app.setting['activate_code'] = ''
    openAddonSettings(PLUGIN_ID, 0, 3)
    xbmc.executebuiltin('Container.Refresh()')