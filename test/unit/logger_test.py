from nose.tools import *
from mock import patch
from collections import namedtuple

import nose_helper

from kiwi.logger import *


class TestLoggerSchedulerFilter(object):
    def setup(self):
        self.scheduler_filter = LoggerSchedulerFilter()

    def test_filter(self):
        MyRecord = namedtuple(
            'MyRecord',
            'name'
        )
        ignorables = [
            'apscheduler.scheduler',
            'apscheduler.executors.default'
        ]
        for ignorable in ignorables:
            record = MyRecord(name=ignorable)
            assert self.scheduler_filter.filter(record) == False


class TestInfoFilter(object):
    def setup(self):
        self.info_filter = InfoFilter()

    def test_filter(self):
        MyRecord = namedtuple(
            'MyRecord',
            'levelno'
        )
        record = MyRecord(levelno=0)
        assert self.info_filter.filter(record) == 0


class TestLogger(object):
    @patch('sys.stdout')
    def test_progress(self, mock_stdout):
        log.progress(50, 100, 'foo')
        mock_stdout.write.assert_called_once_with(
            '\rfoo: [####################                    ] 50%'
        )
        mock_stdout.flush.assert_called_once_with()

    def test_progress_raise(self):
        assert log.progress(50, 0, 'foo') == None
