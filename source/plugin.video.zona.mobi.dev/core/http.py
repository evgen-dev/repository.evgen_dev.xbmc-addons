# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback,base64,math
import xbmcup.app, xbmcup.db, xbmcup.system, xbmcup.net, xbmcup.parser, xbmcup.gui
import xbmc, cover, xbmcplugin, xbmcgui
from common import Render
# from auth import Auth
from defines import *

try:
    cache_minutes = 60*int(xbmcup.app.setting['cache_time'])
except:
    cache_minutes = 0

class HttpData:

    def load(self, url):
        try:
            # self.auth = Auth()
            # self.cookie = self.auth.get_cookies()
            response = xbmcup.net.http.get(url)
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            if(response.status_code == 200):
                # if(self.auth.check_auth(response.text) == False):
                #     self.auth.autorize()
                return response.text
            return None

    def post(self, url, data):
        try:
            data
        except:
            data = {}
        try:
            # self.auth = Auth()
            # self.cookie = self.auth.get_cookies()
            response = xbmcup.net.http.post(url, data)
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            if(response.status_code == 200):
                # if(self.auth.check_auth(response.text) == False):
                #     self.auth.autorize()
                return response.text
            return None


    def ajax(self, url, data={}):
        try:
            # self.auth = Auth()
            # self.cookie = self.auth.get_cookies()
            headers = {
                'X-Requested-With' : 'XMLHttpRequest'
            }
            if(len(data) > 0):
                response = xbmcup.net.http.post(url, data, headers=headers)
            else:
                response = xbmcup.net.http.get(url, headers=headers)
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            return response.text if response.status_code == 200 else None

    def get_movies(self, url, page, idname='results', nocache=False, search="", itemclassname="results-item-wrap"):
        page = int(page)

        if(page > 0 and search == ''):
            url = SITE_URL+"/"+url.strip('/')+"?page="+str(page+1)
        else:
            url = SITE_URL+"/"+url.strip('/')

        if(search != ''):
            html = self.load(url)
        else:
            html = self.load(url)

        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        result = {'page': {}, 'data': []}
        soup = xbmcup.parser.html(self.strip_scripts(html))
        # print soup
        result['page'] = self.get_page(soup)
        if(idname != ''):
            center_menu = soup.find('ul', class_=idname)
        else:
            center_menu = soup

        try:
            for div in center_menu.find_all('li', class_=itemclassname):
                if(itemclassname == 'vlist-item'):
                    href = div.find('a', class_='main-list-link')
                    name = href.find('h3', class_='main-list-title').get_text().strip()

                    try:
                        rating = div.find('span', class_='main-list-rating').get_text().strip()
                    except:
                        rating = 0

                    dop_information = []
                    try:
                        year = div.find('span', class_='main-list-year').get_text().strip()
                        dop_information.append(year)
                    except:
                        pass

                else:
                    href = div.find('a', class_='results-item')

                    dop_information = []
                    try:
                        year = div.find('span', class_='results-item-year').get_text().strip()
                        dop_information.append(year)
                    except:
                        pass

                    try:
                        rating = div.find('span', class_='results-item-rating').find('span').get_text().strip()
                    except:
                        rating = 0
                    # name= ''
                    name = href.find('div', class_='results-item-title').get_text().strip()

                information = ''
                if(len(dop_information) > 0):
                    information = '[COLOR white]['+', '.join(dop_information)+'][/COLOR]'

                try:
                    movieposter = div.find('meta', attrs={'itemprop' : 'image'}).get('content')
                except:
                    movieposter = None

                movie_url = href.get('href'),
                movie_id = movie_url[0]

                result['data'].append({
                        'url': movie_url[0],
                        'id': movie_id,
                        'rating': self.format_rating(rating),
                        'year': information,
                        'name': name,
                        'img': None if not movieposter else movieposter
                    })
        except:
            print traceback.format_exc()

        if(nocache):
            return None, result
        else:
            return cache_minutes, result

    def get_season_movies(self, url, issoup=False):
        if(issoup == False):
            html = self.load('%s%s' % (SITE_URL, url))
            html = html.encode('utf-8')
            soup = xbmcup.parser.html(self.strip_scripts(html))
        else:
            soup = url

        episodes = soup.find('ul', class_='js-episodes').find_all('li')

        current_movie = {}

        for episode in episodes:
            link = episode.find('a', class_='entity-episode-link')
            video_id = link.get('data-id')
            name = episode.find('div', class_='entity-episode-name').get_text().strip()
            name = re.sub('\s+', ' ', name)

            try:
                current_movie['1080'].append([video_id, name])
            except:
                current_movie['1080'] = []
                current_movie['1080'].append([video_id, name])

            # try:
            #     current_movie['480'].append([video_id, name])
            # except:
            #     current_movie['480'] = []
            #     current_movie['480'].append([video_id, name])

        if(issoup):
            return current_movie
        else:
            return cache_minutes, current_movie


    def get_movie_info(self, url):
        html = self.load('%s%s' % (SITE_URL, url))
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

        isSerial = True
        try:
            try:
                seasons = soup.find('div', class_='entity-seasons').find_all('span')
                seasons[0].get_text()
            except:
                seasons = soup.find('div', class_='entity-seasons').find_all('a')
        except:
            isSerial = False

        try:
            video_id = soup.find('div', class_='entity-player').get('data-id')
        except:
            xbmcup.gui.message('Не найден идентификатор видео')
            return

        js_string = self.ajax('%s/ajax/video/%s' % (SITE_URL, video_id))
        movies = json.loads(js_string, 'utf-8')

        if(isSerial):
            for season in seasons:
                season_num = season.get_text().strip()

                s_url = season.get('href')
                if(s_url == None):
                    s_url = url

                current_movie = {
                    'folder_title'  : xbmcup.app.lang[35006]+' '+season_num,
                    'folder_url'    : s_url,
                    'movies'        : self.get_season_movies(soup, True),
                    'isSerial'      : True
                }
                movieInfo['movies'].append(current_movie)

        else:
            current_movie = {
                    'folder_title'  : '',
                    'folder_url'    : '',
                    'movies'        : {},
                    'isSerial'      : False
                }

            current_movie['movies']['1080'] = []
            # current_movie['movies']['480'] = []

            current_movie['movies']['1080'].append([movies['url']])
            # current_movie['movies']['480'].append([movies['lqUrl']])

            movieInfo['movies'].append(current_movie)

        movieInfo['title'] = soup.find('h1', class_='entity-title-text').find('span', class_='js-title').get_text()

        try:
            movieInfo['originaltitle'] = soup.find('h1', class_='entity-title-text').find('meta', attrs={'itemprop' : 'alternativeHeadline'}).get('content')
        except:
            movieInfo['originaltitle'] = ''

        try:
            movieInfo['description'] = soup.find('div', class_='entity-desc-description').get_text().strip()
        except:
            movieInfo['description'] = ''

        try:
            movieInfo['fanart'] = movies['images'][0]
        except:
            movieInfo['fanart'] = ''

        try:
            cover = soup.find('div', class_='entity-desc-poster-img').get('style')
            prog = re.compile('(https?://[^\)]+)', re.I)
            result = prog.findall(cover)
            movieInfo['cover'] = result[0]
        except:
            movieInfo['cover'] = ''

        try:
            movieInfo['genres'] = []
            genres = soup.find('dd', class_='js-genres').find_all('a')
            for genre in genres:
               movieInfo['genres'].append(genre.find('span').get_text().strip())
            movieInfo['genres'] = ' '.join(movieInfo['genres']).encode('utf-8')
        except:
            movieInfo['genres'] = ''

        try:
            movieInfo['year'] = soup.find('div', class_='year').find('a').get_text()
        except:
            movieInfo['year'] = ''

        try:
            movieInfo['durarion'] = int(math.ceil(int(movies['duration'])/60))
        except:
            movieInfo['durarion'] = ''

        try:
            movieInfo['ratingValue'] = float(soup.find(attrs={'itemprop' : 'ratingValue'}).get('content'))
        except:
            movieInfo['ratingValue'] = 0

        try:
            movieInfo['ratingCount'] = int(soup.find(attrs={'itemprop' : 'ratingCount'}).get('content'))
        except:
            movieInfo['ratingCount'] = 0

        try:
            movieInfo['director'] = []
            directors = soup.find('dd', class_='js-scenarist').find_all('span')
            for director in directors:
               movieInfo['director'].append(director.find('span').get_text().strip())
            movieInfo['director'] = ', '.join(movieInfo['director']).encode('utf-8')
        except:
            movieInfo['director'] = ''
        return movieInfo


    def strip_scripts(self, html):
        #удаляет все теги <script></script> и их содержимое
        #сделал для того, что бы html parser не ломал голову на тегах в js
        return re.compile(r'<script[^>]*>(.*?)</script>', re.S).sub('', html)

    def format_rating(self, rating):
        rating = float(rating)
        if(rating == 0): return ''
        if(rating < 4):
            q = 'ffDE4B64'
        elif(rating < 7):
            q = 'ffFFB119'
        else:
            q = 'ff59C641'
        return "[COLOR %s][%s][/COLOR]" % (q, rating)



    def get_page(self, soup):
        info = {'pagenum' : 0, 'maxpage' : 0}
        try:
            wrap  = soup.find('div', class_='js-pageInfo')
            info['pagenum'] = int(wrap.get('data-current').encode('utf-8'))
            info['maxpage'] = int(wrap.get('data-total'))
        except:
            info['pagenum'] = 1
            info['maxpage'] = 1
            print traceback.format_exc()
        return info

class ResolveLink(xbmcup.app.Handler, HttpData, Render):
    def handle(self):
        xbmcup.gui.progress(xbmcup.app.addon.name, 'Открытие потока...')
        xbmcup.gui.progress.render()
        self.params = self.argv[0]
        is_hd = self.params['quality'] == '1080'
        js_string = self.ajax('%s/ajax/video/%s' % (SITE_URL, self.params['movie'][0]))
        movies = json.loads(js_string, 'utf-8')
        xbmcup.gui.progress.close()
        try:
            # if(is_hd and movies['url']):
            return movies['url']
            # else:
            #     return movies['lqUrl']
        except:
            xbmcup.gui.message(movies['error'].encode('utf8'))
            return None