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
from repository_zypper import RepositoryZypper


class Repository(object):
    """
        Repository factory
    """
    @classmethod
    def new(self, root_bind, package_manager, custom_args=[]):
        if package_manager == 'zypper':
            return RepositoryZypper(root_bind, custom_args)
        else:
            raise NotImplementedError(
                'Support for %s repository manager not implemented' %
                package_manager
            )
