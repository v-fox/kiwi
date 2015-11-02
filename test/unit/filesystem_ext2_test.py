from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.filesystem_ext2 import FileSystemExt2


class TestFileSystemExt2(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = True
        self.ext2 = FileSystemExt2('source_dir')
        self.ext2.setup_mountpoint = mock.Mock(
            return_value='some-mount-point'
        )

    @patch('kiwi.filesystem_ext2.Command.run')
    def test_create_on_device(self, mock_command):
        self.ext2.create_on_device('/dev/foo')
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call(['mkfs.ext2', '/dev/foo'])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call(['mount', '/dev/foo', 'some-mount-point'])
