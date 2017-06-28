# -*- coding: utf-8 -*-

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