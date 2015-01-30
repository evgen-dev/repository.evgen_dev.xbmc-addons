# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from common import Render
from auth import Auth
from defines import *

try:
    cache_minutes = 60*int(xbmcup.app.setting['cache_time'])
except:
    cache_minutes = 0

class HttpData:

    def load(self, url):
        try:
            self.auth = Auth()
            self.cookie = self.auth.get_cookies()
            response = xbmcup.net.http.get(url, cookies=self.cookie)
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            if(response.status_code == 200):
                if(self.auth.check_auth(response.text) == False):
                    self.auth.autorize()
                return response.text
            return None

    def ajax(self, url):
        try:
            self.auth = Auth()
            self.cookie = self.auth.get_cookies()
            headers = {
                'X-Requested-With' : 'XMLHttpRequest'
            }
            response = xbmcup.net.http.get(url, cookies=self.cookie, headers=headers)
            print url
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            return response.text if response.status_code == 200 else None

    def get_movies(self, url, page, classname='main_content_item'):
        page = int(page)
        if(page > 0):
            url = SITE_URL+"/"+url.strip('/')+"/page/"+str(page+1)
        else:
            url = SITE_URL+"/"+url.strip('/')
        print url
        html = self.load(url)

        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        result = {'page': {}, 'data': []}
        soup = xbmcup.parser.html(self.strip_scripts(html))
        result['page'] = self.get_page(soup)
        center_menu = soup.find('div', class_=classname)
        print len(center_menu.find_all('div', class_='item'))
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
                        movieposter = img_src
                        break
                movie_url = href.get('href'),
                movie_id = re.compile('id=([\d]+)', re.S).findall(movie_url[0])[0]

                result['data'].append({
                        'url': movie_url,
                        'id': movie_id,
                        'quality': self.format_quality(quality),
                        'year': information,
                        'name': href.get_text().strip(),
                        'img': None if not movieposter else (SITE_URL + movieposter)
                    })
        except:
            print traceback.format_exc()

        return cache_minutes, result


    def get_movie_info(self, url):
        url = SITE_URL+"/"+url[0]
        html = self.load(url)

        movieInfo = {}
        movieInfo['no_files'] = None
        movieInfo['episodes'] = True
        movieInfo['movies'] = []
        movieInfo['resolutions'] = []

        if not html:
            movieInfo['no_files'] = 'HTTP error'
            return movieInfo

        html = html.encode('utf-8')
        soup = xbmcup.parser.html(self.strip_scripts(html))

        js_string = re.compile("'source' : \$\.parseJSON\('([^\']+)'\)", re.S).findall(html)[0].decode('string_escape').decode('utf-8')
        movies = json.loads(js_string, 'utf-8')
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
        html = self.load(url)
        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        html = html.encode('utf-8')
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


    def get_bookmarks(self):
        url = "%s/users/profile/bookmark" % SITE_URL

        #self.ajax('%s/users/profile/addbookmark?name=%s' % (SITE_URL, BOOKMARK_DIR))

        html = self.load(url)
        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        html = html.encode('utf-8')
        result = {'page': {}, 'data': []}
        soup = xbmcup.parser.html(self.strip_scripts(html))
        wrap = soup.find('div', id='bookmark_list')

        try:
            for div in wrap.find_all('a'):
                try:
                    href = div.get('rel')
                    name = div.get_text().strip()
                except:
                    name = ''
                    href = ''

                result['data'].append({
                        'url': href,
                        'name': name,
                        'img': cover.treetv
                    })

        except:
            print traceback.format_exc()

        return None, result

    def get_year(self, results):
        for res in results:
            if(res.get('rel')[0] == 'year1'):
                return res.get_text().encode('utf-8')
        return 0

    def strip_scripts(self, html):
        #удаляет все теги <script></script> и их содержимое
        #сделал для того, что бы html parser не ломал голову на тегах в js
        return re.compile(r'<script[^>]*>(.*?)</script>', re.S).sub('', html)

    def format_quality(self, quality):
        qualitys = {'HD' : 'ff3BADEE', 'HQ' : 'ff59C641', 'SQ' : 'ffFFB119', 'LQ' : 'ffDE4B64'}
        if(quality in qualitys):
            return "[COLOR %s][%s][/COLOR]" % (qualitys[quality], quality)
        return ("[COLOR ffDE4B64][%s][/COLOR]" % quality if quality != '' else '')


    def get_page(self, soup):
        info = {'pagenum' : 0, 'maxpage' : 0}
        try:
            wrap  = soup.find('div', class_='paginationControl')
            info['pagenum'] = int(wrap.find('b').get_text().encode('utf-8'))
            try:
                info['maxpage'] = int(wrap.find('a', class_='last').get('rel')[0])
            except:
                info['maxpage'] = int(os.path.basename(wrap.find('a', class_='next').get('href')))
        except:
            info['pagenum'] = 1
            info['maxpage'] = 1
            print traceback.format_exc()

        return info