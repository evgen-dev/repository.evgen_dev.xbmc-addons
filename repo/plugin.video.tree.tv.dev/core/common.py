# -*- coding: utf-8 -*-

import xbmcup.app, xbmc

class Render:
    def render_items(self, type='movies'):
        self.render(content=type)
        xbmc.executebuiltin("Container.SetViewMode(503)")