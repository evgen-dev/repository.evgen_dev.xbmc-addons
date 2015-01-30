# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from http import HttpData
from common import Render
from defines import *

class ContextMenu(xbmcup.app.Handler, HttpData, Render):

    def handle(self):
        try:
            params = self.argv[0]
        except:
            params = {}

        try:
            eval('self.'+params['action'])(params)
        except:
            xbmcup.gui.message('Addon internal error', title='Call to undefined method ContextMenu::%s()' % params['action'])
            print traceback.format_exc()

    def add_bookmark(self, params):
        self.ajax('%s/users/profile/addtobookmark?film_id=%s&bookmark_id=%s' % (SITE_URL, params['id'], self.get_book_dir()))
        xbmcup.gui.message(xbmcup.app.lang[30150].encode('utf-8'))

    def del_bookmark(self, params):
        self.ajax('%s/film/index/deletefromfavorietes?id_film=%s' % (SITE_URL, params['id']))
        xbmcup.gui.message(xbmcup.app.lang[30151].encode('utf-8'))
        xbmc.executebuiltin('Container.Refresh()')


    def get_book_dir(self):
        if(xbmcup.app.setting['bookmark_dir'] == ''):
            self.ajax('%s/users/profile/addbookmark?name=%s' % (SITE_URL, BOOKMARK_DIR))
            html = self.ajax('%s//users/profile/mybookmark' % SITE_URL)
            if not html:
                raise TypeError('html is None')
            soup = xbmcup.parser.html(self.strip_scripts(html.encode('utf-8')))
            options = soup.find('div', class_='book_mark_select').find_all('option')
            for option in options:
                name = option.get_text().strip()
                if(name == BOOKMARK_DIR):
                    value = option.get('value')
                    xbmcup.app.setting['bookmark_dir'] = value
                    break
        return xbmcup.app.setting['bookmark_dir']