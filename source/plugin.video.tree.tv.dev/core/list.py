# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from http import HttpData
from auth import Auth
from common import Render
from defines import *

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))
SQL = xbmcup.db.SQL(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))

class AbstactList(xbmcup.app.Handler, HttpData, Render):
    def add_movies(self, response, ifempty=30111):
        if(len(response['data']) > 0):
            for movie in response['data']:
                menu = []
                if(self.__class__.__name__ != 'BookmarkList'):
                    #menu.append([xbmcup.app.lang[30147], self.link('context', {'action': 'add_bookmark', 'id' : movie['id']})])
                    menu.append([xbmcup.app.lang[30147], self.link('context', {'action': 'add_bookmark_in', 'id' : movie['id']})])
                else:
                    menu.append([xbmcup.app.lang[30148], self.link('context', {'action': 'del_bookmark', 'id' : movie['id']})])

                self.item(movie['name']+' '+movie['year']+' '+movie['quality'],
                          self.link('quality-list', {'movie_page' : movie['url'], 'cover' : movie['img']}),
                          folder=True, cover=movie['img'], menu=menu)
        else:
            self.item(u'[COLOR red]['+xbmcup.app.lang[ifempty]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)


class CollectionList(AbstactList):
    def handle(self):
        params = self.argv[0]
        try:
            url = params['url']
        except:
            url = ''

        if(url == ''):
            self.show_dirs()
        else:
            self.show_movies(url, params)

    def show_dirs(self):
        md5 = hashlib.md5()
        md5.update('/collection')
        response = CACHE(str(md5.hexdigest()), self.get_collections)

        if(len(response['data']) > 0):
            for movie in response['data']:
                self.item(movie['name'],
                        self.link('collection', {'url' : movie['url']}),
                        folder=True, cover=movie['img'])
        else:
            self.item(u'[COLOR red]['+xbmcup.app.lang[30111]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)

    def show_movies(self, url, params):
        try:
            page = int(params['page'])
        except:
            params['page'] = 0
            page = 0

        md5 = hashlib.md5()
        md5.update(url)
        response = CACHE(str(md5.hexdigest()), self.get_movies, url, page, 'main_content_item', False, "", "item_wrap")

        if(response['page']['pagenum'] > 1):
            params['page'] = page-1
            self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]', self.replace('collection', params), cover=cover.prev)
            params['page'] = page+1

        self.add_movies(response)

        params['page'] = page+1
        if(response['page']['maxpage'] >= response['page']['pagenum']+1):
            self.item('[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]', self.replace('collection', params), cover=cover.next)


class MovieList(AbstactList):
    def handle(self):
        params = self.argv[0]
        try:
            page = int(params['page'])
        except:
            params['page'] = 0
            page = 0

        try:
            sort_by = SORT_TYPES[int(xbmcup.app.setting['sort_by'])]
        except:
            sort_by = 'new'

        page_url = "/"+params['dir']+"/sortType/%s" % sort_by

        md5 = hashlib.md5()
        md5.update(page_url+'/page/'+str(page))

        response = CACHE(str(md5.hexdigest()), self.get_movies, page_url, page)
        if(response['page']['pagenum'] > 1):
            params['page'] = page-1
            self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]', self.replace('list', params), cover=cover.prev)
            params['page'] = page+1

        self.add_movies(response)

        params['page'] = page+1
        if(response['page']['maxpage'] >= response['page']['pagenum']+1):
            self.item('[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]', self.replace('list', params), cover=cover.next)

