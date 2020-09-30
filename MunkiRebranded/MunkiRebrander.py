#!/usr/local/autopkg/python
#
# Copyright 2020 Luca Oonk (Cloudcarrier B.V.)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for MunkiRebrander class"""

import fileinput
import subprocess
import re
from os import listdir, stat, chmod
from os.path import isfile, join
from shutil import copyfile
from autopkglib import BUNDLE_ID, Processor, ProcessorError, is_mac

__all__ = ["MunkiRebrander"]


class MunkiRebrander():

    def main(self):

        # Desired new app name
        appNameWanted = 'Orchard Software Centre'

        # Optional icon file to replace the MSC icon
        srcIcon = 'AppIcon.icns'

        # Git release tag (leave empty for latest build)
        tag = 'v2.2.4'

        ### Probably don't need to edit below this line

        # App name requiring replacement
        appNameOriginal = 'Managed Software Center'

        # Localized forms of app name
        appNameLocalized = {    'da'       : 'Managed Software Center',
                                        'de'       : 'Geführte Softwareaktualisierung',
                                        'en'       : 'Managed Software Center',
                                        'en_AU'  : 'Managed Software Centre',
                                        'en_GB'  : 'Managed Software Centre',
                                        'en_CA'  : 'Managed Software Centre',
                                        'es'       : 'Centro de aplicaciones',
                                        'fi'       : 'Managed Software Center',
                                        'fr'       : 'Centre de gestion des logiciels',
                                        'it'       : 'Centro Gestione Applicazioni',
                                        'nb'       : 'Managed Software Center',
                                        'nl'       : 'Managed Software Center',
                                        'ru'       : 'Центр Управления ПО',
                                        'sv'       : 'Managed Software Center'
                                    }

        # Git repo
        git_repo = "https://github.com/munki/munki"

        # Make Munki pkg script
        make_munki = 'munki/code/tools/make_munki_mpkg.sh'

        # First cleanup previous runs
        print('Cleaning up previous runs')
        proc = subprocess.Popen(['sudo','/bin/rm','-rf', 'munki'])
        proc.communicate()

        # Checkout git repo
        print('Cloning git repo')
        proc = subprocess.Popen(['git','clone', git_repo])
        proc.communicate()

        if tag:
            print('Checkout tag %s' % tag)
            proc = subprocess.Popen(['git','-C', 'munki', 'checkout', 'tags/%s' % tag])
            proc.communicate()

        # Replace in required files

        print('Replacing %s with %s' % (appNameOriginal, appNameWanted))

        replaceList = ['InfoPlist.strings', 'Localizable.strings', 'MainMenu.strings']

        appDirs = ['munki/code/apps/Managed Software Center/Managed Software Center','munki/code/apps/MunkiStatus/MunkiStatus']

        def searchReplace(search, replace, fileToSearch):
            if isfile(fileToSearch):
                    try:
                        for line in fileinput.input(fileToSearch, inplace=True):
                            print(re.sub(search, replace, line)),
                    except Exception:
                        print("Error replacing in %s" % fileToSearch)

        for appDir in appDirs:
            
            if isfile(join(appDir, 'en.lproj/MainMenu.xib')):
                    searchReplace(appNameOriginal, appNameWanted, join(appDir, 'en.lproj/MainMenu.xib'))
            if isfile(join(appDir, 'MSCMainWindowController.py')):
                    searchReplace(appNameOriginal, appNameWanted, join(appDir, 'MSCMainWindowController.py'))
            
            for f in listdir(appDir):
                    for countryCode, localizedName in appNameLocalized.iteritems():
                        if f.endswith('%s.lproj' % countryCode):
                            for i in replaceList:
                                    fileToSearch = join(appDir, f, i)
                                    if isfile(fileToSearch):
                                        # Replaces all instances of original app name
                                        searchReplace(appNameOriginal, appNameWanted, fileToSearch)
                                        # Matches based on localized app name
                                        searchReplace(localizedName, appNameWanted, fileToSearch)

        # Copy icons
        if isfile(srcIcon):
            print("Replace icons with %s" % srcIcon)
            destIcon = "munki/code/apps/Managed Software Center/Managed Software Center/Managed Software Center.icns"
            copyfile(srcIcon, destIcon)
            destIcon = "munki/code/apps/MunkiStatus/MunkiStatus/MunkiStatus.icns"
            copyfile(srcIcon, destIcon)



        print("Building Munki")
        proc = subprocess.Popen(['./munki/code/tools/make_munki_mpkg.sh','-r','munki'])
        proc.communicate()
 

if __name__ == "__main__":
    PROCESSOR = MunkiRebrander()
    PROCESSOR.execute_shell()
