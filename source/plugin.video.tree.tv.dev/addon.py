# -*- coding: utf-8 -*-

import urlparse, urllib,sys

#process STRM files
split_vars = sys.argv[0].split('/')
if(split_vars[-1] == 'play'):
    split_vars[-1] = ''
    params = urlparse.parse_qs(sys.argv[2].replace('?', ''))
    try:
        test = params['folder']
    except:
        params['folder'] = ['']
    sys.argv[0] = '/'.join(split_vars)
    toplay = '{"url": ["resolve", "resolve", [{"page": "'+params['page'][0]+'", "resolution": "'+params['resolution'][0]+'", "file": "'+params['file'][0]+'", "folder" : "'+params['folder'][0]+'"}]], "source": "item", "folder": false, "parent" : {}}'
    sys.argv[2] = '?json'+urllib.quote_plus(toplay)

# process United Search request
try:
    search_vars = sys.argv[2].split('?')
    search_vars = search_vars[-1].split('&')
    if search_vars[0] == 'usearch=True':
        params = urlparse.parse_qs(sys.argv[2].replace('?', ''))
        united_search = '{"url": ["link", "search", [{"vsearch": "'+params['keyword'][0]+'", "usersearch": "'+params['keyword'][0]+'", "page": 0, "is_united" : "1"}]], "source": "item", "folder": true, "parent" : {}}'
        sys.argv[2] = '?json'+urllib.quote_plus(united_search)
except:
    pass

import xbmcup.app
from core.index import Index
from core.list import MovieList, BookmarkList, QualityList, SearchList, CollectionList
from core.http import ResolveLink
from core.filter import Filter
from core.context import ContextMenu
from core.donate import Donate

plugin = xbmcup.app.Plugin()

plugin.route(None, Index)
plugin.route('list', MovieList)
plugin.route('quality-list', QualityList)
plugin.route('search', SearchList)
plugin.route('collection', CollectionList)
plugin.route('filter', Filter)
plugin.route('bookmarks', BookmarkList)
plugin.route('context', ContextMenu)
plugin.route('resolve', ResolveLink)
plugin.route('donate', Donate)

plugin.run()