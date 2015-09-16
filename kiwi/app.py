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
import logging
import sys

import xml_parse
from xml_description import XMLDescription

from root_init import RootInit
from root_bind import RootBind
from repository_zypper import RepositoryZypper
from command import Command


class App(object):
    """
        Application class to create task instances and process them
    """
    def __init__(self):
        # playground, some testing code
        from logger import log
        log.setLevel(logging.DEBUG)

        # cmd = Command.call(['ls', '-l'])
        # while cmd.process.poll() is None:
        #         line = cmd.output.readline()
        #         if line:
        #             print line.rstrip('\n')
        # print cmd.process.returncode
        # sys.exit(0)

        # description = XMLDescription('/home/ms/Project/kiwi-maintenance/kiwi/template/ix86/suse-13.2-JeOS/config.xml')
        # xml = description.load()

        # print xml.get_name()
        # print xml.get_preferences()[0].get_type()[0].get_image()
        # xml.get_packages()[0].add_package(xml_parse.package(name='foo'))
        # for p in xml.get_packages()[0].get_package():
        #     print p.get_name()

        root = RootInit('/home/ms/__foo')
        root.create()

        self.root_bind = RootBind(root)
        self.root_bind.setup_intermediate_config()
        # self.root_bind.mount_kernel_file_systems()
        # self.root_bind.mount_shared_directory()

        repo = RepositoryZypper(self.root_bind)
        print repo.is_remote('http://download.suse.de/foo')
        print repo.is_remote('dir:///home/path/foo')

        repo.add_bootstrap_repo('foo', 'http://download.opensuse.org/distribution/13.2/repo/oss/', 'yast2')

        repo.delete_bootstrap_repo('foo')

    def __del__(self):
        try:
            self.root_bind.cleanup()
        except:
            pass
