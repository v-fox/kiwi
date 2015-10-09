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

# project
from command import Command
from logger import log

from exceptions import (
    KiwiMountKernelFileSystemsError,
    KiwiMountSharedDirectoryError,
    KiwiSetupIntermediateConfigError
)


class RootBind(object):
    """
        Implements binding/copying of host system paths
        into the new root directory
    """
    def __init__(self, root_init):
        self.root_dir = root_init.root_dir
        self.cleanup_files = []
        self.mount_stack = []
        self.dir_stack = []
        # need resolv.conf/hosts for chroot name resolution
        # need /etc/sysconfig/proxy for chroot proxy usage
        self.config_files = [
            '/etc/resolv.conf',
            '/etc/hosts',
            '/etc/sysconfig/proxy'
        ]
        # need kernel filesystems bind mounted
        self.bind_locations = [
            '/proc',
            '/dev',
            '/var/run/dbus',
            '/sys'
        ]
        # share the following directory with the host
        self.shared_location = '/var/cache/kiwi'

    def mount_kernel_file_systems(self):
        try:
            for location in self.bind_locations:
                Command.run(
                    [
                        'mount', '-n', '--bind', location,
                        self.root_dir + location
                    ]
                )
                self.mount_stack.append(location)
        except Exception as e:
            self.cleanup()
            raise KiwiMountKernelFileSystemsError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def mount_shared_directory(self, host_dir=None):
        if not host_dir:
            host_dir = self.shared_location
        try:
            Command.run(['mkdir', '-p', self.root_dir + host_dir])
            Command.run(
                [
                    'mount', '-n', '--bind', host_dir, self.root_dir + host_dir
                ]
            )
            self.mount_stack.append(host_dir)
            self.dir_stack.append(host_dir)
        except Exception as e:
            self.cleanup()
            raise KiwiMountSharedDirectoryError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def setup_intermediate_config(self):
        try:
            for config in self.config_files:
                self.cleanup_files.append(config + '.kiwi')
                Command.run(
                    ['cp', config, self.root_dir + config + '.kiwi']
                )
                link_target = os.path.basename(config) + '.kiwi'
                Command.run(
                    ['ln', '-s', '-f', link_target, self.root_dir + config]
                )
        except Exception as e:
            self.cleanup()
            raise KiwiSetupIntermediateConfigError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def move_to_root(self, elements):
        result = []
        for element in elements:
            result.append(element.replace(self.root_dir, '/'))
        return result

    def cleanup(self):
        self.__cleanup_mount_stack()
        self.__cleanup_dir_stack()
        self.__cleanup_intermediate_config()

    def __cleanup_intermediate_config(self):
        # delete kiwi copied config files
        config_files_to_delete = []

        for config in self.cleanup_files:
            config_files_to_delete.append(self.root_dir + config)

        del self.cleanup_files[:]

        # delete stale symlinks if there are any. normally the package
        # installation process should have replaced the symlinks with
        # real files from the packages
        for config in self.config_files:
            if os.path.islink(self.root_dir + config):
                config_files_to_delete.append(self.root_dir + config)

        try:
            Command.run(['rm', '-f'] + config_files_to_delete)
        except Exception as e:
            log.warn(
                'Failed to remove intermediate config files: %s', format(e)
            )

    def __cleanup_mount_stack(self):
        try:
            result = Command.run(['umount'] + self.__build_mount_list())
        except Exception as e:
            log.warn(
                'Image root directory %s not cleanly umounted: %s',
                self.root_dir, format(e)
            )

        del self.mount_stack[:]

    def __cleanup_dir_stack(self):
        for location in reversed(self.dir_stack):
            try:
                Command.run(
                    [
                        'rmdir', '-p', '--ignore-fail-on-non-empty',
                        self.root_dir + location
                    ]
                )
            except Exception as e:
                log.warn(
                    'Failed to remove directory %s: %s', location, format(e)
                )
        del self.dir_stack[:]

    def __build_mount_list(self):
        mount_points = []
        for location in reversed(self.mount_stack):
            mount_path = self.root_dir + location
            try:
                Command.run(['mountpoint', '-q', mount_path])
                mount_points.append(mount_path)
            except Exception:
                log.warn('Path %s not a mountpoint', mount_path)
        return mount_points
