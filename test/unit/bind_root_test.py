from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiMountKernelFileSystemsError,
    KiwiMountSharedDirectoryError,
    KiwiSetupIntermediateConfigError
)

from kiwi.bind_root import BindRoot


class TestBindRoot(object):
    def __init__(self):
        root = mock.Mock()
        root.root_dir = 'root-dir'
        self.bind_root = BindRoot(root)
        self.bind_root.cleanup_files = ['/foo.kiwi']
        self.bind_root.config_files = ['/foo']
        self.bind_root.bind_locations = ['/foo']
        self.bind_root.mount_stack = ['/mountpoint']

    @raises(KiwiMountKernelFileSystemsError)
    @patch('kiwi.command.Command')
    def test_kernel_file_systems_raises_error(self, mock_command):
        mock_command.side_effect = KiwiMountKernelFileSystemsError(
            'mount-error'
        )
        self.bind_root.mount_kernel_file_systems()

    @raises(KiwiMountSharedDirectoryError)
    @patch('kiwi.command.Command')
    def test_shared_directory_raises_error(self, mock_command):
        mock_command.side_effect = KiwiMountSharedDirectoryError(
            'mount-error'
        )
        self.bind_root.mount_shared_directory()

    @raises(KiwiSetupIntermediateConfigError)
    @patch('kiwi.command.Command')
    def test_intermediate_config_raises_error(self, mock_command):
        mock_command.side_effect = KiwiSetupIntermediateConfigError(
            'config-error'
        )
        self.bind_root.setup_intermediate_config()

    @patch('kiwi.command.Command.run')
    def test_kernel_file_systems(self, mock_command):
        self.bind_root.mount_kernel_file_systems()
        mock_command.assert_called_once_with(
            ['mount', '-n', '--bind', '/foo', 'root-dir/foo']
        )

    @patch('kiwi.command.Command.run')
    def test_shared_directory(self, mock_command):
        self.bind_root.mount_shared_directory()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'mkdir', '-p', 'root-dir/var/cache/kiwi'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'mount', '-n', '--bind', '/var/cache/kiwi',
                'root-dir/var/cache/kiwi'
            ])

    @patch('kiwi.command.Command.run')
    def test_intermediate_config(self, mock_command):
        self.bind_root.setup_intermediate_config()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'cp', '/foo', 'root-dir/foo.kiwi'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'ln', '-s', '-f', 'foo.kiwi', 'root-dir/foo'
            ])

    @patch('kiwi.command.Command.run')
    @patch('os.path.islink')
    def test_cleanup(self, mock_islink, mock_command):
        mock_islink.return_value = True
        self.bind_root.cleanup()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'umount', 'root-dir/var/cache/kiwi'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'rmdir', 'root-dir/var/cache/kiwi'
            ])
        call = mock_command.call_args_list[2]
        assert mock_command.call_args_list[2] == \
            call([
                'umount', 'root-dir/mountpoint'
            ])
        call = mock_command.call_args_list[3]
        assert mock_command.call_args_list[3] == \
            call([
                'rm', '-f', 'root-dir/foo.kiwi'
            ])

    @patch('kiwi.command.Command.run')
    def test_cleanup_no_stop_on_exception(self, mock_command):
        mock_command.side_effect = Exception
        self.bind_root.cleanup()
