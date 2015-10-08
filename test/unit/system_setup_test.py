from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.system_setup import SystemSetup


class TestSystemSetup(object):
    def setup(self):
        self.xml = mock.Mock()
        self.setup = SystemSetup(self.xml, 'description_dir', 'root_dir')

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
        assert self.xml.export.called
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

    @raises(NotImplementedError)
    def test_import_shell_environment(self):
        self.setup.import_shell_environment()

    @patch('kiwi.command.Command.run')
    @patch('os.path.exists')
    def test_import_overlay_files(self, mock_os_path, mock_command):
        mock_os_path.return_value = True
        self.setup.import_overlay_files(follow_links=True)
        mock_command.assert_called_once_with(
            [
                'rsync', '-a', '-H', '-X', '-A',
                '--one-file-system', '--copy-links',
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

    @patch('kiwi.command.Command.run')
    def test_call_config_script(self, mock_command):
        self.setup.call_config_script()
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', '/image/config.sh']
        )

    @patch('kiwi.command.Command.run')
    def test_call_image_script(self, mock_command):
        self.setup.call_image_script()
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', '/image/images.sh']
        )
