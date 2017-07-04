# -*- coding: utf-8 -*-

import xbmcup.app, xbmc, xbmcplugin

class Render:
    def render_items(self, type='movies'):
        self.render(content=type)
        skin = xbmc.getSkinDir()
        if(skin == 'skin.confluence' or skin == 'skin.confluence-ploop'):
            xbmc.executebuiltin("Container.SetViewMode(503)")
            #print skin