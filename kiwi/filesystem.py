# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
# project
from filesystem_ext2 import FileSystemExt2
from filesystem_ext3 import FileSystemExt3
from filesystem_ext4 import FileSystemExt4
from filesystem_btrfs import FileSystemBtrfs
from filesystem_xfs import FileSystemXfs
from filesystem_squashfs import FileSystemSquashFs
from loop_device import LoopDevice
from system_size import SystemSize
from defaults import Defaults
from logger import log

from exceptions import (
    KiwiFileSystemSetupError
)


class FileSystem(object):
    """
        Filesystem image builder
    """
    def __init__(self, xml_state, target_dir, source_dir, custom_args=None):
        self.source_dir = source_dir
        self.custom_args = custom_args
        self.requested_filesystem = xml_state.get_build_type_name()
        self.filename = ''.join(
            [
                target_dir, '/',
                xml_state.xml_data.get_name(), '.', self.requested_filesystem
            ]
        )
        self.blocksize = xml_state.build_type.get_target_blocksize()
        self.size = SystemSize(xml_state, source_dir)
        self.filesystems_no_device_node = [
            'squashfs'
        ]

    def create(self):
        log.info(
            'Creating %s filesystem', self.requested_filesystem
        )
        supported_filesystems = Defaults.get_filesystem_image_types()
        if self.requested_filesystem not in supported_filesystems:
            raise KiwiFileSystemSetupError(
                'Unknown filesystem: %s' % self.requested_filesystem
            )
        if self.requested_filesystem not in self.filesystems_no_device_node:
            self.__operate_on_loop()
        else:
            self.__operate_on_file()

    def __operate_on_loop(self):
        filesystem = None
        loop_provider = LoopDevice(
            self.filename, self.size.get_size_mbytes(), self.blocksize
        )
        loop_provider.create()
        if self.requested_filesystem == 'ext2':
            filesystem = FileSystemExt2(
                self.source_dir, self.custom_args, loop_provider
            )
        elif self.requested_filesystem == 'ext3':
            filesystem = FileSystemExt3(
                self.source_dir, self.custom_args, loop_provider
            )
        elif self.requested_filesystem == 'ext4':
            filesystem = FileSystemExt4(
                self.source_dir, self.custom_args, loop_provider
            )
        elif self.requested_filesystem == 'btrfs':
            filesystem = FileSystemBtrfs(
                self.source_dir, self.custom_args, loop_provider
            )
        elif self.requested_filesystem == 'xfs':
            filesystem = FileSystemXfs(
                self.source_dir, self.custom_args, loop_provider
            )
        else:
            raise KiwiFileSystemSetupError(
                'Support for %s filesystem not implemented' %
                self.requested_filesystem
            )
        filesystem.create_on_device(loop_provider.node_name)
        log.info(
            '--> Syncing data to filesystem on %s', loop_provider.node_name
        )
        exclude_list = [
            'image', '.profile', '.kconfig'
        ]
        filesystem.sync_data(exclude_list)

    def __operate_on_file(self):
        if self.requested_filesystem == 'squashfs':
            filesystem = FileSystemSquashFs(
                self.source_dir, self.custom_args
            )
        else:
            raise KiwiFileSystemSetupError(
                'Support for %s filesystem not implemented' %
                self.requested_filesystem
            )
        filesystem.create_on_file(self.filename)
