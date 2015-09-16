from nose.tools import *
from mock import patch
from collections import namedtuple

import mock

import nose_helper

from kiwi.exceptions import KiwiCommandError
from kiwi.command import Command


class TestCommand(object):
    def __init__(self):
        command_call = namedtuple(
            'command', ['output', 'process']
        )
        self.call_result = command_call(
            output='stdout_stderr',
            process=mock.Mock()
        )

    @raises(KiwiCommandError)
    @patch('subprocess.Popen')
    def test_run_raises_error(self, mock_popen):
        mock_process = mock.Mock()
        mock_process.communicate = mock.Mock(
            return_value=['stdout', 'stderr']
        )
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        Command.run(['command', 'args'])

    @patch('subprocess.Popen')
    def test_run(self, mock_popen):
        command_run = namedtuple(
            'command', ['output', 'error', 'returncode']
        )
        run_result = command_run(
            output='stdout',
            error='stderr',
            returncode=0
        )
        mock_process = mock.Mock()
        mock_process.communicate = mock.Mock(
            return_value=['stdout', 'stderr']
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        assert Command.run(['command', 'args']) == run_result

    @patch('subprocess.Popen')
    @patch('io.open')
    def test_call(self, mock_io_open, mock_popen):
        mock_process = mock.Mock()
        mock_io = mock.Mock()
        mock_io_open.return_value = mock_io
        mock_popen.return_value = mock_process
        command_call = namedtuple(
            'command', ['output', 'process']
        )
        call_result = command_call(
            output=mock_io,
            process=mock_process
        )
        assert Command.call(['command', 'args']) == call_result
