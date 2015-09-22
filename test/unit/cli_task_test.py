import sys
import mock
from nose.tools import *
from mock import patch

import logging
import nose_helper

from kiwi.cli_task import CliTask
from kiwi.exceptions import *


class TestCliTask(object):
    @raises(SystemExit)
    @patch('kiwi.cli_task.Help.show')
    def test_show_help(self, help_show):
        sys.argv = [
            sys.argv[0], 'help'
        ]
        CliTask()
        help_show.assert_called_once_with('kiwi')

    @patch('os.path.isfile')
    @patch('ConfigParser.ConfigParser.has_section')
    @patch('kiwi.logger.log.setLevel')
    def test_global_args(self, mock_setlevel, mock_section, mock_isfile):
        sys.argv = [
            sys.argv[0], '--debug',
            'image', 'prepare',
            '--description', 'description',
            '--root', 'directory'
        ]
        task = CliTask()
        mock_setlevel.assert_called_once_with(logging.DEBUG)
