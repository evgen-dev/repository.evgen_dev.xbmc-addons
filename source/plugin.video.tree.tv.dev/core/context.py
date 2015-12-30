# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from http import HttpData
from auth import Auth
from common import Render
from defines import *

class ContextMenu(xbmcup.app.Handler, HttpData, Render):

    def handle(self):
        self.is_logged = Auth().autorize()
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
        try:
            bookmark_dir = params['dir']
        except:
            return False
            #bookmark_dir = self.get_book_dir()

        if not self.is_logged:
            xbmcup.gui.message(xbmcup.app.lang[30153].encode('utf-8'))
            return False
        resp = self.ajax('%s/users/profile/addtobookmark?film_id=%s&bookmark_id=%s' % (SITE_URL, params['id'], bookmark_dir))
        try:
            resp = json.loads(resp)
            if(resp['result'] == True):
                xbmcup.gui.message(xbmcup.app.lang[30150].encode('utf-8'))
            else:
                xbmcup.gui.message(xbmcup.app.lang[30154].encode('utf-8'))
                print resp
        except:
            pass

    def add_bookmark_in(self, params):
        response = self.get_bookmarks()[1]
        if(len(response['data']) == 0):
            return
        folders = [xbmcup.app.lang[30157]]
        hrefs = ['add_dir']
        for movie in response['data']:
            hrefs.append(movie['url'])
            folders.append(movie['name'])
        ret = xbmcup.gui.select(xbmcup.app.lang[30156], folders)
        if (ret != None):
            if(hrefs[ret] == 'add_dir'):
                keyboard = xbmc.Keyboard()
                keyboard.setHeading(xbmcup.app.lang[30112])
                keyboard.doModal()
                dirname = keyboard.getText(0)
                if not dirname: return False
                self.ajax('%s/users/profile/addbookmark?name=%s' % (SITE_URL, dirname))
                self.add_bookmark_in(params)
                return False
            else:
                self.add_bookmark({'id' : params['id'], 'dir' : hrefs[ret]})

    def del_bookmark(self, params):
        resp = self.ajax('%s/film/index/deletefromfavorietes?id_film=%s' % (SITE_URL, params['id']))
        try:
            resp = json.loads(resp)
            if(resp['result'] == True):
                xbmcup.gui.message(xbmcup.app.lang[30151].encode('utf-8'))
            else:
                xbmcup.gui.message(xbmcup.app.lang[30155].encode('utf-8'))
        except:
            pass
        xbmc.executebuiltin('Container.Refresh()')


    def get_book_dir(self):
        if(True):
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


    def del_bookmark_dir(self, params):
        data = {}
        data['bookmark['+params['id']+'][delete]'] = 1;
        h = self.post('%s/users/profile/editbookmark?type=change' % (SITE_URL), data)
        print h.encode('utf8')
        xbmcup.gui.message(xbmcup.app.lang[30159].encode('utf-8'))
        xbmc.executebuiltin('Container.Refresh()')