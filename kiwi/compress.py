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
from tempfile import NamedTemporaryFile


class Compress(object):
    """
        File compression / decompression
    """
    def __init__(self, source_filename):
        self.source_filename = source_filename
        self.compressed_filename = None
        self.uncompressed_filename = None

    def xz(self):
        Command.run(['xz', self.source_filename])
        self.compressed_filename = self.source_filename + '.xz'

    def un_xz(self, temporary=False):
        if not temporary:
            Command.run(['xz', '-d', self.source_filename])
            self.uncompressed_filename = self.source_filename
        else:
            temp_file = NamedTemporaryFile()
            bash_command = [
                'xz', '-c', '-d', self.source_filename, '>', temp_file.name
            ]
            Command.run(['bash', '-c', ' '.join(bash_command)])
            self.uncompressed_filename = temp_file.name

    def un_gzip(self, temporary=False):
        if not temporary:
            Command.run(['gzip', '-d', self.source_filename])
            self.uncompressed_filename = self.source_filename
        else:
            temp_file = NamedTemporaryFile()
            bash_command = [
                'gzip', '-c', '-d', self.source_filename, '>', temp_file.name
            ]
            Command.run(['bash', '-c', ' '.join(bash_command)])
            self.uncompressed_filename = temp_file.name

    def gzip(self):
        Command.run(['gzip', '-9', self.source_filename])
        self.compressed_filename = self.source_filename + '.gz'
