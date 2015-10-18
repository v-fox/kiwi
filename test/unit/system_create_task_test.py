import sys
import mock
from nose.tools import *
from mock import patch

import kiwi

import nose_helper

from kiwi.system_create_task import SystemCreateTask


class TestSystemCreateTask(object):
    def setup(self):
        sys.argv = [
            sys.argv[0], '--profile', 'vmxFlavour', 'system', 'create',
            '--root', '../data/root-dir', '--target-dir', 'some-target'
        ]
        kiwi.system_create_task.Help = mock.Mock(
            return_value=mock.Mock()
        )
        self.boot_task = mock.MagicMock()
        kiwi.system_create_task.BootImageTask = mock.Mock(
            return_value=self.boot_task
        )
        self.task = SystemCreateTask()

    def __init_command_args(self):
        self.task.command_args = {}
        self.task.command_args['help'] = False
        self.task.command_args['create'] = False
        self.task.command_args['--root'] = '../data/root-dir'
        self.task.command_args['--target-dir'] = 'some-target'

    def test_process_system_create(self):
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = True
        self.task.process()
        # TODO
        self.boot_task.process.assert_called_once_with()

    def test_process_system_create_help(self):
        self.__init_command_args()
        self.task.command_args['help'] = True
        self.task.command_args['create'] = True
        self.task.process()
        self.task.manual.show.assert_called_once_with(
            'kiwi::system::create'
        )
