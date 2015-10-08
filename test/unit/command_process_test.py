from nose.tools import *
from mock import patch
from collections import namedtuple

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiCommandError
)
from kiwi.command_process import CommandProcess


class TestCommandProcess(object):
    def fake_matcher(self, item, output):
        return True

    def poll(self):
        return self.data_flow.pop()

    def create_flow_method(self, method):
        def create_method():
            return method()
        return create_method

    def setup(self):
        self.data_flow = [True, None]
        self.flow = self.create_flow_method(self.poll)

    @patch('kiwi.command.Command')
    def test_poll_show_progress(self, mock_command):
        match_method = CommandProcess(None).create_match_method(
            self.fake_matcher
        )
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 0
        process.poll_show_progress(['a', 'b'], match_method)
        process.command.output.readline.assert_called_once_with()
        assert process.items_processed == 2

    @raises(KiwiCommandError)
    @patch('kiwi.command.Command')
    def test_poll_show_progress_raises(self, mock_command):
        match_method = CommandProcess(None).create_match_method(
            self.fake_matcher
        )
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 1
        process.poll_show_progress(['a', 'b'], match_method)

    @patch('kiwi.command.Command')
    def test_poll(self, mock_command):
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 0
        process.poll()
        process.command.output.readline.assert_called_once_with()

    @patch('kiwi.command.Command')
    def test_poll_and_watch(self, mock_command):
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 0
        result = process.poll_and_watch()
        process.command.output.readline.assert_called_once_with()
        assert result.returncode == 0

    @raises(KiwiCommandError)
    @patch('kiwi.command.Command')
    def test_poll(self, mock_command):
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 1
        process.poll()

    def test_create_match_method(self):
        match_method = CommandProcess(None).create_match_method(
            self.fake_matcher
        )
        assert match_method('a', 'b') == True
