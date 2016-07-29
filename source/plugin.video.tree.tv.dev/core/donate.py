# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback,json
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from http import HttpData
from defines import *


class Donate(xbmcup.app.Handler, HttpData):
    def handle(self):
        js_string = self.load('http://devisok.org/xbmc.php')
        js_string = json.loads(js_string, 'utf-8')

        if(xbmcgui.Dialog().yesno(js_string['title'], js_string['content'], yeslabel='Я помог!', nolabel='Закрыть')):
            xbmcup.gui.message(js_string['thanks'].encode('utf-8'))