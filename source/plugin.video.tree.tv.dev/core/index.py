# -*- coding: utf-8 -*-

import xbmcup.app, cover, xbmc, xbmcaddon
from auth import Auth
from core.defines import *

class Index(xbmcup.app.Handler):
    def handle(self):
        if(xbmcup.app.setting['is_activated'] == 'false'):
            self.item(xbmcup.app.lang[37009], self.link('null'), folder=False, cover=cover.search)
            self.item(xbmcup.app.lang[37010], self.link('list', {'dir' : 'films'}), folder=True, cover=cover.search)
            # openAddonSettings2(PLUGIN_ID, 0, 3)
            return

        Auth().autorize()
        self.item(xbmcup.app.lang[30112], self.link('search'),                        folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30120], self.link('filter', {'window' : ''}),       folder=True, cover=cover.treetv)
        self.item(xbmcup.app.lang[30146], self.link('bookmarks',  {'url' : ''}),       folder=True, cover=cover.treetv)
        self.item(xbmcup.app.lang[30119], self.link('collection', {'url' : ''}),      folder=True, cover=cover.treetv)

        self.item(xbmcup.app.lang[30160], self.link('null', {}),       folder=True, cover=cover.treetv)

        self.item(' - '+xbmcup.app.lang[30114], self.link('list', {'dir' : 'films'}),       folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30115], self.link('list', {'dir' : 'serials'}),     folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30116], self.link('list', {'dir' : 'multfilms'}),   folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30117], self.link('list', {'dir' : 'onlinetv'}),    folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30118], self.link('list', {'dir' : 'anime'}),       folder=True, cover=cover.treetv)

        if(xbmcup.app.setting['hide_donate'] == 'false'):
            self.item(xbmcup.app.lang[37000], self.link('donate', {'hide' : '1'}), folder=True, cover=cover.treetv)


