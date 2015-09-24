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
usage: kiwi system prepare -h | --help
       kiwi system prepare --description=<directory> --root=<directory>
           [--type=<buildtype>]
           [--allow-existing-root]
           [--set-repo=<source,type,alias>]
           [--add-repo=<source,type,alias>...]
       kiwi system prepare help

commands:
    prepare
        prepare and install a new system for chroot access
    prepare help
        show manual page for prepare command

options:
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
    --set-repo=<source,type,alias>
        overwrite the repo source, type and alias for the first
        repository in the XML description
    --add-repo=<source,type,alias>
        add repository with given source, type and alias.
        this option can be specified multiple times
"""
# project
import xml_parse

from cli_task import CliTask
from help import Help
from xml_description import XMLDescription
from system import System
from xml_state import XMLState

from logger import log


class SystemPrepareTask(CliTask):
    """
        Implements preparation and installation of a new root system
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

        if self.command_args['--set-repo']:
            (repo_source, repo_type, repo_alias) = self.triple_token(
                self.command_args['--set-repo']
            )
            XMLState.set_repository(
                self.xml,
                repo_source, repo_type, repo_alias,
                self.used_profiles
            )

        if self.command_args['--add-repo']:
            for add_repo in self.command_args['--add-repo']:
                (repo_source, repo_type, repo_alias) = self.triple_token(
                    add_repo
                )
                XMLState.add_repository(
                    self.xml, repo_source, repo_type, repo_alias
                )

        if self.command_args['prepare']:
            log.info('Preparing system')
            self.system = System(
                self.xml, self.used_profiles,
                self.command_args['--allow-existing-root']
            )
            self.system.setup_root(
                self.command_args['--root']
            )
            self.system.setup_repositories()
            self.system.install_bootstrap()
            self.system.install_system(
                self.command_args['--type']
            )
            self.system.store_description()

    def __help(self):
        if self.command_args['help']:
            self.manual.show('kiwi::system::prepare')
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
