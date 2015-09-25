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
from manager_base import ManagerBase
from command import Command


class ManagerZypper(ManagerBase):
    """
        Implements install tasks for the zypper package manager
    """
    def post_init(self, custom_args):
        self.init_args = custom_args
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
            ] + self.__install_items(),
            self.command_env
        )

    def process_install_requests(self):
        chroot_zypper_args = ManagerBase.move_to_root(
            self.root_dir, self.zypper_args
        )
        return Command.call(
            ['chroot', self.root_dir, 'zypper'] + chroot_zypper_args + [
                'install', '--auto-agree-with-licenses'
            ] + self.__install_items(),
            self.command_env
        )

    def process_delete_requests(self):
        chroot_zypper_args = ManagerBase.move_to_root(
            self.root_dir, self.zypper_args
        )
        return Command.call(
            ['chroot', self.root_dir, 'zypper'] + chroot_zypper_args + [
                'remove', '--auto-agree-with-licenses'
            ] + self.__delete_items(),
            self.command_env
        )

    def update(self):
        chroot_zypper_args = ManagerBase.move_to_root(
            self.root_dir, self.zypper_args
        )
        return Command.call(
            ['chroot', self.root_dir, 'zypper'] + chroot_zypper_args + [
                'update', '--auto-agree-with-licenses'
            ],
            self.command_env
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
