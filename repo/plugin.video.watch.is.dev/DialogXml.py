# -*- coding: utf-8 -*-

import sys, urllib, urllib2, re, os, cookielib, traceback, datetime
import xbmc, xbmcgui, xbmcaddon
from DialogReviews import *

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
class DialogXml(xbmcgui.WindowXMLDialog):
    def onInit(self):
        print "onInit(): Window Initialized"
        self.movie_label = self.getControl(32)
        self.movie_label.setText(self.movieInfo['desc'])

        self.view_label = self.getControl(34)
        self.view_label.setLabel('[COLOR blue]Просм.:[/COLOR] '+self.movieInfo['views'])

        self.view_label = self.getControl(35)
        self.ratingcolor = 'green'
        self.ratingint = int(self.movieInfo['rating'])
        if(self.ratingint < 0):
            self.ratingcolor = 'red'
        self.view_label.setLabel('[COLOR blue]Рейтинг:[/COLOR] [COLOR '+self.ratingcolor+']'+self.movieInfo['rating']+'[/COLOR]')

        self.movie_label = self.getControl(1)
        self.movie_label.setLabel(self.movieInfo['title'])

        self.movie_label = self.getControl(32)
        self.movie_label.setText(self.movieInfo['desc'])

        self.poster = self.getControl(31)
        self.poster.setImage(self.movieInfo['poster'])

        self.poster = self.getControl(36)
        self.poster.setImage(self.movieInfo['kinopoisk'])
        self.quilitybutton = self.getControl(131)

        __settings__ = xbmcaddon.Addon(id='plugin.video.watch.is.dev')
        hq_enabled = __settings__.getSetting('default_play_hd')

        if(hq_enabled != 'false'):
            self.quilitybutton.setSelected(True)
        else:
            self.quilitybutton.setSelected(False)

        print hq_enabled

        if(self.movieInfo['direct_url_hq']):
            self.quilitybutton.setEnabled(True)
        else:
            self.quilitybutton.setEnabled(False)
            self.quilitybutton.setSelected(False)

        self.setFocus(self.getControl(30))

    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        if (action == ACTION_NAV_BACK or action == ACTION_PREVIOUS_MENU):
            self.close()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            self.close()

    def onClick(self, controlID):
        if (controlID == 2 or controlID == 22):
            self.close()
        if (controlID == 30):
            self.close()
            self.listitem = xbmcgui.ListItem(self.movieInfo['title'])
            if(self.quilitybutton.isSelected()):
                xbmc.Player().play(self.movieInfo['direct_url_hq'], self.listitem)
            else:
                xbmc.Player().play(self.movieInfo['direct_url'], self.listitem)

        if(controlID == 33):
            __settings__ = xbmcaddon.Addon(id='plugin.video.watch.is.dev')
            path = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path').replace(';', ''), ''))
            w = DialogReviews("reviews.xml", path, "Default")
            w.doModal(self.movieInfo['movieHtml'])
            del w

    def onFocus(self, controlID):
        #print "onFocus(): control %i" % controlID
        pass


    def doModal(self, movieInfo):
        self.movieInfo = movieInfo
        xbmcgui.WindowXMLDialog.doModal(self)