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
from tempfile import mkdtemp

# project
from command import Command

from exceptions import (
    KiwiUriStyleUnknown,
    KiwiUriTypeUnknown
)


class Uri(object):
    """
        normalize url types available in a kiwi configuration into
        standard mime types.
    """
    def __init__(self, uri, repo_type):
        self.repo_type = repo_type
        self.uri = uri
        self.mount_stack = []

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

    def translate(self):
        expression = re.search('obs:\/\/(.*)', self.uri)
        if expression and self.repo_type == 'yast2':
            return self.__obs_distribution(expression.group(1))

        if expression:
            return self.__obs_project(expression.group(1))

        expression = re.search('dir:\/\/(.*)', self.uri)
        if expression:
            return self.__local_directory(expression.group(1))

        expression = re.search('iso:\/\/(.*)', self.uri)
        if expression:
            return self.__iso_mount_path(expression.group(1))

        raise KiwiUriStyleUnknown(
            'URI style %s unknown' % self.uri
        )

    def alias(self):
        return re.escape(self.uri.replace('/', '_'))

    def is_remote(self):
        uri_exp = re.search('^(.*):\/\/(.*)', self.uri)
        if not uri_exp:
            raise KiwiUriStyleUnknown('URI style %s unknown' % self.uri)
        uri_type = uri_exp.group(1)
        uri_name = uri_exp.group(2)
        try:
            self.remote_uri_types[uri_type]
            return True
        except KeyError:
            try:
                self.local_uri_type[uri_type]
                return False
            except KeyError:
                raise KiwiUriTypeUnknown('URI type %s unknown' % uri_type)

    def __iso_mount_path(self, path):
        iso_path = mkdtemp()
        Command.run(['mount', path, iso_path])
        self.mount_stack.append(iso_path)
        return iso_path

    def __local_directory(self, path):
        return path

    def __obs_project(self, name):
        obs_project = 'http://download.opensuse.org/repositories/'
        return obs_project + name

    def __obs_distribution(self, name):
        obs_distribution = 'http://download.opensuse.org/distribution/'
        return obs_distribution + name

    def __del__(self):
        try:
            for mount in reversed(self.mount_stack):
                Command.run(['umount', mount])
                Command.run(['rmdir', mount])
        except Exception as e:
            pass
