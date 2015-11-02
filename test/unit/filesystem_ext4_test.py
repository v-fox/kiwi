from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.filesystem_ext4 import FileSystemExt4


class TestFileSystemExt4(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = True
        self.ext4 = FileSystemExt4('source_dir')
        self.ext4.setup_mountpoint = mock.Mock(
            return_value='some-mount-point'
        )

    @patch('kiwi.filesystem_ext4.Command.run')
    def test_create_on_device(self, mock_command):
        self.ext4.create_on_device('/dev/foo')
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call(['mkfs.ext4', '/dev/foo'])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call(['mount', '/dev/foo', 'some-mount-point'])
