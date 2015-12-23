# -*- coding: utf-8 -*-

import xbmcup.app
from core.index import Index
from core.list import MovieList, BookmarkList, QualityList, SearchList
from core.filter import Filter
from core.context import ContextMenu

plugin = xbmcup.app.Plugin()

plugin.route(None, Index)
plugin.route('list', MovieList)
plugin.route('quality-list', QualityList)
plugin.route('search', SearchList)
plugin.route('filter', Filter)
plugin.route('bookmarks', BookmarkList)
plugin.route('context', ContextMenu)

plugin.run()