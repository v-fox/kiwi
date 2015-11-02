import sys
import mock
from nose.tools import *
from mock import patch

import kiwi

import nose_helper

from kiwi.system_create_task import SystemCreateTask
from kiwi.exceptions import *


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
        self.filesystem = mock.MagicMock()
        kiwi.system_create_task.FileSystem = mock.Mock(
            return_value=self.filesystem
        )
        self.task = SystemCreateTask()

    def __init_command_args(self):
        self.task.command_args = {}
        self.task.command_args['help'] = False
        self.task.command_args['create'] = False
        self.task.command_args['--root'] = '../data/root-dir'
        self.task.command_args['--target-dir'] = 'some-target'

    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_filesystem(self, mock_type):
        mock_type.return_value = 'ext4'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = False
        self.task.process()
        self.filesystem.create.assert_called_once_with()

    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_disk(self, mock_type):
        mock_type.return_value = 'oem'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = True
        self.task.process()
        self.boot_task.prepare.assert_called_once_with()
        self.boot_task.extract_kernel_files.assert_called_once_with()
        self.boot_task.create_initrd.assert_called_once_with()
        # TODO

    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_live(self, mock_type):
        mock_type.return_value = 'iso'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = True
        self.task.process()
        self.boot_task.prepare.assert_called_once_with()
        self.boot_task.extract_kernel_files.assert_called_once_with()
        self.boot_task.create_initrd.assert_called_once_with()
        # TODO

    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_pxe(self, mock_type):
        mock_type.return_value = 'pxe'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = True
        self.task.process()
        self.boot_task.prepare.assert_called_once_with()
        self.boot_task.extract_kernel_files.assert_called_once_with()
        self.boot_task.create_initrd.assert_called_once_with()
        # TODO

    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_archive(self, mock_type):
        mock_type.return_value = 'tbz'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = True
        self.task.process()
        self.boot_task.prepare.assert_called_once_with()
        self.boot_task.extract_kernel_files.assert_called_once_with()
        self.boot_task.create_initrd.assert_called_once_with()
        # TODO

    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_container(self, mock_type):
        mock_type.return_value = 'docker'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = True
        self.task.process()
        self.boot_task.prepare.assert_called_once_with()
        self.boot_task.extract_kernel_files.assert_called_once_with()
        self.boot_task.create_initrd.assert_called_once_with()
        # TODO

    @raises(KiwiRequestedTypeError)
    @patch('kiwi.xml_state.XMLState.get_build_type_name')
    def test_process_system_create_raise(self, mock_type):
        mock_type.return_value = 'foo'
        self.__init_command_args()
        self.task.command_args['create'] = True
        self.boot_task.required.return_value = False
        self.task.process()

    def test_process_system_create_help(self):
        self.__init_command_args()
        self.task.command_args['help'] = True
        self.task.command_args['create'] = True
        self.task.process()
        self.task.manual.show.assert_called_once_with(
            'kiwi::system::create'
        )
