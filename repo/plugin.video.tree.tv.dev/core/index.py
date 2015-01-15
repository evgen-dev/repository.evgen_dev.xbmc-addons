# -*- coding: utf-8 -*-

import xbmcup.app, cover

class Index(xbmcup.app.Handler):
    def handle(self):
        self.item(u'Поиск',         self.link('search'),                        folder=True, cover=cover.search)
        self.item(u'Фильмы',        self.link('list', {'dir' : 'films'}),       folder=True, cover=cover.treetv)
        self.item(u'Сериалы',       self.link('list', {'dir' : 'serials'}),     folder=True, cover=cover.treetv)
        self.item(u'Мультфильмы',   self.link('list', {'dir' : 'multfilms'}),   folder=True, cover=cover.treetv)
        self.item(u'ТВ-передачи',   self.link('list', {'dir' : 'onlinetv'}),    folder=True, cover=cover.treetv)
        self.item(u'Аниме',         self.link('list', {'dir' : 'anime'}),       folder=True, cover=cover.treetv)
