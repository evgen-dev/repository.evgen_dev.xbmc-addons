# -*- coding: utf-8 -*-

# Импортируем нужные нам библиотеки
import sys, urllib, urllib2, re, os, cookielib, traceback, datetime
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
from DialogXml import *
import __builtin__

def Notificator(title, message, timeout = 500):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(title, message, timeout, plugin_icon))

def Alert(title, message):
    xbmcgui.Dialog().ok(title, message)

__settings__ = xbmcaddon.Addon(id='plugin.video.watch.is.dev')
plugin_path = __settings__.getAddonInfo('path').replace(';', '');
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'addon.py'))
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_watch_is_dev.sid')

username = __settings__.getSetting('username')
password = __settings__.getSetting('password')
detailed_log = __settings__.getSetting('detailed')

def print_log(message):
    if(detailed_log):
        print message

if ( username == "" or password == "" ):
    __settings__.openSettings()
    username = __settings__.getSetting('username')
    password = __settings__.getSetting('password')

if ( username == "" or password == "" ):
    Alert('Вы не авторизованы', 'Укажите логин и пароль в настройках приложения')
    print_log('Пользователь не аторизован. Выход.')
    sys.exit()

siteUrl = "http://watch.is"
authInfo = {'username' : username, 'password' : password, 'login' : ' '}
cookieJar = cookielib.CookieJar()

