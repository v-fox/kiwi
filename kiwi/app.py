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
