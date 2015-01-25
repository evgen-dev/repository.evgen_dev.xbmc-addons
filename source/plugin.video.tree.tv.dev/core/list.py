# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from common import Render
from defines import *

CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))

try:
    cache_minutes = 60*int(xbmcup.app.setting['cache_time'])
except:
    cache_minutes = 0

class Paginator(xbmcup.app.Handler):
    def __init__(self, soup):
       self.soup = soup

    def get_page(self):
        info = {'pagenum' : 0, 'maxpage' : 0}
        try:
            wrap  = self.soup.find('div', class_='paginationControl')
            info['pagenum'] = int(wrap.find('b').get_text().encode('utf-8'))
            try:
                info['maxpage'] = int(wrap.find('a', class_='last').get('rel')[0])
            except:
                info['maxpage'] = int(os.path.basename(wrap.find('a', class_='next').get('href')))
        except:
            info['pagenum'] = 1
            info['maxpage'] = 1
            print traceback.format_exc()
        print info
        return info

class HttpData:
    def load(self, url):
        try:
            response = xbmcup.net.http.get(url)
        except xbmcup.net.http.exceptions.RequestException:
            return None
        else:
            return response.text if response.status_code == 200 else None

    def get_movies(self, url, page):
        url = SITE_URL+"/"+url.strip('/')+"/page/"+str(page+1)
        print url
        html = self.load(url)
        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        result = {'page': {}, 'data': []}
        soup = xbmcup.parser.html(self.strip_scripts(html))
        result['page'] = Paginator(soup).get_page()
        center_menu = soup.find('div', class_='main_content_item')
        try:
            for div in center_menu.find_all('div', class_='item'):
                href = div.find('h2').find('a')
                try:
                    quality = div.find('span', class_='quality_film_title').get_text().strip()
                except:
                    quality = ''

                dop_information = []
                try:
                    year = div.find('div', class_='smoll_year').get_text().strip()
                    dop_information.append(year)
                except:
                    pass

                try:
                    genre = div.find('div', class_='smoll_janr').get_text().strip()
                    dop_information.append(genre)
                except:
                    pass

                information = ''
                if(len(dop_information) > 0):
                    information = '[COLOR white]['+', '.join(dop_information)+'][/COLOR]'

                posters = div.find('div', class_='preview').find_all('img')
                movieposter = None
                for img in posters:
                    img_src = img.get('src')
                    if(img_src.find('/public/') != -1):
                        movieposter = img_src;
                        break

                result['data'].append({
                        'url': href.get('href'),
                        'quality': self.format_quality(quality),
                        'year': information,
                        'name': href.get_text().strip(),
                        'img': None if not movieposter else (SITE_URL + movieposter)
                    })
        except:
            print traceback.format_exc()

        return cache_minutes, result


    def get_movie_info(self, url):
        url = SITE_URL+"/"+url
        html = self.load(url).encode('utf-8')
        movieInfo = {}
        movieInfo['no_files'] = None
        soup = xbmcup.parser.html(self.strip_scripts(html))

        js_string = re.compile("'source' : \$\.parseJSON\('([^\']+)'\)", re.S).findall(html)[0].decode('string_escape').decode('utf-8')
        movies = json.loads(js_string, 'utf-8')
        movieInfo['episodes'] = True
        movieInfo['movies'] = []
        movieInfo['resolutions'] = []
        print movies
        if(movies != None and len(movies) > 0):
            for window_id in movies:
                current_movie = {'folder_title' : '', 'movies': {}}
                try:
                    current_movie['folder_title'] = soup.find('div', {'data-folder': str(window_id)}).find('a').get('title').encode('utf-8')
                except:
                    current_movie['folder_title'] = xbmcup.app.lang[30113]

                sort_movies = sorted(movies[window_id].items(), key=lambda (k,v): int(k))
                for movie in sort_movies:
                    try:
                        current_movie['movies'][movie[0]].append(movie[1])
                    except:
                        current_movie['movies'][movie[0]] = []
                        current_movie['movies'][movie[0]].append(movie[1])

                for resulut in current_movie['movies']:
                    current_movie['movies'][resulut] = current_movie['movies'][resulut][0]
                    # if(len(current_movie['movies'][resulut]) > 1):
                    #     movieInfo['episodes'] = True

                movieInfo['movies'].append(current_movie)

            movieInfo['title'] = soup.find('h1', id='film_object_name').get_text()
            try:
                movieInfo['description'] = soup.find('div', class_='description').get_text().strip()
            except:
                movieInfo['description'] = ''

            try:
                movieInfo['fanart'] = SITE_URL+soup.find('div', class_='screen_bg').find('a').get('href')
            except:
                movieInfo['fanart'] = ''
            try:
                movieInfo['cover'] = SITE_URL+soup.find('img', id='preview_img').get('src')
            except:
                movieInfo['cover'] = ''
            try:
                movieInfo['genres'] = []
                genres = soup.find('div', class_='list_janr').findAll('a')
                for genre in genres:
                   movieInfo['genres'].append(genre.get_text().strip())
                movieInfo['genres'] = ' / '.join(movieInfo['genres']).encode('utf-8')
            except:
                movieInfo['genres'] = ''

            try:
                results = soup.findAll('a', class_='fast_search')
                movieInfo['year'] = self.get_year(results)
            except:
                movieInfo['year'] = ''
            try:
                movieInfo['director'] = soup.find('span', class_='regiser_item').get_text().encode('utf-8')
            except:
                movieInfo['director'] = ''
        else:
            try:
                no_files = soup.find('div', class_='no_files').get_text().strip().encode('utf-8')
            except:
                no_files = ''

            movieInfo['no_files'] = no_files

        return movieInfo

    def get_collections(self):
        url = SITE_URL+"/collection"
        html = self.load(url).encode('utf-8')
        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        result = {'page': {}, 'data': []}
        soup = xbmcup.parser.html(self.strip_scripts(html))
        wrap = soup.find('div', class_='main_content_item')
        try:
            for div in wrap.find_all('div', class_='item'):
                try:
                    preview_img = div.find('div', class_='preview').find('img').get('src')
                except:
                    preview_img = ''

                try:
                    movie_count = div.find('div', class_='item_content').find('span').get_text().strip()
                except:
                    movie_count = ''

                try:
                    href = div.find('div', class_='item_content').find('a')
                    name = href.get_text().strip()+(' (%s)' % movie_count if movie_count != '' else '')
                    href = href.get('href')
                except:
                    name = ''
                    href = ''

                result['data'].append({
                        'url': href,
                        'name': name,
                        'img': None if not preview_img else (SITE_URL + preview_img)
                    })

        except:
            print traceback.format_exc()

        return cache_minutes, result

    def get_year(self, results):
        for res in results:
            if(res.get('rel')[0] == 'year1'):
                return res.get_text().encode('utf-8')
        return 0

    def strip_scripts(self, html):
        #удаляет все теги <script></script> и их содержимое
        #сделал для того, что бы parser не ломал голову на тегах в js
        return re.compile(r'<script[^>]*>(.*?)</script>', re.S).sub('', html)

    def format_quality(self, quality):
        qualitys = {'HD' : 'ff3BADEE', 'HQ' : 'ff59C641', 'SQ' : 'ffFFB119', 'LQ' : 'ffDE4B64'}
        if(quality in qualitys):
            return "[COLOR %s][%s][/COLOR]" % (qualitys[quality], quality)
        return ("[COLOR ffDE4B64][%s][/COLOR]" % quality if quality != '' else '')

