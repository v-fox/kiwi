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

    @raises(NotImplementedError)
    def test_import_shell_environment(self):
        self.setup.import_shell_environment()

    @raises(NotImplementedError)
    def test_import_overlay_files(self):
        self.setup.import_overlay_files()

    @raises(NotImplementedError)
    def test_call_config_script(self):
        self.setup.call_config_script()

    @raises(NotImplementedError)
    def test_call_image_script(self):
        self.setup.call_image_script()
