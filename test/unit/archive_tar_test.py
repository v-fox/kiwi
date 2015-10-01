from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.archive_tar import ArchiveTar


class TestArchiveTar(object):
    def setup(self):
        self.archive = ArchiveTar('foo.tgz')

    @patch('kiwi.archive_tar.Command.run')
    def test_extract(self, mock_command):
        self.archive.extract('destination')
        mock_command.assert_called_once_with(
            ['tar', 'C', 'destination', '-x', '-v', '-f', 'foo.tgz']
        )
