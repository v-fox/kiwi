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
import io
from collections import namedtuple

# project
from exceptions import KiwiCommandError


class Command(object):
    """
        Implements command invocation
    """
    @classmethod
    def run(self, command, environment=os.environ):
        """
            Execute a program and block the caller. The return value
            is a hash containing the stdout, stderr and return code
            information
        """
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
        command = namedtuple(
            'command', ['output', 'error', 'returncode']
        )
        return command(
            output=output,
            error=error,
            returncode=process.returncode
        )

    @classmethod
    def call(self, command, environment=os.environ):
        """
            Execute a program and return a file handle back to the caller.
            stdout and stderr are both send to the file handle. The caller
            must read from the file handle in order to actually
            run the command. This can be done as follows:

            cmd = Command.call(...)

            while cmd.process.poll() is None:
                line = cmd.output.readline()
                if line:
                    print line

            print cmd.process.returncode
        """
        from logger import log
        log.debug('EXEC: [%s]', ' '.join(command))
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=environment
        )
        output = io.open(
            process.stdout.fileno(), 'rb', closefd=False
        )
        command = namedtuple(
            'command', ['output', 'process']
        )
        return command(
            output=output,
            process=process
        )
