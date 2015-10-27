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

    def outavailable(self):
        return self.out_available.pop()

    def erravailable(self):
        return self.err_available.pop()

    def outdata(self):
        return self.data_out.pop()

    def errdata(self):
        return self.data_err.pop()

    def create_flow_method(self, method):
        def create_method():
            return method()
        return create_method

    def setup(self):
        self.data_flow = [True, None]
        self.out_available = [False, True, True]
        self.err_available = [False, True, True]
        self.data_out = ['', 'data']
        self.data_err = ['', 'error']
        self.flow = self.create_flow_method(self.poll)
        self.flow_out_available = self.create_flow_method(self.outavailable)
        self.flow_err_available = self.create_flow_method(self.erravailable)
        self.flow_out = self.create_flow_method(self.outdata)
        self.flow_err = self.create_flow_method(self.errdata)

    @patch('kiwi.command.Command')
    def test_poll_show_progress(self, mock_command):
        match_method = CommandProcess(None).create_match_method(
            self.fake_matcher
        )
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output_available = self.flow_out_available
        process.command.error_available = self.flow_err_available
        process.command.output.readline = self.flow_out
        process.command.error.read = self.flow_err
        process.command.process.returncode = 0
        process.poll_show_progress(['a', 'b'], match_method)
        assert process.items_processed == 2

    @raises(KiwiCommandError)
    @patch('kiwi.command.Command')
    def test_poll_show_progress_raises(self, mock_command):
        match_method = CommandProcess(None).create_match_method(
            self.fake_matcher
        )
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output_available = self.flow_out_available
        process.command.error_available = self.flow_err_available
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 1
        process.poll_show_progress(['a', 'b'], match_method)

    @patch('kiwi.command.Command')
    def test_poll(self, mock_command):
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output_available = self.flow_out_available
        process.command.error_available = self.flow_err_available
        process.command.output.readline = self.flow_out
        process.command.error.read = self.flow_err
        process.command.process.returncode = 0
        process.poll()
        assert process.items_processed == 2

    @patch('kiwi.command.Command')
    def test_poll_and_watch(self, mock_command):
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output_available = self.flow_out_available
        process.command.error_available = self.flow_err_available
        process.command.output.readline = self.flow_out
        process.command.error.read = self.flow_err
        process.command.process.returncode = 0
        result = process.poll_and_watch()
        assert result.returncode == 0

    @raises(KiwiCommandError)
    @patch('kiwi.command.Command')
    def test_poll(self, mock_command):
        process = CommandProcess(mock_command)
        process.command.process.poll = self.flow
        process.command.output_available = self.flow_out_available
        process.command.error_available = self.flow_err_available
        process.command.output.readline = self.flow_out
        process.command.error.read = self.flow_err
        process.command.output.readline.return_value = 'data'
        process.command.process.returncode = 1
        process.poll()

    def test_create_match_method(self):
        match_method = CommandProcess(None).create_match_method(
            self.fake_matcher
        )
        assert match_method('a', 'b') == True
