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


class Defaults(object):
    """
        Default values and export methods
    """
    def __init__(self):
        self.defaults = {
            'kiwi_align': 1048576,
            'kiwi_startsector': 2048,
            'kiwi_sectorsize': 512,
            'kiwi_freespace': 20,
            'kiwi_inode_size': 256,
            'kiwi_inode_ratio': 16384,
            'kiwi_min_inodes': 20000,
            'kiwi_revision': self.__kiwi_revision()
        }
        self.profile_key_list = [
            'kiwi_align',
            'kiwi_startsector',
            'kiwi_sectorsize',
            'kiwi_revision'
        ]

    @classmethod
    def get_image_description_path(self):
        return '/usr/share/kiwi/image'

    @classmethod
    def get_boot_image_strip_file(self):
        return 'config/strip.xml'

    @classmethod
    def get_schema_file(self):
        return 'schema/KIWISchema.rng'

    @classmethod
    def get_common_functions_file(self):
        return 'config/functions.sh'

    @classmethod
    def get_xsl_stylesheet_file(self):
        return 'xsl/master.xsl'

    def get(self, key):
        if key in self.defaults:
            return self.defaults[key]

    def to_profile(self, profile):
        for key in sorted(self.profile_key_list):
            profile.add(key, self.get(key))

    def __kiwi_revision(self):
        with open('schema/kiwi_revision') as revision:
            return revision.read().splitlines().pop()
