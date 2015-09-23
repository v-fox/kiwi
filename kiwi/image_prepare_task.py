# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
"""
usage: kiwi image prepare -h | --help
       kiwi image prepare --description=<directory> --root=<directory>
           [--type=<buildtype>]
           [--allow-existing-root]
       kiwi image prepare help

commands:
    prepare
        prepare and install a new system for chroot access
    --description=<directory>
        the description must be a directory containing a kiwi XML
        description and optional metadata files
    --root=<directory>
        the path to the new root directory of the system
    --allow-existing-root
        allow to use an existing root directory. Use with caution
        this could cause an inconsistent root tree if the existing
        contents does not fit to the additional installation
    --type=<buildtype>
        set the build type. If not set the default XML specified
        build type will be used
    help
        show manual page for prepare command
"""
# project
import xml_parse

from cli_task import CliTask
from help import Help
from xml_description import XMLDescription
from prepare import Prepare
from xml_state import XMLState

from logger import log


class ImagePrepareTask(CliTask):
    """
        Implements preparation and installation of a new root system
    """
    def process(self):
        self.manual = Help()
        if self.__help():
            return

        if self.command_args['prepare']:
            log.info('Preparing system')
            self.xml = self.__load_xml()
            used_profiles = XMLState.used_profiles(
                self.xml, self.__profiles()
            )
            if used_profiles:
                log.info('--> Using profiles: %s', ','.join(used_profiles))
            self.prepare = Prepare(
                self.xml, used_profiles
            )
            self.prepare.setup_root(
                self.command_args['--root'],
                self.command_args['--allow-existing-root']
            )
            self.prepare.setup_repositories()
            self.prepare.install_bootstrap()
            self.prepare.install_system(
                self.command_args['--type']
            )

    def __help(self):
        if self.command_args['help']:
            self.manual.show('kiwi::image::prepare')
        else:
            return False
        return self.manual

    def __load_xml(self):
        config_file = self.command_args['--description'] + '/config.xml'
        log.info('Loading XML description %s', config_file)
        description = XMLDescription(
            config_file
        )
        return description.load()

    def __profiles(self):
        profiles = []
        if self.global_args['--profile']:
            profiles = self.global_args['--profile'].split(',')
        return profiles
