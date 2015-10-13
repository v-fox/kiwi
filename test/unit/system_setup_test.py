from nose.tools import *
from mock import patch

import mock

import nose_helper
from collections import namedtuple

from kiwi.system_setup import SystemSetup

from kiwi.exceptions import *


class TestSystemSetup(object):
    def setup(self):
        self.xml_state = mock.MagicMock()
        self.setup = SystemSetup(
            self.xml_state, 'description_dir', 'root_dir'
        )

    @patch('kiwi.command.Command.run')
    @patch('__builtin__.open')
    @patch('os.path.exists')
    def test_import_description(self, mock_path, mock_open, mock_command):
        mock_path.return_value = True
        self.setup.import_description()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'mkdir', '-p', 'root_dir/image'
            ])
        assert self.xml_state.xml_data.export.called_once_with()
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'cp', 'description_dir/config.sh', 'root_dir/image'
            ])
        call = mock_command.call_args_list[2]
        assert mock_command.call_args_list[2] == \
            call([
                'cp', 'description_dir/images.sh', 'root_dir/image'
            ])

    @patch('kiwi.command.Command.run')
    def test_cleanup(self, mock_command):
        self.setup.cleanup()
        mock_command.assert_called_once_with(
            ['rm', '-r', '-f', '/.kconfig', '/image']
        )

    @patch('__builtin__.open')
    @patch('kiwi.profile.Profile.create')
    def test_import_shell_environment(self, mock_create, mock_open):
        context_manager_mock = mock.Mock()
        mock_open.return_value = context_manager_mock
        file_mock = mock.Mock()
        enter_mock = mock.Mock()
        exit_mock = mock.Mock()
        enter_mock.return_value = file_mock
        setattr(context_manager_mock, '__enter__', enter_mock)
        setattr(context_manager_mock, '__exit__', exit_mock)
        mock_create.return_value = ['a']

        self.setup.import_shell_environment()

        mock_create.assert_called_once_with()
        mock_open.assert_called_once_with('root_dir/.profile', 'w')
        file_mock.write.assert_called_once_with('a\n')

    @patch('kiwi.command.Command.run')
    @patch('os.path.exists')
    def test_import_overlay_files_copy_links(self, mock_os_path, mock_command):
        mock_os_path.return_value = True
        self.setup.import_overlay_files(
            follow_links=True, preserve_owner_group=True
        )
        mock_command.assert_called_once_with(
            [
                'rsync', '-r', '-p', '-t', '-D', '-H', '-X', '-A',
                '--one-file-system', '--copy-links', '-o', '-g',
                'description_dir/root/', 'root_dir'
            ]
        )

    @patch('kiwi.command.Command.run')
    @patch('os.path.exists')
    def test_import_overlay_files_links(self, mock_os_path, mock_command):
        mock_os_path.return_value = True
        self.setup.import_overlay_files(
            follow_links=False, preserve_owner_group=True
        )
        mock_command.assert_called_once_with(
            [
                'rsync', '-r', '-p', '-t', '-D', '-H', '-X', '-A',
                '--one-file-system', '--links', '-o', '-g',
                'description_dir/root/', 'root_dir'
            ]
        )

    @raises(NotImplementedError)
    def test_import_autoyast_profile(self):
        self.setup.import_autoyast_profile()

    @raises(NotImplementedError)
    def test_setup_hardware_clock(self):
        self.setup.setup_hardware_clock()

    @raises(NotImplementedError)
    def test_setup_keyboard_map(self):
        self.setup.setup_keyboard_map()

    @raises(NotImplementedError)
    def test_setup_locale(self):
        self.setup.setup_locale()

    @raises(NotImplementedError)
    def test_setup_timezone(self):
        self.setup.setup_timezone()

    @raises(NotImplementedError)
    def test_setup_groups(self):
        self.setup.setup_groups()

    @raises(NotImplementedError)
    def test_setup_users(self):
        self.setup.setup_users()

    @raises(NotImplementedError)
    def test_import_image_identifier(self):
        self.setup.import_image_identifier()

    @patch('kiwi.command.Command.call')
    @patch('kiwi.command_process.CommandProcess.poll_and_watch')
    @patch('os.path.exists')
    def test_call_config_script(self, mock_os_path, mock_watch, mock_command):
        result_type = namedtuple(
            'result', ['stderr', 'returncode']
        )
        mock_result = result_type(stderr='stderr', returncode=0)
        mock_os_path.return_value = True
        mock_watch.return_value = mock_result
        self.setup.call_config_script()
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'bash', '-x', '/image/config.sh']
        )

    @patch('kiwi.command.Command.call')
    @patch('kiwi.command_process.CommandProcess.poll_and_watch')
    @patch('os.path.exists')
    def test_call_image_script(self, mock_os_path, mock_watch, mock_command):
        result_type = namedtuple(
            'result_type', ['stderr', 'returncode']
        )
        mock_result = result_type(stderr='stderr', returncode=0)
        mock_os_path.return_value = True
        mock_watch.return_value = mock_result
        self.setup.call_image_script()
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'bash', '-x', '/image/images.sh']
        )

    @raises(KiwiScriptFailed)
    @patch('kiwi.command.Command.call')
    @patch('kiwi.command_process.CommandProcess.poll_and_watch')
    @patch('os.path.exists')
    def test_call_image_script_raises(
        self, mock_os_path, mock_watch, mock_command
    ):
        result_type = namedtuple(
            'result_type', ['stderr', 'returncode']
        )
        mock_result = result_type(stderr='stderr', returncode=1)
        mock_os_path.return_value = True
        mock_watch.return_value = mock_result
        self.setup.call_image_script()