class SearchList(AbstactList):
    def handle(self):
        try:
            params = self.argv[0]
        except:
            params = {}

        try:
            page = int(params['page'])
        except:
            params['page'] = 0
            page = 0

        try:
            req_count = int(xbmcup.app.setting['search_history'])
        except:
            req_count = 0

        if(req_count > 0):
            SQL.set('create table if not exists search(id INTEGER PRIMARY KEY AUTOINCREMENT, value varchar(255) unique)')
            history = SQL.get('SELECT id,value FROM search ORDER BY ID DESC')
        else:
            history = []
            SQL.set('DELETE FROM search')

        try:
            usersearch = params['usersearch']
            vsearch = params['vsearch']
        except:

            if(len(history)):
                history = list(history)
                values = ['[COLOR yellow]'+xbmcup.app.lang[30108]+'[/COLOR]']
                for item in history:
                   values.append(item[1])
                ret = xbmcup.gui.select(xbmcup.app.lang[30161], values)

                if ret == None:
                    return

                if(ret > 0):
                    usersearch = values[ret]
                    vsearch = usersearch.encode('utf-8').decode('utf-8')
                    params['vsearch'] = vsearch
                    params['usersearch'] = urllib.quote_plus(usersearch.encode('utf-8'))
                else:
                    params['vsearch'] = ''
            else:
                params['vsearch'] = ''

            if(params['vsearch'] == ''):
                keyboard = xbmc.Keyboard()
                keyboard.setHeading(xbmcup.app.lang[30112])
                keyboard.doModal()
                usersearch = keyboard.getText(0)
                vsearch = usersearch.decode('utf-8')
                params['vsearch'] = vsearch
                params['usersearch'] = urllib.quote_plus(usersearch)

        if not usersearch: return
        try:
            SQL.set('INSERT INTO search (value) VALUES ("%s")' % (vsearch))
        except sqlite.IntegrityError:
            SQL.set('DELETE FROM search WHERE `value` = "%s"' % (vsearch))
            SQL.set('INSERT INTO search (value) VALUES ("%s")' % (vsearch))
        except:
            pass

        if(len(history) >= req_count):
            SQL.set('DELETE FROM search WHERE `id` = (SELECT MIN(id) FROM search)')

        page_url = "search/index/index/usersearch/%s/filter/all" % params['usersearch']
        #page_url = "search"
        md5 = hashlib.md5()
        md5.update(page_url+'/page/'+str(page))
        #md5.update(params['usersearch'])
        response = CACHE(str(md5.hexdigest()), self.get_movies, page_url, page, 'main_content_item', False, usersearch)

        self.item(u'[COLOR yellow]'+xbmcup.app.lang[30108]+'[/COLOR]', self.link('search'), folder=True, cover=cover.search)
        self.item('[COLOR blue]['+xbmcup.app.lang[30109]+': '+vsearch+'][/COLOR]',
                  self.link('null'), folder=False, cover=cover.info)

        if(response['page']['pagenum'] > 1):
           params['page'] = page-1
           self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]', self.replace('search', params), cover=cover.prev)
           params['page'] = page+1

        self.add_movies(response)

        params['page'] = page+1
        if(response['page']['maxpage'] >= response['page']['pagenum']+1):
           self.item(u'[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]', self.replace('search', params), cover=cover.next)


class BookmarkList(AbstactList):

    def handle(self):
        Auth().autorize()

        try:
            params = self.argv[0]
        except:
            params = {}

        try:
            url = params['url']
        except:
            url = ''

        try:
            page = params['page']
        except:
            page = 1

        try:
            params['keyboard']
        except:
            params['keyboard'] = False

        if(params['keyboard']):
            self.add_dir()
            return False

        if(url == ''):
            if(xbmcup.app.setting['is_logged'] == 'false'):
                xbmcup.gui.message(xbmcup.app.lang[30149].encode('utf-8'))
                return False
            self.show_dirs()
            self._variables['is_item'] = False
            self.render(cache=False)
        else:
            self.show_movies(url, page)
            self._variables['is_item'] = False
            self.render(cache=False)

    def show_dirs(self):
        md5 = hashlib.md5()
        md5.update('/bookmarks')
        response = CACHE(str(md5.hexdigest()), self.get_bookmarks)

        self.item(xbmcup.app.lang[30157],
                        self.link('bookmarks', {'keyboard': True}),
                        folder=False)

        if(len(response['data']) > 0):
            for movie in response['data']:
                menu = []
                menu.append([xbmcup.app.lang[30158], self.link('context', {'action': 'del_bookmark_dir', 'id' : movie['url']})])
                self.item(movie['name'],
                        self.link('bookmarks', {'url' : movie['url']}),
                        folder=True, cover=movie['img'], menu=menu)
        else:
            self.item(u'[COLOR red]['+xbmcup.app.lang[30111]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)

    def show_movies(self, url, page):
        params = {}
        params['url'] = url
        url = 'users/profile/bookmark?bookmark=%s&page=%s&_=1422563130401' % (url,str(page))
        md5 = hashlib.md5()
        md5.update(url)
        response = CACHE(str(md5.hexdigest()), self.get_movies, url, 0, 'book_mark_content', True)

        if(page > 1):
            params['page'] = page-1
            self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]', self.replace('bookmarks', params), cover=cover.prev)
            params['page'] = page+1

        self.add_movies(response, 30152)

        params['page'] = page+1
        if(response['page']['maxpage'] >= response['page']['pagenum']+1):
            self.item(u'[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]', self.replace('bookmarks', params), cover=cover.next)

    def add_dir(self):
        keyboard = xbmc.Keyboard()
        keyboard.setHeading(xbmcup.app.lang[30112])
        keyboard.doModal()
        dirname = keyboard.getText(0)
        if not dirname: return False
        self.ajax('%s/users/profile/addbookmark?name=%s' % (SITE_URL, dirname))



