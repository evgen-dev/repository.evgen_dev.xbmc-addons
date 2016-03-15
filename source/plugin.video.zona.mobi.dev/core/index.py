# -*- coding: utf-8 -*-

import xbmcup.app, cover

class Index(xbmcup.app.Handler):
    def handle(self):
        self.item(xbmcup.app.lang[30112], self.link('search'),                        folder=True, cover=cover.search)
        self.item(xbmcup.app.lang[30120], self.link('filter', {'window' : ''}),       folder=True, cover=cover.treetv)

        self.item(xbmcup.app.lang[35004], self.link('null', {}),       folder=True, cover=cover.treetv)

        self.item(xbmcup.app.lang[30119], self.link('list',  {'dir' : '', 'sub_dir' : 'js-popularMovies'}),       folder=True, cover=cover.treetv)
        self.item(xbmcup.app.lang[35001], self.link('list',  {'dir' : '', 'sub_dir' : 'js-popularSerials'}),       folder=True, cover=cover.treetv)
        self.item(xbmcup.app.lang[35002], self.link('list',  {'dir' : '', 'sub_dir' : 'js-lastMovies'}),       folder=True, cover=cover.treetv)
        self.item(xbmcup.app.lang[35003], self.link('list',  {'dir' : '', 'sub_dir' : 'js-lastSerials'}),       folder=True, cover=cover.treetv)

        self.item(xbmcup.app.lang[30160], self.link('null', {}),       folder=True, cover=cover.treetv)

        self.item(' - '+xbmcup.app.lang[30114], self.link('list', {'dir' : 'movies'}),       folder=True, cover=cover.treetv)
        self.item(' - '+xbmcup.app.lang[30115], self.link('list', {'dir' : 'tvseries'}),     folder=True, cover=cover.treetv)