# -*- coding: utf-8 -*-
#очистка кеша

import os, xbmcup.system
from core.defines import *

cache_file = xbmcup.system.fs('sandbox://'+CACHE_DATABASE).replace('clear_cache.py', '')
if xbmcup.system.FS().exists(cache_file):
    os.remove(cache_file)