class QualityList(xbmcup.app.Handler, HttpData, Render):

    def get_icon(self, quality):
        if(quality in cover.res_icon):
            return cover.res_icon[quality]
        else:
            return cover.res_icon['default']

    def handle(self):
        self.params = self.argv[0]
        #print self.argv[0]
        try:
            self.movieInfo = self.params['movieInfo']
        except:
            self.movieInfo = self.get_movie_info(self.params['movie_page'])

        try:
            self.params['sub_dir'] = int(self.params['sub_dir'])
        except:
            self.params['sub_dir'] = None

        quality_settings = int(xbmcup.app.setting['quality'])
        default_quality = QUALITYS[quality_settings]

        try:
            self.params['quality_dir'] = int(self.params['quality_dir'])
        except:
            self.params['quality_dir'] = None

        if(self.params['sub_dir'] == None):
            self.def_dir = 0
        else:
            self.def_dir=  self.params['sub_dir']

        print default_quality

        if(default_quality != None and self.params['quality_dir'] == None):
            try:
                test = self.movieInfo['movies'][self.def_dir]['movies'][str(default_quality)]
                self.params['quality_dir'] = str(default_quality)
            except:
                if(xbmcup.app.setting['lowest_quality'] == 'true'):
                    quality_settings -= 1
                    if(quality_settings > 1):
                        try:
                            default_quality = str(QUALITYS[quality_settings])
                            test = self.movieInfo['movies'][self.def_dir]['movies'][default_quality]
                            self.params['quality_dir'] = default_quality
                        except:
                            quality_settings -= 1
                            if(quality_settings > 1):
                                try:
                                    default_quality = str(QUALITYS[quality_settings])
                                    test = self.movieInfo['movies'][self.def_dir]['movies'][default_quality]
                                    self.params['quality_dir'] = default_quality
                                except:
                                    pass

        #если на сайте несколько папок с файлами
        if((len(self.movieInfo['movies']) > 1 and self.params['sub_dir'] == None) or self.movieInfo['no_files'] != None):
            self.show_folders()

        #если эпизоды есть в разном качествве
        elif(self.movieInfo['episodes'] == True and
            len(self.movieInfo['movies'][self.def_dir]['movies']) > 1 and
            self.params['quality_dir'] == None):

            self.show_quality_folder()

        elif(self.movieInfo['episodes'] == True):
            self.show_episodes()


    def show_folders(self):
        print self.movieInfo['no_files']
        if(self.movieInfo['no_files'] == None):
            i = 0
            for movie in self.movieInfo['movies']:
                self.item(movie['folder_title'],
                           self.link('quality-list',
                                    {
                                        'sub_dir' : i,
                                        'movieInfo' : self.movieInfo
                                    }
                           ),
                           folder=True,
                           cover = self.movieInfo['cover']
                )
                i = i+1
        else:
            self.item(u'[COLOR red]['+self.movieInfo['no_files'].decode('utf-8')+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)


    def show_episodes(self):
        show_first_quality = False
        if(self.params['quality_dir']):
            movies = self.movieInfo['movies'][self.def_dir]['movies'][str(self.params['quality_dir'])]
        else:
            show_first_quality = True
            movies = self.movieInfo['movies'][0]['movies']

        if(show_first_quality):
            for quality in movies:
                for movie in movies[quality]:
                    self.add_playable_item(movie)
                break
        else:
            for movie in movies:
                self.add_playable_item(movie)

        self.render_items()

    def show_quality_folder(self):
        if(len(self.movieInfo['movies']) > 1):
            movies = self.movieInfo['movies'][self.params['sub_dir']]['movies']
        else:
            movies = self.movieInfo['movies'][0]['movies']

        resolutions = []
        for movie in movies:
            resolutions.append(int(movie))

        resolutions.sort()

        for movie in resolutions:
            self.item(str(movie),
                self.link('quality-list',
                    {
                        'sub_dir' : self.params['sub_dir'],
                        'quality_dir' : str(movie),
                        'movieInfo' : self.movieInfo
                    }
                ),
                folder=True,
                cover=self.get_icon(str(movie))
            )

    def get_info(self):
        return {
                'Genre'     : self.movieInfo['genres'],
                'year'      : self.movieInfo['year'],
                'director'  : self.movieInfo['director'],
                #'rating' : 8.0,
                #'duration' : '90',
                #'votes' :   '10000',
                'plot' :    self.movieInfo['description']
                # 'playcount' : 1,
                # 'date': '%d.%m.%Y',
                # 'count' : 12
            }


    def add_playable_item(self, movie):
        movie_name = movie.split('?')
        self.item(os.path.basename(str(movie_name[0])),
                           movie,
                           folder=False,
                           media='video',
                           info=self.get_info(),
                           cover = self.movieInfo['cover'],
                           fanart = self.movieInfo['fanart']
                    )
