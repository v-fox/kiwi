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
import os
from tempfile import mkdtemp

# project
from command import Command
from logger import log

from exceptions import (
    KiwiFileSystemSetupError
)


class FileSystemBase(object):
    """
        Implements base class for filesystem interface
    """
    def __init__(self, source_dir, custom_args=None, device_provider=None):
        # bind the block device providing class instance to this object.
        # This is done to guarantee the correct destructor order when
        # the device should be released. This is only required if the
        # filesystem required a block device to become created
        self.device_provider = device_provider

        # filesystems created with a block device stores the mountpoint
        # here. The file name of the file containing the filesystem is
        # stored in the device_provider if the filesystem is represented
        # as a file there
        self.mountpoint = None

        if not os.path.exists(source_dir):
            raise KiwiFileSystemSetupError(
                'given source directory %s does not exist' % source_dir
            )
        self.source_dir = source_dir

        # filesystems created without a block device stores the result
        # filesystem file name here
        self.filename = None

        self.post_init(custom_args)

    def post_init(self, custom_args):
        self.custom_args = custom_args
        if not custom_args:
            self.custom_args = []

    def create_on_device(self, device):
        # implement for filesystems which requires a block device to
        # become created, e.g ext4.
        raise NotImplementedError

    def create_on_file(self, filename):
        # implement for filesystems which doesn't need a block device
        # to become created, e.g squashfs
        raise NotImplementedError

    def setup_mountpoint(self):
        self.mountpoint = mkdtemp(prefix='kiwi_filesystem.')
        return self.mountpoint

    def sync_data(self, exclude=None):
        if self.mountpoint and self.is_mounted():
            exclude_options = []
            if exclude:
                for item in exclude:
                    exclude_options.append('--exclude')
                    exclude_options.append(
                        '/' + item
                    )
            Command.run(
                [
                    'rsync', '-a', '-H', '-X', '-A', '--one-file-system'
                ] + exclude_options + [
                    self.source_dir, self.mountpoint
                ]
            )

    def is_mounted(self):
        if self.mountpoint:
            try:
                Command.run(['mountpoint', self.mountpoint])
                return True
            except Exception:
                pass
        return False

    def __del__(self):
        if self.mountpoint:
            log.info('Cleaning up %s instance', type(self).__name__)
            if self.is_mounted():
                Command.run(['umount', self.mountpoint])
            Command.run(['rmdir', self.mountpoint])
