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
from tempfile import mkdtemp
from shutil import rmtree
import os

# project
from command import Command

from exceptions import (
    KiwiRootDirExists,
    KiwiInitRootCreationError
)


class InitRoot(object):
    """
        Implements creation of new root directory for a linux system.
        Host system independent static default files and device nodes
        are created to initialize a new base system
    """
    def __init__(self, root_dir):
        if os.path.exists(root_dir):
            raise KiwiRootDirExists(
                'Root directory %s already exists' % root_dir
            )
        self.root_dir = root_dir

    def delete(self):
        Command.run(['rm', '-r', '-f', self.root_dir])

    def create(self):
        root = mkdtemp()
        try:
            Command.run(['mkdir', '-p', root])
            Command.run(['mkdir', '-p', root + '/dev/pts'])
            Command.run(['mkdir', '-p', root + '/proc'])
            Command.run(['mkdir', '-p', root + '/etc/sysconfig'])
            Command.run(['mkdir', '-p', root + '/var'])
            Command.run(['mkdir', '-p', root + '/run'])

            Command.run(['cp', 'config/functions.sh', root + '/.kconfig'])

            Command.run(['chown', 'root:root', root + '/dev'])
            Command.run(['chown', 'root:root', root + '/proc'])
            Command.run(['chown', 'root:root', root + '/var'])
            Command.run(['chown', 'root:root', root + '/run'])

            Command.run(
                ['mknod', '-m', '666', root + '/dev/null', 'c', '1', '3']
            )
            Command.run(
                ['mknod', '-m', '666', root + '/dev/zero', 'c', '1', '5']
            )
            Command.run(
                ['mknod', '-m', '622', root + '/dev/full', 'c', '1', '7']
            )
            Command.run(
                ['mknod', '-m', '666', root + '/dev/random', 'c', '1', '8']
            )
            Command.run(
                ['mknod', '-m', '644', root + '/dev/urandom', 'c', '1', '9']
            )
            Command.run(
                ['mknod', '-m', '666', root + '/dev/tty', 'c', '5', '0']
            )
            Command.run(
                ['mknod', '-m', '666', root + '/dev/ptmx', 'c', '5', '2']
            )
            Command.run(
                ['mknod', '-m', '640', root + '/dev/loop0', 'b', '7', '0']
            )
            Command.run(
                ['mknod', '-m', '640', root + '/dev/loop1', 'b', '7', '1']
            )
            Command.run(
                ['mknod', '-m', '640', root + '/dev/loop2', 'b', '7', '2']
            )
            Command.run(
                ['mknod', '-m', '666', root + '/dev/loop3', 'b', '7', '3']
            )
            Command.run(
                ['mknod', '-m', '666', root + '/dev/loop4', 'b', '7', '4']
            )

            Command.run(['ln', '-s', '/proc/self/fd', root + '/dev/fd'])
            Command.run(['ln', '-s', 'fd/2', root + '/dev/stderr'])
            Command.run(['ln', '-s', 'fd/0', root + '/dev/stdin'])
            Command.run(['ln', '-s', 'fd/1', root + '/dev/stdout'])
            Command.run(['ln', '-s', '/run', root + '/var/run'])

            self._provide_passwd_group(root)

        except Exception as e:
            rmtree(root, ignore_errors=True)
            raise KiwiInitRootCreationError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        Command.run(['mv', root, self.root_dir])

    def _provide_passwd_group(self, root):
        group_template = '/var/adm/fillup-templates/group.aaa_base'
        passwd_template = '/var/adm/fillup-templates/passwd.aaa_base'
        if os.path.exists(group_template):
            Command.run(['cp', group_template, root + '/etc/group'])
        if os.path.exists(passwd_template):
            Command.run(['cp', passwd_template, root + '/etc/passwd'])
