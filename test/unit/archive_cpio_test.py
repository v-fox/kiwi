from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.archive_cpio import ArchiveCpio


class TestArchiveCpio(object):
    def setup(self):
        self.archive = ArchiveCpio('foo.cpio')

    @patch('kiwi.archive_cpio.Command.run')
    def test_create(self, mock_command):
        self.archive.create('source-dir', ['/boot', '/var/cache'])
        find_command = \
            'find . -path ./boot -prune -or -path ./var/cache -prune -o -print'
        cpio_command = 'cpio --quiet -o -H newc'
        mock_command.assert_called_once_with(
            [
                'bash', '-c', 'cd source-dir && ' +
                find_command + ' | ' + cpio_command + ' > foo.cpio'
            ]
        )

    def test_extract(self):
        # TODO
        self.archive.extract('destination')
