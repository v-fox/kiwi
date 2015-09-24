import sys
import mock
from nose.tools import *
from mock import patch

import logging
import nose_helper
import inspect

from kiwi.cli_task import CliTask
from kiwi.exceptions import *

import kiwi.xml_parse


class TestCliTask(object):
    @patch('os.path.isfile')
    @patch('ConfigParser.ConfigParser.has_section')
    @patch('kiwi.logger.log.setLevel')
    def setup(self, mock_setlevel, mock_section, mock_isfile):
        sys.argv = [
            sys.argv[0], '--debug', '--profile', 'foo',
            'system', 'prepare',
            '--description', 'description',
            '--root', 'directory'
        ]
        self.task = CliTask()
        mock_setlevel.assert_called_once_with(logging.DEBUG)

    @raises(SystemExit)
    @patch('kiwi.cli_task.Help.show')
    def test_show_help(self, help_show):
        sys.argv = [
            sys.argv[0], 'help'
        ]
        CliTask()
        help_show.assert_called_once_with('kiwi')

    def test_profile_list(self):
        assert self.task.profile_list() == ['foo']

    def test_quadruple_token(self):
        assert self.task.quadruple_token('a,b') == ['a', 'b', None, None]

    def test_load_xml_description(self):
        self.task.load_xml_description('../data/description')
        assert self.task.config_file == '../data/description/config.xml'
        assert isinstance(self.task.xml, kiwi.xml_parse.image)
        assert self.task.used_profiles == ['foo']
