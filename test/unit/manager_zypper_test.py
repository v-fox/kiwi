from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.manager_zypper import ManagerZypper


class TestManager(object):
    def setup(self):
        repository = mock.Mock()
        repository.root_dir = 'root-dir'
        repository.runtime_config = mock.Mock(
            return_value={
                'zypper_args': ['--reposd-dir', 'root-dir/my/repos'],
                'command_env': ['env']
            }
        )
        self.manager = ManagerZypper(repository)

    def test_request_package(self):
        self.manager.request_package('name')
        assert self.manager.package_requests == ['name']

    def test_request_collection(self):
        self.manager.request_collection('name')
        assert self.manager.collection_requests == ['pattern:name']

    def test_request_product(self):
        self.manager.request_product('name')
        assert self.manager.product_requests == ['product:name']

    @patch('kiwi.command.Command.call')
    def test_install_requests_bootstrap(self, mock_call):
        self.manager.request_package('vim')
        self.manager.install_requests_bootstrap()
        mock_call.assert_called_once_with(
            [
                'zypper', '--reposd-dir', 'root-dir/my/repos',
                '--root', 'root-dir',
                'install', '--auto-agree-with-licenses', 'vim'
            ],
            [
                'env'
            ]
        )

    @patch('kiwi.command.Command.call')
    def test_install_requests(self, mock_call):
        self.manager.request_package('vim')
        self.manager.install_requests()
        mock_call.assert_called_once_with(
            [
                'chroot', 'root-dir', 'zypper', '--reposd-dir', '//my/repos',
                'install', '--auto-agree-with-licenses', 'vim'
            ],
            [
                'env'
            ]
        )
