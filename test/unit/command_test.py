from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import KiwiCommandError
from kiwi.command import Command


class TestCommand(object):
    @raises(KiwiCommandError)
    @patch('subprocess.Popen')
    def test_run_raises_error(self, mock_popen):
        mock_process = mock.Mock()
        mock_process.communicate = mock.Mock(
            return_value=['output', 'error']
        )
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        Command.run(['command', 'args'])

    @patch('subprocess.Popen')
    def test_run(self, mock_popen):
        mock_process = mock.Mock()
        mock_process.communicate = mock.Mock(
            return_value=['output', 'error']
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        assert Command.run(['command', 'args']) == 'output'
