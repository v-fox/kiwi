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


class ArchiveCpio(object):
    """
        extraction/creation of cpio archives
    """
    def __init__(self, filename):
        self.filename = filename

    def create(self, source_dir):
        cpio_command = [
            'cd', source_dir, '&&',
            'find', '.', '-path', './boot', '-prune', '-o', '-print', '|',
            'cpio', '--quiet', '-o', '-H', 'newc', '>', self.filename
        ]
        Command.run(
            ['bash', '-c', ' '.join(cpio_command)]
        )

    def extract(self, destination):
        # TODO
        pass
