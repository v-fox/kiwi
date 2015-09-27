from nose.tools import *
from mock import patch

import mock
import re

import nose_helper

from kiwi.package_manager_zypper import PackageManagerZypper

from kiwi.exceptions import (
    KiwiUnknownPackageMatchMode
)


class TestPackageManagerZypper(object):
    def setup(self):
        repository = mock.Mock()
        repository.root_dir = 'root-dir'

        root_bind = mock.Mock()
        root_bind.move_to_root = mock.Mock(
            return_value=['root-moved-arguments']
        )
        repository.root_bind = root_bind

        repository.runtime_config = mock.Mock(
            return_value={
                'zypper_args': ['--reposd-dir', 'root-dir/my/repos'],
                'command_env': ['env']
            }
        )
        self.manager = PackageManagerZypper(repository)

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
    def test_process_install_requests_bootstrap(self, mock_call):
        self.manager.request_package('vim')
        self.manager.process_install_requests_bootstrap()
        mock_call.assert_called_once_with(
            [
                'zypper', '--reposd-dir', 'root-dir/my/repos',
                '--root', 'root-dir',
                'install', '--auto-agree-with-licenses'
            ] + self.manager.custom_args + ['vim'],
            [
                'env'
            ]
        )

    @patch('kiwi.command.Command.call')
    def test_process_install_requests(self, mock_call):
        self.manager.request_package('vim')
        self.manager.process_install_requests()
        chroot_zypper_args = self.manager.root_bind.move_to_root(
            self.manager.zypper_args
        )
        mock_call.assert_called_once_with(
            ['chroot', 'root-dir', 'zypper'] + chroot_zypper_args + [
                'install', '--auto-agree-with-licenses'
            ] + self.manager.custom_args + ['vim'],
            [
                'env'
            ]
        )

    @patch('kiwi.command.Command.call')
    def test_process_delete_requests(self, mock_call):
        self.manager.request_package('vim')
        self.manager.process_delete_requests()
        chroot_zypper_args = self.manager.root_bind.move_to_root(
            self.manager.zypper_args
        )
        mock_call.assert_called_once_with(
            ['chroot', 'root-dir', 'zypper'] + chroot_zypper_args + [
                'remove', '--auto-agree-with-licenses'
            ] + self.manager.custom_args + ['vim'],
            [
                'env'
            ]
        )

    @patch('kiwi.command.Command.call')
    def test_update(self, mock_call):
        self.manager.update()
        chroot_zypper_args = self.manager.root_bind.move_to_root(
            self.manager.zypper_args
        )
        mock_call.assert_called_once_with(
            ['chroot', 'root-dir', 'zypper'] + chroot_zypper_args + [
                'update', '--auto-agree-with-licenses'
            ] + self.manager.custom_args,
            [
                'env'
            ]
        )

    def test_process_only_required(self):
        self.manager.process_only_required()
        assert self.manager.custom_args == ['--no-recommends']

    def test_match_package(self):
        assert self.manager.match_package('foo', 'Installing: foo')
        assert self.manager.match_package('foo', 'Removing: foo', 'deleted')

    @raises(KiwiUnknownPackageMatchMode)
    def test_match_package_raises(self):
        self.manager.match_package(
            'foo', 'Installing: foo', 'wrong-mode'
        )
