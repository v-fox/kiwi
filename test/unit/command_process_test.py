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
    def setup(self):
        self.command = mock.MagicMock()
        self.process = CommandProcess(self.command)

    def test_poll_show_progress(self):
        # TODO
        pass

    def test_poll(self):
        # TODO
        pass
