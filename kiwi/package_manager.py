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
from package_manager_zypper import PackageManagerZypper


class PackageManager(object):
    """
        package manager factory
    """
    @classmethod
    def new(self, repository, package_manager, custom_args=None):
        from logger import log

        if package_manager == 'zypper':
            manager = PackageManagerZypper(repository, custom_args)
        else:
            raise NotImplementedError(
                'Support for package manager %s not implemented' %
                package_manager
            )

        log.info(
            'Using package manager backend: %s', package_manager
        )
        return manager
