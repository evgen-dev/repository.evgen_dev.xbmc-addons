# -*- coding: utf-8 -*-

import xbmcup.app
from core.index import Index
from core.list import MovieList
from core.list import QualityList
from core.list import SearchList


plugin = xbmcup.app.Plugin()

plugin.route(None, Index)
plugin.route('list', MovieList)
plugin.route('quality-list', QualityList)
plugin.route('search', SearchList)

plugin.run()