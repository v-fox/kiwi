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
           [--add-package=<name>...]
           [--delete-package=<name>...]
       kiwi system update help

commands:
    update
        update root system with latest repository updates
        and optionally allow to add or delete packages. the options
        to add or delete packages can be used multiple times
    update help
        show manual page for update command

options:
    --root=<directory>
        the path to the new root directory of the system
    --add-package=<name>
        install the given package name
    --delete-package=<name>
        delete the given package name
"""
# project
import xml_parse

from cli_task import CliTask
from help import Help
from xml_description import XMLDescription
from system import System

from logger import log


class SystemUpdateTask(CliTask):
    """
        Implements update and maintenance of root systems
    """
    def process(self):
        self.manual = Help()
        if self.__help():
            return

        self.load_xml_description(
            self.command_args['--root']
        )

        package_requests = False
        if self.command_args['--add-package']:
            package_requests = True
        if self.command_args['--delete-package']:
            package_requests = True

        if self.command_args['update']:
            log.info('Updating system')
            self.system = System(
                self.xml, self.used_profiles, allow_existing=True
            )
            self.system.setup_root(
                self.command_args['--root']
            )
            self.system.setup_repositories()
            if not package_requests:
                self.system.update_system()
            else:
                if self.command_args['--add-package']:
                    self.system.install_packages(
                        self.command_args['--add-package']
                    )
                if self.command_args['--delete-package']:
                    self.system.delete_packages(
                        self.command_args['--delete-package']
                    )

    def __help(self):
        if self.command_args['help']:
            self.manual.show('kiwi::system::update')
        else:
            return False
        return self.manual
