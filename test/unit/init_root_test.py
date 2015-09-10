from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiRootDirExists,
    KiwiInitRootCreationError
)

from kiwi.init_root import InitRoot


class TestInitRoot(object):
    @raises(KiwiRootDirExists)
    @patch('os.path.exists')
    def test_init_raises_error(self, mock_path):
        mock_path.return_value = True
        InitRoot('root_dir')

    @raises(KiwiInitRootCreationError)
    @patch('kiwi.command.Command.run')
    @patch('os.path.exists')
    def test_create_raises_error(self, mock_path, mock_command):
        mock_path.return_value = False
        mock_command.side_effect = KiwiInitRootCreationError('some-error')
        root = InitRoot('root_dir')
        root.create()

    @patch('kiwi.command.Command.run')
    @patch('os.path.exists')
    def test_create(self, mock_path, mock_command):
        mock_path.return_value = False
        root = InitRoot('root_dir')
        mock_path.return_value = True
        root.create()
        assert mock_command.called
