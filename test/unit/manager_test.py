from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.manager import Manager


class TestManager(object):
    @raises(NotImplementedError)
    def test_package_manager_not_implemented(self):
        Manager.new('repository', 'ms-manager')

    @patch('kiwi.manager.ManagerZypper')
    def test_manager_zypper_new(self, mock_manager):
        repository = mock.Mock()
        Manager.new(repository, 'zypper')
        mock_manager.assert_called_once_with(repository, None)
