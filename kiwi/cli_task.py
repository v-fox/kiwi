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
import sys
import logging

# project
from cli import Cli
from help import Help
from xml_state import XMLState


class CliTask(object):
    """
        Base class for all task classes, loads the task and provides
        the interface to the command options and the XML description
    """
    def __init__(self):
        from logger import log

        self.cli = Cli()

        # show main help man page if requested
        if self.cli.show_help():
            manual = Help()
            manual.show('kiwi')
            sys.exit(0)

        # load/import task module
        self.task = self.cli.load_command()

        # get command specific args
        self.command_args = self.cli.get_command_args()

        # get global args
        self.global_args = self.cli.get_global_args()

        # set log level
        if self.global_args['--debug']:
            log.setLevel(logging.DEBUG)

    def load_xml_description(self, description_directory):
        from logger import log

        log.info('Loading XML description')
        (self.xml, self.config_file) = XMLState.load_xml(
            description_directory
        )
        log.info('--> loaded %s', self.config_file)
        self.used_profiles = XMLState.used_profiles(
            self.xml, self.profile_list()
        )
        if self.used_profiles:
            log.info('--> Using profiles: %s', ','.join(self.used_profiles))

    def profile_list(self):
        profiles = []
        if self.global_args['--profile']:
            profiles = self.global_args['--profile'].split(',')
        return profiles

    def quadruple_token(self, option):
        tokens = option.split(',', 3)
        return [tokens.pop(0) if len(tokens) else None for _ in range(0, 4)]
