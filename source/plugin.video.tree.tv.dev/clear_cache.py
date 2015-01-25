# -*- coding: utf-8 -*-
#очистка кеша

import sys
sys.argv[0] = sys.argv[0].replace('/clear_cache.py', '')
import os, xbmcup.system, xbmcup.db
from core.defines import *

CACHE = xbmcup.db.Cache(xbmcup.system.fs('sandbox://'+CACHE_DATABASE))
CACHE.flush();
