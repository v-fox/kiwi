from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.compress import Compress


class TestCompress(object):
    def setup(self):
        self.compress = Compress('some-file')

    @patch('kiwi.command.Command.run')
    def test_xz(self, mock_command):
        self.compress.xz()
        mock_command.assert_called_once_with(
            ['xz', 'some-file']
        )
        assert self.compress.compressed_filename == 'some-file.xz'

    @patch('kiwi.command.Command.run')
    def test_gzip(self, mock_command):
        self.compress.gzip()
        mock_command.assert_called_once_with(
            ['gzip', '-9', 'some-file']
        )
        assert self.compress.compressed_filename == 'some-file.gz'

    @patch('kiwi.command.Command.run')
    def test_unxz(self, mock_command):
        self.compress.un_xz()
        mock_command.assert_called_once_with(
            ['xz', '-d', 'some-file']
        )
        assert self.compress.uncompressed_filename == 'some-file'

    @patch('kiwi.command.Command.run')
    @patch('kiwi.compress.NamedTemporaryFile')
    def test_unxz_temporary(self, mock_temp, mock_command):
        tempfile = mock.Mock()
        tempfile.name = 'tempfile'
        mock_temp.return_value = tempfile
        self.compress.un_xz(temporary=True)
        mock_command.assert_called_once_with(
            ['bash', '-c', 'xz -c -d some-file > tempfile']
        )
        assert self.compress.uncompressed_filename == 'tempfile'

    @patch('kiwi.command.Command.run')
    def test_ungzip(self, mock_command):
        self.compress.un_gzip()
        mock_command.assert_called_once_with(
            ['gzip', '-d', 'some-file']
        )
        assert self.compress.uncompressed_filename == 'some-file'

    @patch('kiwi.command.Command.run')
    @patch('kiwi.compress.NamedTemporaryFile')
    def test_ungzip_temporary(self, mock_temp, mock_command):
        tempfile = mock.Mock()
        tempfile.name = 'tempfile'
        mock_temp.return_value = tempfile
        self.compress.un_gzip(temporary=True)
        mock_command.assert_called_once_with(
            ['bash', '-c', 'gzip -c -d some-file > tempfile']
        )
        assert self.compress.uncompressed_filename == 'tempfile'
