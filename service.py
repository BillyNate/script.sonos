# -*- coding: utf-8 -*-
import os
import traceback
import uuid
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

# Import the common settings
from resources.lib.settings import Settings
from resources.lib.settings import log

ADDON = xbmcaddon.Addon(id='service.sonos')
CWD = ADDON.getAddonInfo('path').decode('utf-8')
RES_DIR = xbmc.translatePath(os.path.join(CWD, 'resources').encode('utf-8')).decode('utf-8')


#########################################
# Redirects the volume controls
#########################################
class VolumeRedirect():
    def __init__(self):
        # TODO: Optionally init any service/connection/whatever here
        self.KEYMAP_PATH = xbmc.translatePath(os.path.join(RES_DIR, 'keymaps'))
        self.KEYMAPSOURCEFILE = os.path.join(self.KEYMAP_PATH, 'volume_keymap.xml')
        self.KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'volume_keymap.xml')

        if Settings.redirectVolumeControls():
            self._enableKeymap()
        else:
            self._cleanupKeymap()

    def checkVolumeChange(self):
        # Check to see if the Volume Redirect is Enabled
        if not Settings.redirectVolumeControls():
            return

        redirect = xbmcgui.Window(10000).getProperty('volume_redirect')
            xbmcgui.Window(10000).clearProperty('volume_redirect_%s' % (RANDOM_STR,))

        while redirect not in [None, '']:
            xbmcgui.Window(10000).clearProperty('volume_redirect')

            log('%s: %s %s' % (ADDON.getLocalizedString(32050), ADDON.getLocalizedString(32060), redirect))
            redirect = xbmcgui.Window(10000).getProperty('volume_redirect')
            if redirect.lower() == 'up':
                None
                # TODO: Apply real volume change here!
            elif redirect.lower() == 'down':
                None
                # TODO: Apply real volume change here!
            elif redirect.lower() == 'mute':
                None
                # Check the current muted state?
                # TODO: Toggle mute!


    def cleanup(self):
        if Settings.redirectVolumeControls():
            self._cleanupKeymap()

    # Copies the keymap to the correct location and loads it
    def _enableKeymap(self):
        try:
            xbmcvfs.copy(self.KEYMAPSOURCEFILE, self.KEYMAPDESTFILE)
            xbmc.executebuiltin('Action(reloadkeymaps)')
            log('%s: %s' % (ADDON.getLocalizedString(32050), ADDON.getLocalizedString(32052)))
        except:
            log('%s: %s: %s' % (ADDON.getLocalizedString(32050), ADDON.getLocalizedString(32053), traceback.format_exc()), xbmc.LOGERROR)

    # Removes the keymap
    def _cleanupKeymap(self):
        if xbmcvfs.exists(self.KEYMAPDESTFILE):
            try:
                xbmcvfs.delete(self.KEYMAPDESTFILE)
                log('%s: %s' % (ADDON.getLocalizedString(32050), ADDON.getLocalizedString(32054)))
            except:
                log('%s: %s: %s' % (ADDON.getLocalizedString(32050), ADDON.getLocalizedString(32055), traceback.format_exc()), xbmc.LOGERROR)

            # Force a re-load
            xbmc.executebuiltin('Action(reloadkeymaps)')


################################
# Main of the Service           
################################
if __name__ == '__main__':
    
    log('%s: %s (%s %s)' % (ADDON.getLocalizedString(32051), ADDON.getLocalizedString(32056), ADDON.getLocalizedString(32057), str(ADDON.getAddonInfo('version'))))

    if not Settings.redirectVolumeControls():
        log('%s: %s' % (ADDON.getLocalizedString(32051), ADDON.getLocalizedString(32058)))
    else:
        # Class to deal with redirecting the volume
        redirectVolume = VolumeRedirect()

        # Loop until Kodi exits
        while (not xbmc.abortRequested):

            # Check if a volume change has been made
            redirectVolume.checkVolumeChange()

            # Increment the timer and sleep for a second before the next check
            xbmc.sleep(1000 / Settings.getChecksPerSecond())

        redirectVolume.cleanup()
        del redirectVolume

    log(ADDON.getLocalizedString(32059))
