# -*- coding: utf-8 -*-

import xbmcup.system
from defines import *

icons_path = 'home://addons/'+PLUGIN_ID+'/resources/media/icons/'

treetv = xbmcup.system.fs(icons_path+'/icon.png')
search = xbmcup.system.fs(icons_path+'/search.png')
info = xbmcup.system.fs(icons_path+'/info.png')
next = xbmcup.system.fs(icons_path+'/next.png')
prev = xbmcup.system.fs(icons_path+'/prev.png')

res_icon = {}
res_icon['360']     = xbmcup.system.fs(icons_path+'/360.png')
res_icon['480']     = xbmcup.system.fs(icons_path+'/480.png')
res_icon['720']     = xbmcup.system.fs(icons_path+'/720.png')
res_icon['1080']    = xbmcup.system.fs(icons_path+'/1080.png')
res_icon['default'] = xbmcup.system.fs(icons_path+'/1080.png')