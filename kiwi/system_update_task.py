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
usage: kiwi system update -h | --help
       kiwi system update --root=<directory>
           [--add-package=<name>]
           [--delete-package=<name>]
       kiwi system update help

commands:
    update
        update root system with latest repository updates
        and optionally allow to add or delete packages
    update help
        show manual page for update command

options:
    --root=<directory>
        the path to the new root directory of the system
    --add-package=<name>
        install the given package name after upgrading
    --delete-package=<name>
        delete the given package name after upgrading
"""
# project
import xml_parse

from cli_task import CliTask
from help import Help
from xml_description import XMLDescription
from system import System
from xml_state import XMLState

from logger import log


class SystemUpdateTask(CliTask):
    """
        Implements update and maintenance of root systems
    """
    def process(self):
        self.manual = Help()
        if self.__help():
            return

        self.xml = self.__load_xml()
        self.used_profiles = XMLState.used_profiles(
            self.xml, self.profile_list()
        )
        if self.used_profiles:
            log.info('--> Using profiles: %s', ','.join(self.used_profiles))

        if self.command_args['update']:
            log.info('Updating system')
            self.system = System(
                self.xml, self.used_profiles, allow_existing=True
            )
            self.system.setup_root(
                self.command_args['--root']
            )
            self.system.setup_repositories()
            self.system.update()

    def __help(self):
        if self.command_args['help']:
            self.manual.show('kiwi::system::update')
        else:
            return False
        return self.manual

    def __load_xml(self):
        config_file = self.command_args['--root'] + '/image/config.xml'
        log.info('Loading XML description %s', config_file)
        description = XMLDescription(
            config_file
        )
        return description.load()
