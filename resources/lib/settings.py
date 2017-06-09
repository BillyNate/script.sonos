# -*- coding: utf-8 -*-
import os
import xbmc
import xbmcaddon
import logging

ADDON = xbmcaddon.Addon(id='service.sonos')
ADDON_ID = ADDON.getAddonInfo('id')


# Common logging module
def log(txt, loglevel=xbmc.LOGDEBUG):
    if (ADDON.getSetting("logEnabled") == "true") or (loglevel != xbmc.LOGDEBUG):
        if isinstance(txt, str):
            txt = txt.decode("utf-8")
        message = u'%s: %s' % (ADDON_ID, txt)
        xbmc.log(msg=message.encode("utf-8"), level=loglevel)


# There has been problems with calling join with non ascii characters,
# so we have this method to try and do the conversion for us
def os_path_join(dir, file):
    # Convert each argument - if an error, then it will use the default value
    # that was passed in
    try:
        dir = dir.decode("utf-8")
    except:
        pass
    try:
        file = file.decode("utf-8")
    except:
        pass
    return os.path.join(dir, file)


##############################
# Stores Addon Settings
##############################
class Settings():

    @staticmethod
    def redirectVolumeControls():
        return ADDON.getSetting("redirectVolumeControls") == 'true'

    @staticmethod
    def getChecksPerSecond():
        return int(float(ADDON.getSetting("checksPerSecond")))
