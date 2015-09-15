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
import re

from exceptions import (
    KiwiUriStyleUnknown,
    KiwiUriTypeUnknown
)


class Repository(object):
    """
        Implements base class for package manager repo handling
    """
    def __init__(self, root_bind, custom_args=None):
        self.root_bind = root_bind
        self.root_dir = root_bind.root_dir
        self.shared_location = root_bind.shared_location

        self.remote_uri_types = {
            'http': True,
            'https': True,
            'ftp': True
        }
        self.local_uri_type = {
            'iso': True,
            'dir': True,
            'this': True
        }
        self.post_init(custom_args)

    def post_init(self, custom_args):
        pass

    def add_bootstrap_repo(self, name, uri, repo_type, prio):
        raise NotImplementedError

    def delete_bootstrap_repo(self, name):
        raise NotImplementedError

    def add_repo(self, name, uri, repo_type, prio):
        raise NotImplementedError

    def delete_repo(self, name):
        raise NotImplementedError

    def is_remote(self, uri):
        uri_exp = re.search('^(.*):\/\/(.*)', uri)
        if not uri_exp:
            raise KiwiUriStyleUnknown('URI style %s unknown' % uri)
        uri_type = uri_exp.group(1)
        uri_name = uri_exp.group(2)
        try:
            self.remote_uri_types[uri_type]
            result = {'name': uri, 'remote': True}
        except KeyError:
            try:
                self.local_uri_type[uri_type]
                result = {'name': uri_name, 'remote': False}
            except KeyError:
                raise KiwiUriTypeUnknown('URI type %s unknown' % uri_type)
        return result
