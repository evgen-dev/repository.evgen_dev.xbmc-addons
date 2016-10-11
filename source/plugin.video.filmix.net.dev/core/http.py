# -*- coding: utf-8 -*-

import os, re, sys, json, urllib, hashlib, traceback,base64
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

    def post(self, url, data):
        try:
            data
        except:
            data = {}
        try:
            self.auth = Auth()
            self.cookie = self.auth.get_cookies()
            response = xbmcup.net.http.post(url, data, cookies=self.cookie)
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            if(response.status_code == 200):
                if(self.auth.check_auth(response.text) == False):
                    self.auth.autorize()
                return response.text
            return None


    def ajax(self, url, data={}):
        try:
            self.auth = Auth()
            self.cookie = self.auth.get_cookies()
            headers = {
                'X-Requested-With' : 'XMLHttpRequest'
            }
            if(len(data) > 0):
                response = xbmcup.net.http.post(url, data, cookies=self.cookie, headers=headers)
            else:
                response = xbmcup.net.http.get(url, cookies=self.cookie, headers=headers)
        except xbmcup.net.http.exceptions.RequestException:
            print traceback.format_exc()
            return None
        else:
            return response.text if response.status_code == 200 else None

    def get_movies(self, url, page, idname='dle-content', nocache=False, search="", itemclassname="shortstory"):
        page = int(page)

        if(page > 0 and search == ''):
            url = SITE_URL+"/"+url.strip('/')+"/page/"+str(page+1)
        else:
            url = SITE_URL+"/"+url.strip('/')

        print url

        if(search != ''):
            html = self.ajax(url)
        else:
            html = self.load(url)

        #print html.encode('utf-8')
        print url

        if not html:
            return None, {'page': {'pagenum' : 0, 'maxpage' : 0}, 'data': []}
        result = {'page': {}, 'data': []}
        soup = xbmcup.parser.html(self.strip_scripts(html))

        if(search != ''):
            result['page'] = self.get_page_search(soup)
        else:
            result['page'] = self.get_page(soup)

        if(idname != ''):
            center_menu = soup.find('div', id=idname)
        else:
            center_menu = soup
        try:
            for div in center_menu.find_all('article', class_=itemclassname):
                href = div.find('div', class_='short')#.find('a')

                movie_name = div.find('div', class_='full').find('h3', class_='name').find('a').get_text()

                not_movie = True
                try:
                    not_movie_test = div.find('span', class_='not-movie').get_text()
                except:
                    not_movie = False

                try:
                    quality = div.find('div', class_='full').find('div', class_='quality').get_text().strip()
                except:
                    quality = ''

                dop_information = []
                try:
                    year = div.find('div', class_='item year').find('a').get_text().strip()
                    dop_information.append(year)
                except:
                    pass

                try:
                    genre = div.find('div', class_='category').find(class_='item-content').get_text().strip()
                    dop_information.append(genre)
                except:
                    print traceback.format_exc()

                information = ''
                if(len(dop_information) > 0):
                    information = '[COLOR white]['+', '.join(dop_information)+'][/COLOR]'

                movieposter = SITE_URL+href.find('img', class_='poster').get('src')

                movie_url = href.find('a').get('href'),
                movie_id = re.compile('/([\d]+)-', re.S).findall(movie_url[0])[0]

                result['data'].append({
                        'url': movie_url[0],
                        'id': movie_id,
                        'not_movie': not_movie,
                        'quality': self.format_quality(quality),
                        'year': information,
                        'name': movie_name.strip(),
                        'img': None if not movieposter else movieposter
                    })
        except:
            print traceback.format_exc()

        if(nocache):
            return None, result
        else:
            return cache_minutes, result

    def decode_direct_media_url(self, encoded_url):
        codec_a = ("l", "u", "T", "D", "Q", "H", "0", "3", "G", "1", "f", "M", "p", "U", "a", "I", "6", "k", "d", "s", "b", "W", "5", "e", "y", "=")
        codec_b = ("w", "g", "i", "Z", "c", "R", "z", "v", "x", "n", "N", "2", "8", "J", "X", "t", "9", "V", "7", "4", "B", "m", "Y", "o", "L", "h")
        i = 0
        for a in codec_a:
            b = codec_b[i]
            i += 1
            encoded_url = encoded_url.replace(a, '___')
            encoded_url = encoded_url.replace(b, a)
            encoded_url = encoded_url.replace('___', b)

        return base64.b64decode(encoded_url)

    def format_direct_link(self, source_link, q):
        regex = re.compile("\[([^\]]+)\]", re.IGNORECASE)
        return regex.sub(q, source_link)

    def get_qualitys(self, source_link):
        try:
            avail_quality = re.compile("\[([^\]]+)\]", re.S).findall(source_link)[0]
            return avail_quality.split(',')
        except:
            return '0'.split()

    def get_movie_info(self, url):
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

        #print self.strip_scripts(html)

        try:
            try:
                js_string = self.decode_direct_media_url(re.compile("videoLink = '([^\']+)';", re.S).findall(html)[0].decode('string_escape').decode('utf-8'))
            except:
                try:
                    js_string = self.decode_direct_media_url(re.compile("plLink = '([^\']+)';", re.S).findall(html)[0].decode('string_escape').decode('utf-8'))
                except:
                    movieInfo['no_files'] = xbmcup.app.lang[34026].encode('utf8')
                    raise

            if(js_string.find('.txt') != -1):
                playlist = self.decode_direct_media_url(self.load(js_string))

                movies = json.loads(playlist, 'utf-8')
                for season in movies['playlist']:
                    current_movie = {'folder_title' : season['comment'], 'movies': {}}

                    for movie in season['playlist']:
                        avail_quality = self.get_qualitys(movie['file'])
                        for q in avail_quality:
                            if(q == ''): continue
                            direct_link = self.format_direct_link(movie['file'], q) if q != 0 else movie['file']
                            try:
                                current_movie['movies'][q].append(direct_link)
                            except:
                                current_movie['movies'][q] = []
                                current_movie['movies'][q].append(direct_link)


                    #for resulut in current_movie['movies']:
                    #    current_movie['movies'][resulut] = current_movie['movies'][resulut][0]

                    movieInfo['movies'].append(current_movie)

            elif(js_string.find('http://') != -1):
                avail_quality = self.get_qualitys(js_string)
                current_movie = {'folder_title' : '1', 'movies': {}}
                for q in avail_quality:
                    if(q == ''): continue
                    direct_link = self.format_direct_link(js_string, q) if q != 0 else js_string
                    try:
                        current_movie['movies'][q].append(direct_link)
                    except:
                        current_movie['movies'][q] = []
                        current_movie['movies'][q].append(direct_link)

                movieInfo['movies'].append(current_movie)

            movieInfo['title'] = soup.find('div', class_='name').get_text()
            try:
                movieInfo['originaltitle'] = soup.find('div', class_='origin-name').get_text().strip()
            except:
                movieInfo['originaltitle'] = ''

            try:
                movieInfo['description'] = soup.find('div', class_='full-story').get_text().strip()
            except:
                movieInfo['description'] = ''

            try:
                movieInfo['fanart'] = SITE_URL+soup.find('ul', class_='frames-list').find('a').get('href')
            except:
                movieInfo['fanart'] = ''
            try:
                movieInfo['cover'] = SITE_URL+soup.find('img', class_='poster').get('src')
            except:
                movieInfo['cover'] = ''

            try:
                movieInfo['genres'] = []
                genres = soup.find('div', class_='category').find_all('a')
                for genre in genres:
                   movieInfo['genres'].append(genre.get_text().strip())
                movieInfo['genres'] = ' / '.join(movieInfo['genres']).encode('utf-8')
            except:
                movieInfo['genres'] = ''

            try:
                movieInfo['year'] = soup.find('div', class_='year').find('a').get_text()
            except:
                movieInfo['year'] = ''

            try:
                movieInfo['durarion'] = soup.find('div', class_='durarion').get('content')
                movieInfo['durarion'] = int(movieInfo['durarion'])*60
            except:
                movieInfo['durarion'] = ''

            try:
                movieInfo['ratingValue'] = float(soup.find(attrs={'itemprop' : 'ratingValue'}).get_text())
            except:
                movieInfo['ratingValue'] = 0

            try:
                movieInfo['ratingCount'] = int(soup.find(attrs={'itemprop' : 'ratingCount'}).get_text())
            except:
                movieInfo['ratingCount'] = 0

            try:
                movieInfo['director'] = []
                directors = soup.find('div', class_='directors').findAll('a')
                for director in directors:
                   movieInfo['director'].append(director.get_text().strip())
                movieInfo['director'] = ', '.join(movieInfo['director']).encode('utf-8')
            except:
                movieInfo['director'] = ''
        except:
            print traceback.format_exc()

        print movieInfo

        return movieInfo

    def get_modal_info(self, url):
        html = self.load(url)
        movieInfo = {}
        movieInfo['error'] = False
        if not html:
            movieInfo['error'] = True
            return movieInfo

        html = html.encode('utf-8')
        soup = xbmcup.parser.html(self.strip_scripts(html))

        try:
            movieInfo['desc'] = soup.find('div', class_='full-story').get_text().strip()
        except:
            movieInfo['desc'] = ''

        try:
            movieInfo['title'] = soup.find('h1', class_='name').get_text()
        except:
            movieInfo['title'] = ''

        try:
            movieInfo['originaltitle'] = soup.find('div', class_='origin-name').get_text().strip()
        except:
            movieInfo['originaltitle'] = ''

        if(movieInfo['originaltitle'] != ''):
             movieInfo['title'] = '%s / %s' % (movieInfo['title'],  movieInfo['originaltitle'])

        try:
            movieInfo['poster'] = SITE_URL+soup.find('img', class_='poster').get('src')
        except:
            movieInfo['poster'] = ''

        movieInfo['desc'] = ''
        try:
            infos = soup.find('div', class_='full min').find_all('div', class_="item")
            skip = True
            for div in infos:
                if(skip):
                    skip = False
                    continue
                movieInfo['desc'] += self.format_desc_item(div.get_text().strip())+"\n"
        except:
           movieInfo['desc'] = traceback.format_exc()

        try:
            div = soup.find('div', class_='full-panel').find('span', class_='kinopoisk')
            rvalue = div.find('div', attrs={'itemprop' : 'ratingValue'}).get_text().strip()
            rcount = div.find('div', attrs={'itemprop' : 'ratingCount'}).get_text().strip()
            kp = xbmcup.app.lang[34029] % (self.format_rating(rvalue), rvalue, rcount)
            movieInfo['desc'] += kp+"\n"
        except:
            pass

        try:
            div = soup.find('div', class_='full-panel').find('span', class_='imdb').find_all('div')
            rvalue = div[0].get_text().strip()
            rcount = div[1].get_text().strip()
            kp = xbmcup.app.lang[34030] % (self.format_rating(rvalue), rvalue, rcount)
            movieInfo['desc'] += kp+"\n"
        except:
            pass

        try:
            desc = soup.find('div', class_='full-story').get_text().strip()
            movieInfo['desc'] += '\n[COLOR blue]%s[/COLOR]\n%s' % (xbmcup.app.lang[34027], desc)
        except:
            movieInfo['desc'] = traceback.format_exc()

        try:
            movieInfo['trailer'] = soup.find('li', attrs={'data-id' : "trailers"}).find('a').get('href')
        except:
            movieInfo['trailer'] = False

        return movieInfo

    def my_int(self, str):
        if(str == ''):
            return 0
        return int(str)

    def get_trailer(self, url):
        progress = xbmcgui.DialogProgress()
        progress.create(xbmcup.app.addon['name'])
        progress.update(0)
        html = self.load(url)
        movieInfo = {}
        movieInfo['error'] = False
        if not html:
            xbmcup.gui.message(xbmcup.app.lang[34031].encode('utf8'))
            progress.update(0)
            progress.close()
            return False

        progress.update(50)
        html = html.encode('utf-8')
        soup = xbmcup.parser.html(self.strip_scripts(html))

        link = self.decode_direct_media_url(soup.find('input', id='video-link').get('value'))
        avail_quality = max(map(self.my_int, self.get_qualitys(link)))
        progress.update(100)
        progress.close()
        return self.format_direct_link(link, str(avail_quality))

    def format_desc_item(self, text):
        return re.compile(r'^([^:]+:)', re.S).sub('[COLOR blue]\\1[/COLOR] ', text)


    def strip_scripts(self, html):
        html = re.compile(r'<head[^>]*>(.*?)</head>', re.S).sub('<head></head>', html)
        #удаляет все теги <script></script> и их содержимое
        #сделал для того, что бы html parser не ломал голову на тегах в js
        return re.compile(r'<script[^>]*>(.*?)</script>', re.S).sub('', html)

    def format_rating(self, rating):
        rating = float(rating)
        if(rating == 0):
            return 'white'
        elif(rating > 7):
            return 'ff59C641'
        elif(rating > 4):
            return 'ffFFB119'
        else:
            return 'ffDE4B64'


    def format_quality(self, quality):
        if(quality == ''): return ''
        if(quality.find('1080') != -1):
            q = 'HD'
        elif(quality.find('720') != -1):
            q = 'HQ'
        elif(quality.find('480') != -1):
            q = 'SQ'
        else:
            q = 'LQ'

        qualitys = {'HD' : 'ff3BADEE', 'HQ' : 'ff59C641', 'SQ' : 'ffFFB119', 'LQ' : 'ffDE4B64'}
        if(q in qualitys):
            return "[COLOR %s][%s][/COLOR]" % (qualitys[q], quality)
        return ("[COLOR ffDE4B64][%s][/COLOR]" % quality if quality != '' else '')


    def get_page(self, soup):
        info = {'pagenum' : 0, 'maxpage' : 0}
        try:
            wrap  = soup.find('div', class_='navigation')
            info['pagenum'] = int(wrap.find('span', class_='').get_text())
            try:
                info['maxpage'] = len(wrap.find('a', class_='next'))
                if(info['maxpage'] > 0):
                    info['maxpage'] = info['pagenum']+1
            except:
                info['maxpage'] = info['pagenum']
                print traceback.format_exc()

        except:
            info['pagenum'] = 1
            info['maxpage'] = 1
            print traceback.format_exc()

        return info


    def get_page_search(self, soup):
        info = {'pagenum' : 0, 'maxpage' : 0}
        try:
            wrap  = soup.find('div', class_='navigation')
            current_page = wrap.find_all('span', class_='')
            info['pagenum'] = 1
            for cpage in current_page:
                if(cpage.get_text().find('...') == -1):
                    info['pagenum'] = int(cpage.get_text())
                    break

            try:
                clicks = wrap.find_all('span', class_='click')
                pages = []
                for page in clicks:
                    pages.append(int(page.get_text()))

                info['maxpage'] = max(pages)
            except:
                info['maxpage'] = info['pagenum']
                print traceback.format_exc()

        except:
            info['pagenum'] = 1
            info['maxpage'] = 1
            print traceback.format_exc()

        return info