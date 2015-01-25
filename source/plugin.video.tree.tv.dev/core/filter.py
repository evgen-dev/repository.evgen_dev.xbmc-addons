# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from common import Render
from defines import *
from defines import *
from list import HttpData

CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))

#кешируем загружаемые фильтры на сутки
CACHE_TIME = 60*60*24

class FilterData(HttpData):

    def get_genre_list(self):
        html = self.load('%s/default/index/janrs' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('div', class_='scroll-pane').find_all('a')
        for genre in genres:
            result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
            result['href'].append("janrs/%s" % genre.get('rel')[0].encode('utf-8').decode('utf-8'))

        return CACHE_TIME, result

    def get_awards_list(self):
            html = self.load('%s/default/index/awards' % SITE_URL)
            result = {'name' : [xbmcup.app.lang[30136]], 'href': ['']}
            if not html:
                return None, result
            soup = xbmcup.parser.html(self.strip_scripts(html))
            avards = soup.find('div', id='awards').find_all('div', class_='awards_item')
            for avard in avards:
                result['name'].append(avard.find('p').get_text().strip().encode('utf-8').decode('utf-8'))
                result['href'].append("awards/%s" % avard.find('a').get('rel')[0].encode('utf-8').decode('utf-8'))

            return CACHE_TIME, result



class Filter(xbmcup.app.Handler, FilterData, Render):

    def handle(self):
        try:
            params = self.argv[0]
        except:
            params = {}

        self.rubric_list = {
            'name' : [
                xbmcup.app.lang[30114],
                xbmcup.app.lang[30115],
                xbmcup.app.lang[30116],
                xbmcup.app.lang[30117],
                xbmcup.app.lang[30118],
            ],
            'href' : [
                '/films/',
                '/serials/',
                '/multfilms/',
                '/onlinetv/',
                '/anime/',
            ]
        }

        self.quality_list = {
            'name' : [
                xbmcup.app.lang[30136],
                "HD",
                "HQ",
                "SQ",
                "LQ"
            ],
            'href' : [
                '',
                'quality/HD',
                'quality/HQ',
                'quality/SQ',
                'quality/LQ'
            ]
        }

        self.productions_list = {
            'name' : [
                xbmcup.app.lang[30136],
                xbmcup.app.lang[30142],
                xbmcup.app.lang[30143]
            ],
            'href' : [
                '',
                'production/our',
                'production/foreign'
            ]
        }

        window = str(params.get('window', ''))
        filter = params.get('filter', {})
        show_results = params.get('show_results', False)
        page = params.get('page', 0)

        if(window != ''):
            value = eval('self.'+window+'_window')(filter.get(window, None))
            filter.update({window:value})

        if('rubrics' not in filter):
            filter.update({'rubrics' : [self.rubric_list['name'][0], self.rubric_list['href'][0], 0]})

        rubric      = filter.get('rubrics')
        genre       = filter.get('genre',    [xbmcup.app.lang[30135]])
        qiality     = filter.get('qualitys', [xbmcup.app.lang[30136]])
        award       = filter.get('awards',   [xbmcup.app.lang[30136]])
        production  = filter.get('productions', [xbmcup.app.lang[30136]])

        print filter

        self.item(xbmcup.app.lang[30128] % rubric[0],      self.replace('filter', {'window' : 'rubrics', 'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30129] % genre[0],       self.replace('filter', {'window' : 'genre',   'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30130] % qiality[0],     self.replace('filter', {'window' : 'qualitys','filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30131] % award[0],       self.replace('filter', {'window' : 'awards',  'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30132] % production[0],  self.replace('filter', {'window' : 'productions', 'filter' : filter}),  folder=True, cover=cover.search)

        self.item(xbmcup.app.lang[30133],
                  self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : 0}),
                  folder=True, cover=cover.search)

        self.item('', self.link('null'),  folder=False, cover=cover.search)

        try:
            sort_by = SORT_TYPES[int(xbmcup.app.setting['sort_by'])]
        except:
            sort_by = 'new'

        url = filter['rubrics'][1]+"sortType/%s/" % sort_by
        for key in filter:
            if(key != 'rubrics' and filter[key][1] != ''):
                url = url+"%s/" % filter[key][1].strip('/')

        if(show_results == True):
            md5 = hashlib.md5()
            md5.update(url+'/page/'+str(page))

            response = CACHE(str(md5.hexdigest()), self.get_movies, url, page)

            if(response['page']['maxpage'] == 0):
                response['page']['maxpage'] = response['page']['pagenum']

            self.item(xbmcup.app.lang[30134] % (str(response['page']['pagenum']), str(response['page']['maxpage'])),
                      self.link('null'),  folder=False, cover=cover.search)


            if(response['page']['pagenum'] > 1):
                self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]',
                          self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : (page-1)}),
                          cover=cover.prev)

            if(len(response['data']) > 0):
                for movie in response['data']:
                    self.item(movie['name']+' '+movie['year']+' '+movie['quality'],
                              self.link('quality-list', {'movie_page' : movie['url'], 'cover' : movie['img']}),
                              folder=True, cover=movie['img'])
                print response['page']
                print page

                if(response['page']['maxpage'] >= response['page']['pagenum']+1):
                    self.item('[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]',
                              self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : (page+1)}),
                              cover=cover.next)
            else:
                self.item(u'[COLOR red]['+xbmcup.app.lang[30110]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)


    def rubrics_window(self, prev):
        prev_key = None
        if(prev != None):
            prev_key = prev[2]

        w = xbmcgui.Dialog()
        ret = w.select(xbmcup.app.lang[30137], self.rubric_list['name'])
        del w
        try:
            self.rubric_list['name'][prev_key]
        except:
            prev_key = None
        if(ret < 0 and prev_key == None):
            ret = 0
        elif(ret < 0 and prev_key != None):
            ret = int(prev_key)
        return [self.rubric_list['name'][ret], self.rubric_list['href'][ret], ret]

    def qualitys_window(self, prev):
        prev_key = None
        if(prev != None):
            prev_key = prev[2]

        w = xbmcgui.Dialog()
        ret = w.select(xbmcup.app.lang[30139], self.quality_list['name'])
        del w
        try:
            self.quality_list['name'][prev_key]
        except:
            prev_key = None
        if(ret < 0 and prev_key == None):
            ret = 0
        elif(ret < 0 and prev_key != None):
            ret = int(prev_key)
        return [self.quality_list['name'][ret], self.quality_list['href'][ret], ret]

    def productions_window(self, prev):
        prev_key = None
        if(prev != None):
            prev_key = prev[2]

        w = xbmcgui.Dialog()
        ret = w.select(xbmcup.app.lang[30139], self.productions_list['name'])
        del w
        try:
            self.productions_list['name'][prev_key]
        except:
            prev_key = None
        if(ret < 0 and prev_key == None):
            ret = 0
        elif(ret < 0 and prev_key != None):
            ret = int(prev_key)
        return [self.productions_list['name'][ret], self.productions_list['href'][ret], ret]

    def genre_window(self, prev):
        prev_key = None
        if(prev != None):
            prev_key = prev[2]

        w = xbmcgui.Dialog()
        md5 = hashlib.md5()
        md5.update('/default/index/janrs')
        genres_list = CACHE(str(md5.hexdigest()), self.get_genre_list)
        try:
            genres_list['name'][prev_key]
        except:
            prev_key = None
        ret = w.select(xbmcup.app.lang[30138], genres_list['name'])
        del w
        if(ret < 0 and prev_key == None):
            ret = 0
        elif(ret < 0 and prev_key != None):
            ret = int(prev_key)
        return [genres_list['name'][ret], genres_list['href'][ret], ret]


    def awards_window(self, prev):
        prev_key = None
        if(prev != None):
            prev_key = prev[2]
        w = xbmcgui.Dialog()
        md5 = hashlib.md5()
        md5.update('/default/index/awards')
        awards_list = CACHE(str(md5.hexdigest()), self.get_awards_list)
        try:
            awards_list['name'][prev_key]
        except:
            prev_key = None
        ret = w.select(xbmcup.app.lang[30140], awards_list['name'])
        del w
        if(ret < 0 and prev_key == None):
            ret = 0
        elif(ret < 0 and prev_key != None):
            ret = int(prev_key)
        return [awards_list['name'][ret], awards_list['href'][ret], ret]