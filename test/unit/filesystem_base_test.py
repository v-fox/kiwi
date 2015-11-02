from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.filesystem_base import FileSystemBase


class TestFileSystemBase(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = True
        self.fsbase = FileSystemBase('source_dir')

    @raises(KiwiFileSystemSetupError)
    def test_source_dir_does_not_exist(self):
        FileSystemBase('source_dir_not_existing')

    @raises(NotImplementedError)
    def test_create_on_device(self):
        self.fsbase.create_on_device('/dev/foo')

    @raises(NotImplementedError)
    def test_create_on_file(self):
        self.fsbase.create_on_file('myimage')

    def test_post_init(self):
        self.fsbase.post_init(None)
        assert self.fsbase.custom_args == []

    @patch('kiwi.filesystem_base.mkdtemp')
    @patch('kiwi.filesystem_base.Command.run')
    def test_setup_mountpoint(self, mock_command, mock_mkdtemp):
        mock_mkdtemp.return_value = 'tmpdir'
        assert self.fsbase.setup_mountpoint() == 'tmpdir'
        assert self.fsbase.mountpoint == 'tmpdir'
        self.fsbase.mountpoint = None

    @patch('kiwi.filesystem_base.Command.run')
    def test_is_mounted_true(self, mock_command):
        self.fsbase.mountpoint = 'tmpdir'
        assert self.fsbase.is_mounted()
        mock_command.assert_called_once_with(['mountpoint', 'tmpdir'])
        self.fsbase.mountpoint = None

    @patch('kiwi.filesystem_base.Command.run')
    def test_is_mounted_false(self, mock_command):
        mock_command.side_effect = Exception
        self.fsbase.mountpoint = 'tmpdir'
        assert self.fsbase.is_mounted() == False
        self.fsbase.mountpoint = None

    @patch('kiwi.filesystem_base.Command.run')
    @patch('kiwi.filesystem_base.FileSystemBase.is_mounted')
    def test_sync_data(self, mock_mounted, mock_command):
        mock_mounted.return_value = True
        self.fsbase.mountpoint = 'tmpdir'
        self.fsbase.sync_data(['exclude_me'])
        mock_command.assert_called_once_with(
            [
                'rsync', '-a', '-H', '-X', '-A', '--one-file-system',
                '--exclude', '/exclude_me',
                'source_dir', 'tmpdir'
            ]
        )
        self.fsbase.mountpoint = None

    @patch('kiwi.filesystem_base.Command.run')
    @patch('kiwi.filesystem_base.FileSystemBase.is_mounted')
    def test_destructor_valid_mountpoint(self, mock_mounted, mock_command):
        mock_mounted.return_value = True
        self.fsbase.mountpoint = 'tmpdir'
        self.fsbase.__del__()
        self.fsbase.mountpoint = None
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call(['umount', 'tmpdir'])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call(['rmdir', 'tmpdir'])
