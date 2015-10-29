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

    def create(self, source_dir, exclude=None):
        find_excludes = []
        find_command = ['cd', source_dir, '&&', 'find', '.']
        cpio_command = [
            'cpio', '--quiet', '-o', '-H', 'newc', '>', self.filename
        ]
        if exclude:
            for path in exclude:
                if find_excludes:
                    find_excludes.append('-or')
                find_excludes.append('-path')
                find_excludes.append('.' + path)
                find_excludes.append('-prune')
            find_excludes.append('-o')
            find_excludes.append('-print')
            find_command += find_excludes

        bash_command = find_command + ['|'] + cpio_command
        Command.run(
            ['bash', '-c', ' '.join(bash_command)]
        )

    def extract(self, dest_dir):
        bash_command = [
            'cd', dest_dir, '&&',
            'cat', self.filename, '|',
            'cpio', '-i', '--make-directories'
        ]
        Command.run(
            ['bash', '-c', ' '.join(bash_command)]
        )
