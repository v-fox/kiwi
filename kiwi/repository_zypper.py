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
import os
from ConfigParser import ConfigParser

# project
from command import Command
from repository import Repository


class RepositoryZypper(Repository):
    """
        Implements repo handling for zypper package manager
    """
    def post_init(self, custom_args):
        self.args = custom_args
        # config file parameters for zypper tool
        self.runtime_zypper_config = ConfigParser()
        # config file parameters for libzypp library
        self.runtime_zypp_config = ConfigParser()

        self.runtime_zypper_config.add_section('main')
        self.runtime_zypp_config.add_section('main')

        self._write_runtime_config()

    def add_bootstrap_repo(self, name, uri, repo_type, prio):
        print "OK"

    def delete_bootstrap_repo(self, name):
        print "OK"

    def add_repo(self, name, uri, repo_type, prio):
        print "OK"

    def delete_repo(self, name):
        print "OK"

    def _write_runtime_config(self):
        runtime_zypper_config_file = self.root_dir + self.shared_location \
            + '/zypper/zypper.conf.' + format(os.getpid())
        runtime_zypp_config_file = self.root_dir + self.shared_location \
            + '/zypper/zypp.conf.' + format(os.getpid())
        Command.run(['mkdir', '-p', os.path.dirname(runtime_zypp_config_file)])
        with open(runtime_zypper_config_file, 'w') as config:
            self.runtime_zypper_config.write(config)
        with open(runtime_zypp_config_file, 'w') as config:
            self.runtime_zypp_config.write(config)

        print runtime_zypper_config_file
