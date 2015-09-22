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
from cli_task import CliTask


import logging
import sys

import xml_parse
from xml_description import XMLDescription

from root_init import RootInit
from root_bind import RootBind
from repository_zypper import RepositoryZypper
from manager_zypper import ManagerZypper
from command import Command
from xml_state import XMLState


class App(object):
    """
        Application class to create task instances and process them
    """
    def __init__(self):
        app = CliTask()
        action = app.cli.get_command()
        service = app.cli.get_servicename()
        task_class_name = service.title() + action.title() + 'Task'
        task_class = app.task.__dict__[task_class_name]
        task_class().process()

    def playground(self):
        # playground only, some testing code

        from logger import log
        log.setLevel(logging.DEBUG)

        description = XMLDescription('/home/ms/Project/kiwi-maintenance/kiwi/template/ix86/suse-13.2-JeOS/config.xml')
        xml = description.load()

        print xml.get_name()
        print xml.get_preferences()[0].get_type()[0].get_image()
        xml.get_packages()[0].add_package(xml_parse.package(name='foo'))

        print "####### BUILD TYPE ############"

        print XMLState.build_type(xml)

        print "----------"

        for p in XMLState.profiled(xml.get_packages(), matching=['vmxFlavour']):
            print
            print '#########################'
            print p.get_profiles()
            for i in p.get_package():
                print i.get_name()

        # sys.exit(0)

        root = RootInit('/home/ms/__foo', allow_existing=True)
        root.create()

        self.root_bind = RootBind(root)
        self.root_bind.setup_intermediate_config()
        # self.root_bind.mount_kernel_file_systems()
        # self.root_bind.mount_shared_directory()

        repo = RepositoryZypper(self.root_bind)

        repo.delete_bootstrap_repo('foo')

        repo.add_bootstrap_repo('foo', 'http://download.opensuse.org/distribution/13.2/repo/oss/', 'yast2')

        manager = ManagerZypper(repo)
        manager.request_package('zypper')

        # bootstrap phase
        zypper = manager.install_requests_bootstrap()
        while zypper.process.poll() is None:
            line = zypper.output.readline()
            if line:
                print line.rstrip('\n')

        print zypper.process.returncode

        # install in new root
        manager.request_package('vim')
        zypper = manager.install_requests()
        while zypper.process.poll() is None:
            line = zypper.output.readline()
            if line:
                print line.rstrip('\n')

        print zypper.process.returncode

        repo.delete_bootstrap_repo('foo')

    def __del__(self):
        try:
            self.root_bind.cleanup()
        except:
            pass
