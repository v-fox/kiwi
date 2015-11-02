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
from command import Command
from filesystem_base import FileSystemBase


class FileSystemBtrfs(FileSystemBase):
    """
        Implements creation of btrfs filesystem
    """
    def create_on_device(self, device):
        Command.run(['mkfs.btrfs'] + self.custom_args + [device])
        Command.run(['mount', device, self.setup_mountpoint()])
