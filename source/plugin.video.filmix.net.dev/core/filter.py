# -*- coding: utf-8 -*-

import os, re, sys, hashlib, traceback, datetime
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from common import Render
from defines import *
from list import AbstactList
from http import HttpData

CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))

#кешируем загружаемые фильтры на неделю
CACHE_TIME = 60*60*24*7

class FilterData(HttpData):

    def get_genre_list(self):
        html = self.load('%s/search' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('section', id='items-more-ganres').find_all('span', class_='item')
        for genre in genres:
            result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
            result['href'].append(genre.get('data-scope')[0].encode('utf-8').decode('utf-8')+genre.get('data-value')[0].encode('utf-8').decode('utf-8'))
        print result
        return CACHE_TIME, result

    def get_quality_list(self):
        html = self.load('%s/search' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('section', id='items-more-rip').find_all('span', class_='item')
        for genre in genres:
            result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
            result['href'].append(genre.get('data-scope')[0].encode('utf-8').decode('utf-8')+genre.get('data-value')[0].encode('utf-8').decode('utf-8'))
        print result
        return CACHE_TIME, result

    def get_country_list(self):
        html = self.load('%s/search' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('section', id='items-more-country').find_all('span', class_='item')
        for genre in genres:
            result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
            result['href'].append(genre.get('data-scope')[0].encode('utf-8').decode('utf-8')+genre.get('data-value')[0].encode('utf-8').decode('utf-8'))
        print result
        return CACHE_TIME, result

    def get_awards_list(self):
        html = self.load('%s/search' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('section', id='items-more-translate').find_all('span', class_='item')
        for genre in genres:
            result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
            result['href'].append(genre.get('data-scope')[0].encode('utf-8').decode('utf-8')+genre.get('data-value')[0].encode('utf-8').decode('utf-8'))
        print result
        return CACHE_TIME, result



class Filter(FilterData, AbstactList):
    def handle(self):
        try:
            params = self.argv[0]
        except:
            params = {}

        self.rubric_list = {
            'name' : [
                xbmcup.app.lang[30136],
                xbmcup.app.lang[30114],
                xbmcup.app.lang[30115],
                xbmcup.app.lang[30116],
                xbmcup.app.lang[30117]
            ],
            'href' : [
                '',
                's999',
                's14',
                's7',
                's93'
            ]
        }

        window = str(params.get('window', ''))
        filter = params.get('filter', {})
        show_results = params.get('show_results', False)
        page = params.get('page', 0)

        if(window != ''):
            value = eval('self.'+window+'_window')()
            if(value == False):
                return False
            filter.update({window:value})

        if('rubrics' not in filter):
            filter.update({'rubrics' : [self.rubric_list['name'][0], self.rubric_list['href'][0], 0]})

        rubric      = filter.get('rubrics')
        genre       = filter.get('genre',    [xbmcup.app.lang[30135]])
        year        = filter.get('years',    [xbmcup.app.lang[30135]])
        qiality     = filter.get('qualitys', [xbmcup.app.lang[30136]])
        award       = filter.get('awards',   [xbmcup.app.lang[30136]])
        production  = filter.get('productions', [xbmcup.app.lang[30136]])

        print filter

        self.item(xbmcup.app.lang[30128] % rubric[0],      self.replace('filter', {'window' : 'rubrics', 'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30129] % genre[0],       self.replace('filter', {'window' : 'genre',   'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30145] % year[0],       self.replace('filter', {'window' : 'years',   'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30130] % qiality[0],     self.replace('filter', {'window' : 'qualitys','filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30132] % production[0],  self.replace('filter', {'window' : 'productions', 'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30131] % award[0],       self.replace('filter', {'window' : 'awards',  'filter' : filter}),  folder=True, cover=cover.search)

        self.item(xbmcup.app.lang[30133],
                  self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : 0}),
                  folder=True, cover=cover.search)

        self.item('', self.link('null'),  folder=False, cover=cover.search)

        try:
            sort_by = SORT_TYPES[int(xbmcup.app.setting['sort_by'])]
        except:
            sort_by = 'new'

        url = "filters/"
        params = []
        for key in filter:
            if(filter[key][1] != ''):
                params.append(filter[key][1])

        url = url+('-'.join(params))

        if(show_results == True):
            md5 = hashlib.md5()
            md5.update(url+'/page/'+str(page))

            response = CACHE(str(md5.hexdigest()), self.get_movies, url, page)

            if(response['page']['maxpage'] == 0):
                response['page']['maxpage'] = response['page']['pagenum']

            self.item(xbmcup.app.lang[30134] % (str(response['page']['pagenum'])),
                      self.link('null'),  folder=False, cover=cover.search)


            if(response['page']['pagenum'] > 1):
                self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]',
                          self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : (page-1)}),
                          cover=cover.prev)

            self.add_movies(response, 30110)

            if(response['page']['maxpage'] >= response['page']['pagenum']+1):
                self.item('[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]',
                            self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : (page+1)}),
                            cover=cover.next)


    def rubrics_window(self):
        ret = xbmcup.gui.select(xbmcup.app.lang[30137], self.rubric_list['name'])
        return False if ret < 0 else [self.rubric_list['name'][ret], self.rubric_list['href'][ret], ret]

    def qualitys_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/qualitys')
        self.quality_list = CACHE(str(md5.hexdigest()), self.get_quality_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30139], self.quality_list['name'])
        return False if ret < 0 else [self.quality_list['name'][ret], self.quality_list['href'][ret], ret]

    def productions_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/countries')
        self.productions_list = CACHE(str(md5.hexdigest()), self.get_country_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30141], self.productions_list['name'])
        return False if ret < 0 else [self.productions_list['name'][ret], self.productions_list['href'][ret], ret]

    def genre_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/janrs')
        genres_list = CACHE(str(md5.hexdigest()), self.get_genre_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30138], genres_list['name'])
        return False if ret < 0 else [genres_list['name'][ret], genres_list['href'][ret], ret]

    def awards_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/awards')
        awards_list = CACHE(str(md5.hexdigest()), self.get_awards_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30140], awards_list['name'])
        return False if ret < 0 else [awards_list['name'][ret], awards_list['href'][ret], ret]

    def years_window(self):
        now_time = datetime.datetime.now()
        years_list = map(str, list(reversed(range(1900, int(now_time.year)+1))))
        years_list.insert(0, xbmcup.app.lang[30135])
        ret = xbmcup.gui.select(xbmcup.app.lang[30144], years_list)
        return False if ret < 0 else [years_list[ret], "y%s" % str(years_list[ret]) if ret > 0 else '', ret]