class CollectionList(xbmcup.app.Handler, HttpData, Render):
    def handle(self):
        params = self.argv[0]
        try:
            url = params['url']
        except:
            url = ''

        if(url == ''):
           self.show_dirs()
        else:
            self.show_movies(url)

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

    def show_movies(self, url):
        md5 = hashlib.md5()
        md5.update(url)
        response = CACHE(str(md5.hexdigest()), self.get_movies, url, 0)
        if(len(response['data']) > 0):
            for movie in response['data']:
                self.item(movie['name']+' '+movie['year']+' '+movie['quality'],
                          self.link('quality-list', {'movie_page' : movie['url'], 'cover' : movie['img']}),
                          folder=True, cover=movie['img'])
        else:
            self.item(u'[COLOR red]['+xbmcup.app.lang[30111]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)


class MovieList(xbmcup.app.Handler, HttpData, Render):
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

        if(len(response['data']) > 0):
            for movie in response['data']:
                self.item(movie['name']+' '+movie['year']+' '+movie['quality'],
                          self.link('quality-list', {'movie_page' : movie['url'], 'cover' : movie['img']}),
                          folder=True, cover=movie['img'])

            params['page'] = page+1
            if(response['page']['maxpage'] >= response['page']['pagenum']+1):
                self.item('[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]', self.replace('list', params), cover=cover.next)
        else:
            self.item(u'[COLOR red]['+xbmcup.app.lang[30111]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)

