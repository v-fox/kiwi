import sys
import mock
from nose.tools import *
from mock import patch

import kiwi

import nose_helper

from kiwi.system_prepare_task import SystemPrepareTask


class TestSystemPrepareTask(object):
    def setup(self):
        sys.argv = [
            sys.argv[0], '--profile', 'vmxFlavour', 'system', 'prepare',
            '--description', '../data/description',
            '--root', '../data/root-dir'
        ]
        self.task = SystemPrepareTask()
        kiwi.system_prepare_task.System = mock.Mock(
            return_value=mock.Mock()
        )
        kiwi.system_prepare_task.SystemSetup = mock.Mock(
            return_value=mock.Mock()
        )
        kiwi.system_prepare_task.Help = mock.Mock(
            return_value=mock.Mock()
        )

    def __init_command_args(self):
        self.task.command_args = {}
        self.task.command_args['help'] = False
        self.task.command_args['prepare'] = False
        self.task.command_args['--description'] = '../data/description'
        self.task.command_args['--root'] = '../data/root-dir'
        self.task.command_args['--type'] = None
        self.task.command_args['--allow-existing-root'] = False
        self.task.command_args['--set-repo'] = None
        self.task.command_args['--add-repo'] = []

    def test_process_system_prepare(self):
        self.__init_command_args()
        self.task.command_args['prepare'] = True
        self.task.process()
        self.task.system.setup_root.assert_called_once_with(
            self.task.command_args['--root']
        )
        self.task.system.setup_repositories.assert_called_once_with()
        self.task.system.install_bootstrap.assert_called_once_with()
        self.task.system.install_system.assert_called_once_with(
            self.task.command_args['--type']
        )
        self.task.setup.import_description.assert_called_once_with()

    @patch('kiwi.xml_state.XMLState.set_repository')
    def test_process_system_prepare_set_repo(self, mock_state):
        self.__init_command_args()
        self.task.command_args['--set-repo'] = 'http://example.com,yast2,alias'
        self.task.process()
        mock_state.assert_called_once_with(
            self.task.xml, 'http://example.com',
            'yast2', 'alias', None, ['vmxFlavour']
        )

    @patch('kiwi.xml_state.XMLState.add_repository')
    def test_process_system_prepare_add_repo(self, mock_state):
        self.__init_command_args()
        self.task.command_args['--add-repo'] = [
            'http://example.com,yast2,alias'
        ]
        self.task.process()
        mock_state.assert_called_once_with(
            self.task.xml, 'http://example.com',
            'yast2', 'alias', None
        )

    def test_process_system_prepare_help(self):
        self.__init_command_args()
        self.task.command_args['help'] = True
        self.task.command_args['prepare'] = True
        self.task.process()
        self.task.manual.show.assert_called_once_with(
            'kiwi::system::prepare'
        )