# Функция для получения исходного кода web-страниц
def request(url, reqData):
    """:rtype : basestring"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Host": "watch.is",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3",
            "Accept-Encoding" : "windows-1251,utf-8;q=0.7,*;q=0.7",
            "Referer": "http://watch.is/login"
        }
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
        conn = urllib2.Request(url, urllib.urlencode(reqData), headers)
        connection = opener.open(conn)
        html = connection.read()
        connection.close()
        return html
    except:
        Notificator('Ошибка HTTP', 'Проверьте подключение к интернету', 3000)
        print_log('Не смог открыть ссылку: '+url)
        print traceback.format_exc()
        sys.exit()

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param

def addLink(title, url):
    item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


def addDir(title, url, mode, page=0, searchValue=''):
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + \
              '&mode=' + urllib.quote_plus(str(mode)) + '&page=' + urllib.quote_plus(str(page))+'&search'+\
              urllib.quote_plus(str(searchValue))

    item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def addDirLink(title, url, mode, page=0, icon="DefaultFolder.png", inbookmarks=False):
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + \
              '&mode=' + urllib.quote_plus(str(mode)) + '&page=' + urllib.quote_plus(str(page))
    id = url.split('/')

    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage='')
    item.setIconImage(siteUrl+'/posters/'+id[1]+'.jpg')


    contextMenuItems = []
    if inbookmarks:
        contextMenuItems.append(('Удалить из закладок', 'XBMC.RunScript(%s,%i,%s)' %
                            (context_path, 1, 'mode=remove_bookmark&url='+id[1])))
    else:
        contextMenuItems.append(('Добавить в закладки', 'XBMC.RunScript(%s,%i,%s)' %
                            (context_path, 1, 'mode=add_bookmark&url='+id[1])))

    item.addContextMenuItems(contextMenuItems, replaceItems=True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=False)

def getBookmarkNum():
    bookmarks = re.compile('<a href="/bookmark">Закладки \(([\d]+)\)</a>',re.S).findall(basicHtml)
    print bookmarks
    if (len(bookmarks) == 0):
        return '0'
    else:
        return bookmarks[0]

def homePage():
    addDir("Поиск", siteUrl, "search")
    addDir("Новые фильмы", siteUrl+'/?genre=0&year='+str(datetime.date.today().year)+'&sorting=added&order=desc', "newmovie")
    addDir("Лучшие фильмы", siteUrl+'/top', "topmovie")
    addDir("Фильмы по рейтингу", siteUrl, "view_rating")
    addDir("Фильмы по жанрам", siteUrl, "genres")
    addDir("Фильмы по годам", siteUrl, "years")
    addDir("Все фильмы", '', "allmovie")
    addDir("Мои закладки ("+getBookmarkNum()+")", siteUrl+'/bookmark', "bookmarks")

def viewGenres():
    genresLinks = re.compile('<li><a href="/genre/([^"]+)">([^<]+)</a></li>',re.S).findall(basicHtml)
    for url, title in genresLinks:
        addDir(title, '/?genre='+url+'&year=0&sorting=&order=&kinopoisk', "view_genre")
    if (len(genresLinks) == 0):
        Notificator('Список пуст', 'Не удалось обнаружить ни одного жанра', 3000)
        print_log('Не удалось обнаружить ни одного жанра')
        return False

def parseMovies(html):
    hd_movies = re.compile('<a href="([^"]+)"><img src="[^"]+" width="105" height="156" alt="" /></a>'+
                        '\n<div class="hd"><img src="/templates/images/hd.png" alt=""></div><div class="info">',re.S).findall(html)

    movies = re.compile('<div class="name"><a href="([^"]+)" class="name"><strong>([^<]+)</strong>',re.S).findall(html)
    views = re.compile('<div class="votes"><img src="/templates/images/vote.png" alt=""><span class="text">([\-\d]+)</span></div>',re.S).findall(html)
    rating = re.compile('<div class="views"><img src="/templates/images/views.png" alt=""><span class="text">([\-\d]+)</span></div>',re.S).findall(html)

    i = 0
    for url, title in movies:
        movies[i] = list(movies[i])
        if(url in hd_movies):
            movies[i][1] = title+' (HD)'

        movies[i][1] = movies[i][1]+' - [COLOR red]%s[/COLOR]' %rating[i] + ' / ' + '[COLOR yellow]%s[/COLOR]' %views[i]
        movies[i] = tuple(movies[i])
        i = i + 1

    return movies

def getMaxPage(html):
    genresPages = re.compile('class="page[^"]*"><span><span>([\d]+)</span>',re.S).findall(html)
    maxPage = 0
    if(len(genresPages) > 0):
        maxPage = int(genresPages[-1:][0])-1
    return maxPage

def viewSelectedGenre(genreUrl, page=0):
    if page > 0:
        addDir('[COLOR blue]<< Первая страница[/COLOR]', genreUrl+'&year=0&sorting=&order=&kinopoisk=', "view_genre", 0)
        addDir('[COLOR green]< Предылущая страница[/COLOR]', genreUrl+'&year=0&sorting=&order=&kinopoisk=', "view_genre", page-1)
    genreHtml =  request(siteUrl+genreUrl+'&page='+str(page), {})

    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info")

    maxPage = getMaxPage(genreHtml)
    if(maxPage > page):
        addDir('[COLOR green]Следущая страница >[/COLOR]', genreUrl+'&year=0&sorting=&order=&kinopoisk=', "view_genre", page+1)
        addDir('[COLOR blue]Последняя страница >>[/COLOR]', genreUrl+'&year=0&sorting=&order=&kinopoisk=', "view_genre", maxPage)


def viewSelectedYear(genreUrl, page=0):
    if page > 0:
        addDir('[COLOR blue]<< Первая страница[/COLOR]', genreUrl+'&sorting=&order=&kinopoisk=', "view_year", 0)
        addDir('[COLOR green]< Предылущая страница[/COLOR]', genreUrl+'&sorting=&order=&kinopoisk=', "view_year", page-1)
    genreHtml =  request(siteUrl+genreUrl+'&page='+str(page), {})

    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info")

    maxPage = getMaxPage(genreHtml)
    if(maxPage > page):
        addDir('[COLOR green]Следущая страница >[/COLOR]', genreUrl+'&sorting=&order=&kinopoisk=', "view_year", page+1)
        addDir('[COLOR blue]Последняя страница >>[/COLOR]', genreUrl+'&sorting=&order=&kinopoisk=', "view_year", maxPage)


def viewOrderByRating(page=0):
    if page > 0:
        addDir('[COLOR blue]<< Первая страница[/COLOR]', '/?genre=0&year=0&sorting=rating&order=desc', "view_rating", 0)
        addDir('[COLOR green]< Предылущая страница[/COLOR]', '/?genre=0&year=0&sorting=rating&order=desc', "view_rating", page-1)
    genreHtml =  request(siteUrl+'/?genre=0&year=0&sorting=rating&order=desc&page='+str(page), {})

    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info")

    maxPage = getMaxPage(genreHtml)
    if(maxPage > page):
        addDir('[COLOR green]Следущая страница >[/COLOR]', '/?genre=0&year=0&sorting=rating&order=desc', "view_rating", page+1)
        addDir('[COLOR blue]Последняя страница >>[/COLOR]', '/?genre=0&year=0&sorting=rating&order=desc', "view_rating", maxPage)


def viewAllMovies(page=0):
    if page > 0:
        addDir('[COLOR blue]<< Первая страница[/COLOR]', '', "allmovie", 0)
        addDir('[COLOR green]< Предылущая страница[/COLOR]', '', "allmovie", page-1)

    genreHtml =  request(siteUrl+'/?page='+str(page), {})
    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info")

    maxPage = getMaxPage(genreHtml)
    if(maxPage > page):
        addDir('[COLOR green]Следущая страница >[/COLOR]', '', "allmovie", page+1)
        addDir('[COLOR blue]Последняя страница >>[/COLOR]', '', "allmovie", maxPage)


def viewTopMovie():
    genreHtml =  request(siteUrl+'/top', {})
    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info")

def viewBookmarks():
    genreHtml =  request(siteUrl+'/bookmark', {})
    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info", inbookmarks=True)

def viewNewMovies(uri):
    genreHtml =  request(uri, {})
    genresMovies = parseMovies(genreHtml)
    for url, title in genresMovies:
        addDirLink(title, url, "movie_info")

def pretty_desc(desc):
    replace = {
            "Название:"         : "[COLOR blue]Название:[/COLOR]",
            "Год:"              : "[COLOR blue]Год:[/COLOR]",
            "Жанр:"             : "[COLOR blue]Жанр:[/COLOR]",
            "Студия/Страна:"    : "[COLOR blue]Студия/Страна:[/COLOR]",
            "Режиссер:"         : "[COLOR blue]Режиссер:[/COLOR]",
            "О фильме:"         : "[COLOR blue]О фильме:[/COLOR]",
            "Перевод:"          : "[COLOR blue]Перевод:[/COLOR]",
            "В ролях:"          : "[COLOR blue]В ролях:[/COLOR]",
            "Длительность:"     : "[COLOR blue]Длительность:[/COLOR]"
        }
    replace = dict((re.escape(k), v) for k, v in replace.iteritems())
    pattern = re.compile("|".join(replace.keys()))
    return pattern.sub(lambda m: replace[re.escape(m.group(0))], desc)

def showMovieInfo(url):
    global progress
    progress.update(50)
    movieHtml =  request(siteUrl+url, {})
    movieInfo = {}
    movieInfo['movieHtml'] = movieHtml
    progress.update(75)
    direct_url = re.compile('file:"([^"]+)"',re.S).findall(movieHtml)

    if(len(direct_url) > 0):
        movieInfo['direct_url'] = direct_url[0];
    else:
        progress.close()
        Alert('Капец...', 'Не удалось найти прямую ссылку на фильм')
        print_log('Нет ссылки на видео: '+url)
        return False

    movieInfo['direct_url_hq'] = False
    hd_quility = re.compile('var flashvars ={"file":"([^\]]+:\[[^\]]+)\]', re.S).findall(movieHtml)
    if(len(hd_quility) > 0):
        contentServer = direct_url[0].split('/watch/')
        movieInfo['direct_url_hq'] = contentServer[0]+'/watch/'+hd_quility[0].split(',')[1]+'?'+direct_url[0].split('?')[1]

    desc_info = re.compile('<div class="opt" id="video-descr">(.*?)</div>',re.S).findall(movieHtml)
    if(len(desc_info) > 0):
        desc_info = desc_info[0].replace("\n", "").replace('<br />', "\n")
        movieInfo['desc'] =  pretty_desc(re.sub(r'<[^>]*?>', '', desc_info))
        del desc_info

    progress.update(85)

    poster = re.compile('<img src="/posters/([^"]+)" class="image-border" alt="" />',re.S).findall(movieHtml)
    if(len(poster) > 0):
        movieInfo['poster'] = siteUrl+'/posters/'+poster[0];
    del poster

    rating = re.compile('<div class="rating-count"><strong id="[^"]*">([^<]+)</strong></div>',re.S).findall(movieHtml)
    if(len(rating) > 0):
        movieInfo['rating'] = rating[0];
    del rating

    views = re.compile('<div class="view">Просмотров: <strong class="color-red">([^<]+)</strong></div>',re.S).findall(movieHtml)
    if(len(views) > 0):
        movieInfo['views'] = views[0];
    del views

    kinopoisk = re.compile('src="(http://(?:www.)?kinopoisk.ru/rating/[^"]+)"',re.S).findall(movieHtml)
    if(len(kinopoisk) > 0):
        movieInfo['kinopoisk'] = kinopoisk[0];
    del kinopoisk

    movietitle = re.compile('<h3 class="content-pad">([^<]+)</h3>',re.S).findall(movieHtml)
    if(len(movietitle) > 0):
        movieInfo['title'] = movietitle[0];
    del movietitle

    progress.update(100)
    progress.close()

    path = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path').replace(';', ''), ''))
    w = DialogXml("movieinfo.xml", path, "Default")
    w.doModal(movieInfo)
    del w
    del movieInfo

def openSearchDialog(page):
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Поиск')
    keyboard.doModal()
    searchValue = keyboard.getText(0)
    #dialog = xbmcgui.Dialog()
    #searchValue = dialog.input('Поиск')
    if not searchValue: return False
    viewSearchResult(searchValue, page)

def viewSearchResult(searchValue, page=0):
    print 'called viewSearchResult("'+searchValue+'", '+str(page)+')'
    if(page > 0):
        addDir('[COLOR blue]<< Первая страница[/COLOR]', '', "search_page", 0, searchValue)
        addDir('[COLOR green]<< Предылущая страница[/COLOR]', '', "search_page", page-1, searchValue)

    genreHtml =  request(siteUrl+'/?search='+urllib.quote_plus(searchValue)+'&page='+str(page), {})

    movies = parseMovies(genreHtml)
    if(len(movies) > 0):
        for url, title in movies:
            addDirLink(title, url, "movie_info")
    else:
        Alert('Фильмы? Нет, не видели!', 'Фильмы по Вашем запросу хорошо спрятались.')
        sys.exit()

    maxPage = getMaxPage(genreHtml)
    if(maxPage > page):
        addDir('[COLOR green]Следущая страница >[/COLOR]', '', "search_page", page+1, searchValue)
        addDir('[COLOR blue]Последняя страница >>[/COLOR]', '', "search_page", maxPage, searchValue)

def showYearsList():
    now_time = datetime.datetime.now()
    for x in reversed(range(1900, int(now_time.year)+1)):
        addDir(str(x), '/?genre=0&year='+str(x)+'&sorting=&order=&kinopoisk', "view_year")


def add_bookmark(id):
    result = request(siteUrl+'/jquery', {'action' : 'bookmark_add', 'video_id' : id})
    Notificator('Добавление закладки', result.strip(' \t\n\r'), 3000)

def remove_bookmark(id):
    request(siteUrl+'/bookmark', {'bookmark_delete' : 'Удалить отмеченные', 'bids[]' : id})
    Notificator('Удаление закладки', 'Закладка удалена', 3000)
    xbmc.executebuiltin('Container.Refresh()')

try:
    progress = xbmcgui.DialogProgress()

    params = get_params()
    url    = None
    title  = None
    mode   = None
    page   = 0
    searchValue = ''
    movieInfo = {}
    isBusy = False

    try:    title = urllib.unquote_plus(params['title'])
    except: pass
    try:    url = urllib.unquote_plus(params['url'])
    except: pass
    try:    mode = urllib.unquote_plus(params['mode'])
    except: pass
    try:    page = int(params['page'])
    except: pass
    try:    searchValue = params['search']
    except: pass

    if mode == "movie_info":
        progress.create('Загрузка информации о фильме...')
        progress.update(0)

    # авторизация на watch.is
    if(mode != "years"):
        basicHtml = request(siteUrl+'/login', authInfo)

    if mode == "movie_info":
        progress.update(25)

    if mode == None:
        homePage()
    elif mode == "genres":
        viewGenres()
    elif mode == "view_genre":
        viewSelectedGenre(url, page)
    elif mode == "view_year":
        viewSelectedYear(url, page)
    elif mode == "view_rating":
        viewOrderByRating(page)
    elif mode == "movie_info":
        showMovieInfo(url)
    elif mode == "search":
        openSearchDialog(page)
    elif mode == "search_page":
        viewSearchResult(searchValue, page)
    elif mode == "topmovie":
        viewTopMovie()
    elif mode == "allmovie":
        viewAllMovies(page)
    elif mode == "bookmarks":
        viewBookmarks()
    elif mode == "newmovie":
        viewNewMovies(url)
    elif mode == "years":
        showYearsList()
    elif mode == 'add_bookmark':
        add_bookmark(url)
    elif mode == 'remove_bookmark':
        remove_bookmark(url)
    del progress

except SystemExit:
    pass
except:
    print traceback.format_exc()
    Notificator('Шеф, все пропало...', 'Произошла критическая ошибка', 3000)
    sys.exit(1)

if mode == None or mode == "bookmarks":
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
else:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))