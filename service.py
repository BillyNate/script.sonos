# -*- coding: utf-8 -*-
import os
import re
import select
import subprocess
import traceback
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

# Import the common settings
from resources.lib.settings import Settings
from resources.lib.settings import log


ADDON = xbmcaddon.Addon(id='service.cec')
CWD = ADDON.getAddonInfo('path').decode('utf-8')
RES_DIR = xbmc.translatePath(os.path.join(CWD, 'resources').encode('utf-8')).decode('utf-8')


#########################################
# Redirects the volume controls
#########################################
class CEC():

    def __init__(self):
        (self.readPipe, self.writePipe) = os.pipe()
        self.readPipeAsFile = os.fdopen(self.readPipe)
        self.reset()

    def reset(self):
        self.process = subprocess.Popen(['/usr/osmc/bin/cec-client'], stdin=subprocess.PIPE, stdout=self.writePipe)
        self.process.stdin.write('pow 5') # Fix for non-responsiveness to volume changes

    def action(self, action):
        self.process.stdin.write(action)

    def read(self):
        if len(select.select([self.readPipe], [], [], 0)[0]) == 1:
            return self.readPipeAsFile.readline()
        return None

    def cleanup(self):
        self.process.kill()

#########################################
# Redirects the volume controls
#########################################
class VolumeRedirect():
    def __init__(self):
        self.KEYMAP_PATH = xbmc.translatePath(os.path.join(RES_DIR, 'keymaps'))
        self.KEYMAPSOURCEFILE = os.path.join(self.KEYMAP_PATH, 'keymap.xml')
        self.KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'cec_keymap.xml')

        if Settings.redirectVolumeControls():
            self._enableKeymap()
        else:
            self._cleanupKeymap()

    def checkVolumeChange(self):
        # Check to see if the Volume Redirect is Enabled
        if not Settings.redirectVolumeControls():
            return

        redirect = xbmcgui.Window(10000).getProperty('cec_redirect')

        if redirect in [None, '']:
            return

        commands = []
        while redirect not in [None, '']:
            xbmcgui.Window(10000).clearProperty('cec_redirect')
            commands.append(redirect.lower())
            redirect = xbmcgui.Window(10000).getProperty('cec_redirect')
        return commands

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

        # Class to deal with CEC support
        cec = CEC()
        reDeviceNumber = re.compile('\((\d+)\)')
        reNewStatus = re.compile('\'([a-zA-Z0-9_ ]+)\'$')
        # Two examples of lines that show a status change in cec-client:
        "TV (0): power status changed from 'unknown' to 'on'"
        "TV (0): power status changed from 'unknown' to 'in transition from standby to on'"

        resetCEC = False

        # Loop until Kodi exits
        while (not xbmc.abortRequested):

            line = cec.read()
            while line is not None:
                if 'power status changed from' in line:
                    device = re.search(reDeviceNumber, line).group(1)
                    status = re.search(reNewStatus, line).group(1)
                    if not 'in transition' in status:
                        xbmcgui.Window(10000).setProperty('cec_status_' + device, status)
                        if device == '0' and status == 'standby':
                            resetCEC = True
                line = cec.read()

            # Check if a volume change has been made
            commands = redirectVolume.checkVolumeChange()
            if commands:
                for command in commands:
                    log('%s: %s %s' % (ADDON.getLocalizedString(32050), ADDON.getLocalizedString(32060), command), xbmc.LOGERROR)
                    cec.action(command)

            # This is a fix for TV's turning on, when only the AVR is requested to turn on, after the TV has already been turned on once:
            if resetCEC:
                cec.cleanup()
                cec.reset()
                resetCEC = False

            # Sleep for a bit to not take to much resources
            xbmc.sleep(1000 / Settings.getChecksPerSecond())

        redirectVolume.cleanup()
        del redirectVolume

        cec.cleanup()
        del cec

    log(ADDON.getLocalizedString(32059))
