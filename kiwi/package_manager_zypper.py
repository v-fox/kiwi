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
import re

# project
from command import Command
from package_manager_base import PackageManagerBase


class PackageManagerZypper(PackageManagerBase):
    """
        Implements install tasks for the zypper package manager
    """
    def post_init(self, custom_args=[]):
        self.custom_args = custom_args
        runtime_config = self.repository.runtime_config()

        self.zypper_args = runtime_config['zypper_args']
        self.command_env = runtime_config['command_env']

    def request_package(self, name):
        self.package_requests.append(name)

    def request_collection(self, name):
        self.collection_requests.append('pattern:' + name)

    def request_product(self, name):
        self.product_requests.append('product:' + name)

    def process_install_requests_bootstrap(self):
        return Command.call(
            ['zypper'] + self.zypper_args + [
                '--root', self.root_dir,
                'install', '--auto-agree-with-licenses'
            ] + self.custom_args + self.__install_items(),
            self.command_env
        )

    def process_install_requests(self):
        chroot_zypper_args = self.root_bind.move_to_root(
            self.zypper_args
        )
        return Command.call(
            ['chroot', self.root_dir, 'zypper'] + chroot_zypper_args + [
                'install', '--auto-agree-with-licenses'
            ] + self.custom_args + self.__install_items(),
            self.command_env
        )

    def process_delete_requests(self):
        chroot_zypper_args = self.root_bind.move_to_root(
            self.zypper_args
        )
        return Command.call(
            ['chroot', self.root_dir, 'zypper'] + chroot_zypper_args + [
                'remove', '-u', '--force-resolution'
            ] + self.__delete_items(),
            self.command_env
        )

    def update(self):
        chroot_zypper_args = self.root_bind.move_to_root(
            self.zypper_args
        )
        return Command.call(
            ['chroot', self.root_dir, 'zypper'] + chroot_zypper_args + [
                'update', '--auto-agree-with-licenses'
            ] + self.custom_args,
            self.command_env
        )

    def process_only_required(self):
        self.custom_args.append('--no-recommends')

    def match_package_installed(self, package_name, zypper_output):
        # this match for the package to be installed in the output
        # of the zypper command is not 100% accurate. There might
        # be false positives due to sub package names starting with
        # the same base package name
        return re.match(
            '.*Installing: ' + package_name + '.*', zypper_output
        )

    def match_package_deleted(self, package_name, zypper_output):
        return re.match(
            '.*Removing: ' + package_name + '.*', zypper_output
        )

    def __install_items(self):
        items = self.package_requests + self.collection_requests \
            + self.product_requests
        self.cleanup_requests()
        return items

    def __delete_items(self):
        # collections and products can't be deleted
        items = []
        items += self.package_requests
        self.cleanup_requests()
        return items
