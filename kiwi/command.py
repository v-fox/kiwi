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
import os
import subprocess

# project
from exceptions import KiwiCommandError


class Command(object):
    """
        Implements command invocation
    """
    @classmethod
    def run(self, command, environment=os.environ):
        from logger import log
        log.debug('EXEC: [%s]', ' '.join(command))
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment
        )
        output, error = process.communicate()
        if process.returncode != 0:
            log.debug('EXEC: Failed with %s', error)
            raise KiwiCommandError(error)
        return {
            'output': output,
            'returncode': process.returncode
        }
