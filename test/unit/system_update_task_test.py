import sys
import mock
from nose.tools import *
from mock import patch

import kiwi

import nose_helper

from kiwi.system_update_task import SystemUpdateTask


class TestSystemUpdateTask(object):
    def setup(self):
        sys.argv = [
            sys.argv[0], '--profile', 'vmxFlavour', 'system', 'update',
            '--root', '../data/root-dir'
        ]
        self.task = SystemUpdateTask()
        kiwi.system_update_task.System = mock.Mock(
            return_value=mock.Mock()
        )
        kiwi.system_update_task.Help = mock.Mock(
            return_value=mock.Mock()
        )

    def __init_command_args(self):
        self.task.command_args = {}
        self.task.command_args['help'] = False
        self.task.command_args['update'] = False
        self.task.command_args['--add-package'] = []
        self.task.command_args['--delete-package'] = []
        self.task.command_args['--root'] = '../data/root-dir'

    def test_process_system_update(self):
        self.__init_command_args()
        self.task.command_args['update'] = True
        self.task.process()
        self.task.system.setup_root.assert_called_once_with(
            self.task.command_args['--root']
        )
        self.task.system.setup_repositories.assert_called_once_with()
        self.task.system.update_system.assert_called_once_with()

    def test_process_system_update_add_package(self):
        self.__init_command_args()
        self.task.command_args['update'] = True
        self.task.command_args['--add-package'] = ['vim']
        self.task.process()
        self.task.system.setup_root.assert_called_once_with(
            self.task.command_args['--root']
        )
        self.task.system.setup_repositories.assert_called_once_with()
        self.task.system.install_packages.assert_called_once_with(['vim'])

    def test_process_system_update_delete_package(self):
        self.__init_command_args()
        self.task.command_args['update'] = True
        self.task.command_args['--delete-package'] = ['vim']
        self.task.process()
        self.task.system.setup_root.assert_called_once_with(
            self.task.command_args['--root']
        )
        self.task.system.setup_repositories.assert_called_once_with()
        self.task.system.delete_packages.assert_called_once_with(['vim'])

    def test_process_system_update_help(self):
        self.__init_command_args()
        self.task.command_args['help'] = True
        self.task.command_args['update'] = True
        self.task.process()
        self.task.manual.show.assert_called_once_with(
            'kiwi::system::update'
        )
