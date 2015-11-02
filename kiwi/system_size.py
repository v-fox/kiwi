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
from defaults import Defaults
from logger import log


class SystemSize(object):
    """
        Provide source tree size information
    """
    def __init__(self, xml_state, source_dir):
        self.xml_state = xml_state
        self.source_dir = source_dir
        self.requested_filesystem = xml_state.get_build_type_name()
        self.configured_size = self.xml_state.get_build_type_size()

    def get_size_mbytes(self):
        source_dir_mbytes = self.__accumulate_mbyte_file_sizes()
        filesystem_mbytes = self.__customize(source_dir_mbytes)

        if not self.configured_size:
            log.info(
                'Using calculated size: %d MB',
                filesystem_mbytes
            )
            return filesystem_mbytes
        elif self.configured_size.additive:
            result_filesystem_mbytes = \
                self.configured_size.mbytes + filesystem_mbytes
            log.info(
                'Using configured size: %d MB plus %d MB calculated = %d MB',
                self.configured_size.mbytes,
                filesystem_mbytes,
                result_filesystem_mbytes
            )
            return result_filesystem_mbytes
        else:
            log.info(
                'Using configured size: %d MB',
                self.configured_size.mbytes
            )
            if self.configured_size.mbytes < filesystem_mbytes:
                log.warning(
                    '--> Configured size smaller than calculated size: %d MB',
                    filesystem_mbytes
                )
            return self.configured_size.mbytes

    def __customize(self, size):
        """
            increase the sum of all file sizes by an empiric factor
        """
        if self.requested_filesystem.startswith('ext'):
            size *= 1.2
            file_count = self.__accumulate_files()
            inode_mbytes = \
                file_count * Defaults.get_default_inode_size() / 1048576
            size += 2 * inode_mbytes
        elif self.requested_filesystem == 'btrfs':
            size *= 1.5
        elif self.requested_filesystem == 'xfs':
            size *= 1.2
        return int(size)

    def __accumulate_mbyte_file_sizes(self):
        du_call = Command.run(
            [
                'du', '-s', '--apparent-size', '--block-size', '1',
                self.source_dir
            ]
        )
        return int(du_call.output.split('\t')[0]) / 1048576

    def __accumulate_files(self):
        bash_comand = [
            'find', self.source_dir, '|', 'wc', '-l'
        ]
        wc_call = Command.run(
            [
                'bash', '-c', ' '.join(bash_comand)
            ]
        )
        return int(wc_call.output.rstrip('\n'))
