# -*- coding: utf-8 -*-

import xbmcup.app, cover
from auth import Auth

class Index(xbmcup.app.Handler):
    def handle(self):
        Auth().autorize()
        self.item(xbmcup.app.lang[30112], self.link('search'),                        folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30120], self.link('filter', {'window' : ''}),       folder=True, cover=cover.treetv)
        self.item(xbmcup.app.lang[30146], self.link('bookmarks',  {'url' : ''}),       folder=True, cover=cover.treetv)

        self.item(xbmcup.app.lang[30160], self.link('null', {}),       folder=True, cover=cover.treetv)

        self.item(' - '+xbmcup.app.lang[30114], self.link('list', {'dir' : 'films'}),       folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30115], self.link('list', {'dir' : 'serialy'}),     folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30116], self.link('list', {'dir' : 'multfilmy'}),   folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30117], self.link('list', {'dir' : 'multserialy'}),   folder=True, cover=cover.treetv)

        if(xbmcup.app.setting['hide_donate'] == 'false'):
            self.item(xbmcup.app.lang[37000], self.link('donate', {'hide' : '1'}), folder=True, cover=cover.treetv)