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
CACHE_TIME = 0#60*60*24*7
CACHE_VERSION =  xbmcup.app.addon['version']

class FilterData(HttpData):

    def get_genre_list(self):
        html = self.load('%s/movies' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('select', id='filter-id-genreId').find_all('option')
        for genre in genres:
            if(genre.get('value') != '0'):
                result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
                result['href'].append(genre.get('value').encode('utf-8').decode('utf-8'))
        return CACHE_TIME, result

    def get_country_list(self):
        html = self.load('%s/movies' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        genres = soup.find('select', id='filter-id-country_id').find_all('option')
        for genre in genres:
            if(genre.get('value') != '0'):
                result['name'].append(genre.get_text().strip().encode('utf-8').decode('utf-8'))
                result['href'].append(genre.get('value').encode('utf-8').decode('utf-8'))
        return CACHE_TIME, result

    def get_years_list(self):
        html = self.load('%s/movies' % SITE_URL)
        result = {'name' : [xbmcup.app.lang[30135]], 'href': ['']}
        if not html:
            return None, result
        soup = xbmcup.parser.html(self.strip_scripts(html))
        years = soup.find('select', id='filter-id-year').find_all('option')
        for year in years:
            if(year.get('value') != '0'):
                result['name'].append(year.get_text().strip().encode('utf-8').decode('utf-8'))
                result['href'].append(year.get('value').encode('utf-8').decode('utf-8'))
        return CACHE_TIME, result


class Filter(FilterData, AbstactList):
    def handle(self):
        try:
            params = self.argv[0]
        except:
            params = {}

        self.rubric_list = {
            'name' : [
                xbmcup.app.lang[30114],
                xbmcup.app.lang[30115]
            ],
            'href' : [
                #'',
                'movies',
                'tvseries'
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
        rating       = filter.get('ratings',   [xbmcup.app.lang[30136]])
        production  = filter.get('productions', [xbmcup.app.lang[30136]])

        print filter

        self.item(xbmcup.app.lang[30128] % rubric[0],      self.replace('filter', {'window' : 'rubrics', 'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30129] % genre[0],       self.replace('filter', {'window' : 'genre',   'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30145] % year[0],       self.replace('filter', {'window' : 'years',   'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30132] % production[0],  self.replace('filter', {'window' : 'productions', 'filter' : filter}),  folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30131] % rating[0],       self.replace('filter', {'window' : 'ratings',  'filter' : filter}),  folder=True, cover=cover.search)

        self.item(xbmcup.app.lang[30133],
                  self.replace('filter', {'window' : '', 'filter' : filter, 'show_results' : True, 'page' : 0}),
                  folder=True, cover=cover.search)

        self.item('', self.link('null'),  folder=False, cover=cover.search)

        if(len(filter) > 1):
            url = "%s/" % filter['rubrics'][1]+"filter/"
        else:
            url = "%s/" % filter['rubrics'][1]
        params = []
        for key in filter:
            if(key != 'rubrics' and filter[key][1] != ''):
                params.append(filter[key][1])

        url = url+('/'.join(params))

        print url

        if(show_results == True):
            md5 = hashlib.md5()
            md5.update(url+'?page='+str(page))

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


    def productions_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/countries?v='+CACHE_VERSION)
        productions_list = CACHE(str(md5.hexdigest()), self.get_country_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30141], productions_list['name'])
        return False if ret < 0 else [productions_list['name'][ret], productions_list['href'][ret], ret]

    def genre_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/janrs?v='+CACHE_VERSION)
        genres_list = CACHE(str(md5.hexdigest()), self.get_genre_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30138], genres_list['name'])
        return False if ret < 0 else [genres_list['name'][ret], genres_list['href'][ret], ret]

    def ratings_window(self):
        rating_list = map(str, list(reversed(range(1, 10))))
        rating_names = map(lambda x: xbmcup.app.lang[35005]+' '+x, rating_list)
        rating_list.insert(0, xbmcup.app.lang[30136])
        rating_names.insert(0, xbmcup.app.lang[30136])
        ret = xbmcup.gui.select(xbmcup.app.lang[30140], rating_names)
        return False if ret < 0 else [rating_names[ret], "rating-%s" % str(rating_list[ret]) if ret > 0 else '', ret]

    def years_window(self):
        md5 = hashlib.md5()
        md5.update('/default/index/years?v='+CACHE_VERSION)
        years_list = CACHE(str(md5.hexdigest()), self.get_years_list)
        ret = xbmcup.gui.select(xbmcup.app.lang[30144], years_list['name'])
        return False if ret < 0 else [years_list['name'][ret], years_list['href'][ret], ret]