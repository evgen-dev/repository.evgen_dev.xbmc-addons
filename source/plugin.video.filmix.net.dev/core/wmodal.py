# -*- coding: utf-8 -*-

import sys, urllib, urllib2, re, os, cookielib, traceback, datetime
import xbmc, xbmcgui, xbmcaddon, xbmcup
from http import HttpData

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

class MovieInfo(xbmcgui.WindowXMLDialog, HttpData):
    def formatRating(self, rating):
        ratingcolor = 'green'
        rating = int(rating)
        if(rating < 0):
             ratingcolor = 'red'
        return '[COLOR blue]Рейтинг:[/COLOR] [COLOR '+ratingcolor+']'+str(rating)+'[/COLOR]'

    def onInit(self):
        print "onInit(): Window Initialized"
        self.getControl(1).setLabel(self.movieInfo['title'])
        self.getControl(32).setText(self.movieInfo['desc'])
        self.getControl(31).setImage(self.movieInfo['poster'])

        self.trailer = self.getControl(33)
        if(self.movieInfo['trailer'] != False):
            self.trailer.setEnabled(True)
        else:
            self.trailer.setEnabled(False)

        self.setFocus(self.getControl(22))


    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        if (action == ACTION_NAV_BACK or action == ACTION_PREVIOUS_MENU):
            self.close()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            self.close()

    def onClick(self, controlID):
        if (controlID == 2 or controlID == 22):
            self.close()

        if(controlID == 33):
            self.close()
            self.listitem = xbmcgui.ListItem(xbmcup.app.lang[34028]+' '+self.movieInfo['title'], iconImage=self.movieInfo['poster'], thumbnailImage=self.movieInfo['poster'])
            link = self.get_trailer(self.movieInfo['trailer'])
            if(link != False):
                xbmc.Player().play(link, self.listitem)
            else:
                xbmcup.gui.message(xbmcup.app.lang[34032].encode('utf8'))

    def onFocus(self, controlID):
        print "onFocus(): control %i" % controlID
        pass


    def doModal(self, movieInfo):
        self.movieInfo = movieInfo
        xbmcgui.WindowXMLDialog.doModal(self)