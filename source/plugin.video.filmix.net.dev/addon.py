# -*- coding: utf-8 -*-

import urlparse, urllib,sys, xbmc,traceback

# process United Search request
try:
    search_vars = sys.argv[2].split('?')
    search_vars = search_vars[-1].split('&')
    if search_vars[0] == 'usearch=True':
        params = urlparse.parse_qs(sys.argv[2].replace('?', ''))
        united_search = '{"url": ["link", "search", [{"vsearch": "'+(params['keyword'][0])+'", "usersearch": "'+(params['keyword'][0])+'", "page": 0, "is_united" : "1"}]], "source": "item", "folder": true, "parent" : {}}'
        sys.argv[2] = '?json'+urllib.quote_plus(united_search)
except:
    xbmc.log(traceback.format_exc())


import xbmcup.app, sys
from core.index import Index
from core.list import MovieList, BookmarkList, QualityList, SearchList
from core.filter import Filter
from core.context import ContextMenu
from core.donate import Donate

#log = open(xbmcup.system.fs('sandbox://myprog.log'), "a")
#sys.stdout = log



plugin = xbmcup.app.Plugin()

plugin.route(None, Index)
plugin.route('list', MovieList)
plugin.route('quality-list', QualityList)
plugin.route('search', SearchList)
plugin.route('filter', Filter)
plugin.route('bookmarks', BookmarkList)
plugin.route('context', ContextMenu)
plugin.route('donate', Donate)

plugin.run()