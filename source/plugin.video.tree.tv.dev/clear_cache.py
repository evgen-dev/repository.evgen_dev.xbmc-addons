# -*- coding: utf-8 -*-
#очистка кеша

import os, xbmcup.system
from core.defines import *

cache_fake = xbmcup.system.fs('sandbox://'+CACHE_DATABASE)
cache_file = cache_fake.replace('clear_cache.py', '')
if xbmcup.system.FS().exists(cache_file):
    os.remove(cache_file.replace('clear_cache.py', ''))
os.rmdir(cache_fake.replace(CACHE_DATABASE, ''))