# -*- coding: utf-8 -*-
#очистка кеша

import os, xbmcup.system

cache_file = xbmcup.system.fs('sandbox://treetv.cache.db').replace('clear_cache.py', '')
if xbmcup.system.FS().exists(cache_file):
    os.remove(cache_file)