class SearchList(xbmcup.app.Handler, HttpData, Render):
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
            usersearch = params['usersearch']
            vsearch = params['vsearch']
        except:
            keyboard = xbmc.Keyboard()
            keyboard.setHeading(xbmcup.app.lang[30112])
            keyboard.doModal()
            usersearch = keyboard.getText(0)
            vsearch = usersearch.decode('utf-8')
            params['vsearch'] = vsearch
            params['usersearch'] = urllib.quote_plus(usersearch)

        if not usersearch: return False

        page_url = "search/index/index/usersearch/"+params['usersearch']

        md5 = hashlib.md5()
        md5.update(page_url+'/page/'+str(page))
        response = CACHE(str(md5.hexdigest()), self.get_movies, page_url, page)

        self.item(u'[COLOR yellow]'+xbmcup.app.lang[30108]+'[/COLOR]', self.link('search'), folder=True, cover=cover.search)
        self.item('[COLOR blue]['+xbmcup.app.lang[30109]+': '+vsearch+'][/COLOR]',
                  self.link('null'), folder=False, cover=cover.info)

        if(response['page']['pagenum'] > 1):
            params['page'] = page-1
            self.item('[COLOR green]'+xbmcup.app.lang[30106]+'[/COLOR]', self.replace('search', params), cover=cover.prev)
            params['page'] = page+1
        if(len(response['data']) > 0):
            for movie in response['data']:
                self.item(movie['name']+' '+movie['year']+' '+movie['quality'],
                          self.link('quality-list', {'movie_page' : movie['url'], 'cover' : movie['img']}),
                          folder=True, cover=movie['img'])

            params['page'] = page+1
            if(response['page']['maxpage'] >= response['page']['pagenum']+1):
                self.item(u'[COLOR green]'+xbmcup.app.lang[30107]+'[/COLOR]', self.replace('search', params), cover=cover.next)
        else:
            self.item(u'[COLOR red]['+xbmcup.app.lang[30110]+'][/COLOR]', self.link('null'), folder=False, cover=cover.info)


class QualityList(xbmcup.app.Handler, HttpData, Render):

    def get_icon(self, quality):
        if(quality in cover.res_icon):
            return cover.res_icon[quality]
        else:
            return cover.res_icon['default']

    def handle(self):
        self.params = self.argv[0]
        print self.argv[0]
        try:
            self.movieInfo = self.params['movieInfo']
        except:
            self.movieInfo = self.get_movie_info(self.params['movie_page'])

        try:
            self.params['sub_dir'] = int(self.params['sub_dir'])
        except:
            self.params['sub_dir'] = None

        try:
            self.params['quality_dir'] = int(self.params['quality_dir'])
        except:
            self.params['quality_dir'] = None

        if(self.params['sub_dir'] == None):
            self.def_dir = 0
        else:
            self.def_dir=  self.params['sub_dir']

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

        infoLabels = self.get_info()

        if(show_first_quality):
            for quality in movies:
                for movie in movies[quality]:
                    self.add_playable_item(movie)
                break
        else:
            for movie in movies:
                self.add_playable_item(movie)

        #xbmcplayer.player.onPlayBackEnded()
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
        self.item(os.path.basename(str(movie)),
                           movie,
                           folder=False,
                           media='video',
                           info=self.get_info(),
                           cover = self.movieInfo['cover'],
                           fanart = self.movieInfo['fanart']
                    )
