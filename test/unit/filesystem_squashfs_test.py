from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.filesystem_squashfs import FileSystemSquashFs


class TestFileSystemSquashfs(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = True
        self.squashfs = FileSystemSquashFs('source_dir')

    @patch('kiwi.filesystem_squashfs.Command.run')
    def test_create_on_file(self, mock_command):
        self.squashfs.create_on_file('myimage')
        mock_command.assert_called_once_with(
            ['mksquashfs', 'source_dir', 'myimage']
        )
