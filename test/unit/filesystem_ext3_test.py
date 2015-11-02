from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.filesystem_ext3 import FileSystemExt3


class TestFileSystemExt3(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = True
        self.ext3 = FileSystemExt3('source_dir')
        self.ext3.setup_mountpoint = mock.Mock(
            return_value='some-mount-point'
        )

    @patch('kiwi.filesystem_ext3.Command.run')
    def test_create_on_device(self, mock_command):
        self.ext3.create_on_device('/dev/foo')
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call(['mkfs.ext3', '/dev/foo'])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call(['mount', '/dev/foo', 'some-mount-point'])
