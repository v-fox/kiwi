from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.filesystem import FileSystem


class TestFileSystem(object):
    @patch('kiwi.filesystem.SystemSize')
    def setup(self, mock_size):
        self.loop_provider = mock.Mock()
        self.loop_provider.node_name = '/dev/loop1'
        self.loop_provider.create = mock.Mock()

        self.xml_state = mock.Mock()
        self.xml_state.get_build_type_name = mock.Mock(
            return_value='super-fs'
        )
        self.xml_state.xml_data.get_name = mock.Mock(
            return_value='myimage'
        )
        self.xml_state.build_type.get_target_blocksize = mock.Mock(
            return_value=4096
        )
        size = mock.Mock()
        size.get_size_mbytes = mock.Mock(
            return_value=42
        )
        mock_size.return_value = size
        self.fs = FileSystem(self.xml_state, 'target_dir', 'source_dir')

    @raises(KiwiFileSystemSetupError)
    def test_create_unknown_filesystem(self):
        self.fs.create()

    @patch('kiwi.defaults.Defaults.get_filesystem_image_types')
    @patch('kiwi.filesystem.LoopDevice')
    @raises(KiwiFileSystemSetupError)
    def test_create_unsupported_on_loop_filesystem(self, mock_loop, mock_types):
        mock_types.return_value = [self.fs.requested_filesystem]
        self.fs.create()

    @patch('kiwi.defaults.Defaults.get_filesystem_image_types')
    @raises(KiwiFileSystemSetupError)
    def test_create_unsupported_on_file_filesystem(self, mock_types):
        mock_types.return_value = [self.fs.requested_filesystem]
        self.fs.filesystems_no_device_node = [self.fs.requested_filesystem]
        self.fs.create()

    @patch('kiwi.filesystem.LoopDevice')
    @patch('kiwi.filesystem.FileSystemExt2')
    def test_create_on_loop_ext2(self, mock_ext2, mock_loop):
        self.fs.requested_filesystem = 'ext2'
        ext2 = mock.Mock()
        ext2.create_on_device = mock.Mock()
        mock_loop.return_value = self.loop_provider
        mock_ext2.return_value = ext2
        self.fs.create()
        mock_loop.assert_called_once_with(
            'target_dir/myimage.super-fs', 42, 4096
        )
        self.loop_provider.create.assert_called_once_with()
        mock_ext2.assert_called_once_with(
            'source_dir', None, self.loop_provider
        )
        ext2.create_on_device.assert_called_once_with('/dev/loop1')
        ext2.sync_data.assert_called_once_with(
            ['image', '.profile', '.kconfig']
        )

    @patch('kiwi.filesystem.LoopDevice')
    @patch('kiwi.filesystem.FileSystemExt3')
    def test_create_on_loop_ext3(self, mock_ext3, mock_loop):
        self.fs.requested_filesystem = 'ext3'
        ext3 = mock.Mock()
        ext3.create_on_device = mock.Mock()
        mock_loop.return_value = self.loop_provider
        mock_ext3.return_value = ext3
        self.fs.create()
        mock_loop.assert_called_once_with(
            'target_dir/myimage.super-fs', 42, 4096
        )
        self.loop_provider.create.assert_called_once_with()
        mock_ext3.assert_called_once_with(
            'source_dir', None, self.loop_provider
        )
        ext3.create_on_device.assert_called_once_with('/dev/loop1')
        ext3.sync_data.assert_called_once_with(
            ['image', '.profile', '.kconfig']
        )

    @patch('kiwi.filesystem.LoopDevice')
    @patch('kiwi.filesystem.FileSystemExt4')
    def test_create_on_loop_ext4(self, mock_ext4, mock_loop):
        self.fs.requested_filesystem = 'ext4'
        ext4 = mock.Mock()
        ext4.create_on_device = mock.Mock()
        mock_loop.return_value = self.loop_provider
        mock_ext4.return_value = ext4
        self.fs.create()
        mock_loop.assert_called_once_with(
            'target_dir/myimage.super-fs', 42, 4096
        )
        self.loop_provider.create.assert_called_once_with()
        mock_ext4.assert_called_once_with(
            'source_dir', None, self.loop_provider
        )
        ext4.create_on_device.assert_called_once_with('/dev/loop1')
        ext4.sync_data.assert_called_once_with(
            ['image', '.profile', '.kconfig']
        )

    @patch('kiwi.filesystem.LoopDevice')
    @patch('kiwi.filesystem.FileSystemBtrfs')
    def test_create_on_loop_btrfs(self, mock_btrfs, mock_loop):
        self.fs.requested_filesystem = 'btrfs'
        btrfs = mock.Mock()
        btrfs.create_on_device = mock.Mock()
        mock_loop.return_value = self.loop_provider
        mock_btrfs.return_value = btrfs
        self.fs.create()
        mock_loop.assert_called_once_with(
            'target_dir/myimage.super-fs', 42, 4096
        )
        self.loop_provider.create.assert_called_once_with()
        mock_btrfs.assert_called_once_with(
            'source_dir', None, self.loop_provider
        )
        btrfs.create_on_device.assert_called_once_with('/dev/loop1')
        btrfs.sync_data.assert_called_once_with(
            ['image', '.profile', '.kconfig']
        )

    @patch('kiwi.filesystem.LoopDevice')
    @patch('kiwi.filesystem.FileSystemXfs')
    def test_create_on_loop_xfs(self, mock_xfs, mock_loop):
        self.fs.requested_filesystem = 'xfs'
        xfs = mock.Mock()
        xfs.create_on_device = mock.Mock()
        mock_loop.return_value = self.loop_provider
        mock_xfs.return_value = xfs
        self.fs.create()
        mock_loop.assert_called_once_with(
            'target_dir/myimage.super-fs', 42, 4096
        )
        self.loop_provider.create.assert_called_once_with()
        mock_xfs.assert_called_once_with(
            'source_dir', None, self.loop_provider
        )
        xfs.create_on_device.assert_called_once_with('/dev/loop1')
        xfs.sync_data.assert_called_once_with(
            ['image', '.profile', '.kconfig']
        )

    @patch('kiwi.filesystem.FileSystemSquashFs')
    def test_create_on_file_squashfs(self, mock_squashfs):
        self.fs.requested_filesystem = 'squashfs'
        squashfs = mock.Mock()
        squashfs.create_on_file = mock.Mock()
        mock_squashfs.return_value = squashfs
        self.fs.create()
        mock_squashfs.assert_called_once_with('source_dir', None)
        squashfs.create_on_file.assert_called_once_with(
            'target_dir/myimage.super-fs'
        )
