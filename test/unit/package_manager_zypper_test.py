from nose.tools import *
from mock import patch

import mock
import re

import nose_helper

from kiwi.package_manager_zypper import PackageManagerZypper
from kiwi.exceptions import *


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
    @patch('kiwi.command.Command.run')
    def test_process_delete_requests_all_installed(self, mock_run, mock_call):
        self.manager.request_package('vim')
        self.manager.process_delete_requests()
        chroot_zypper_args = self.manager.root_bind.move_to_root(
            self.manager.zypper_args
        )
        mock_call.assert_called_once_with(
            ['chroot', 'root-dir', 'zypper'] + chroot_zypper_args + [
                'remove', '-u', '--force-resolution'
            ] + self.manager.custom_args + ['vim'],
            [
                'env'
            ]
        )

    @patch('kiwi.command.Command.call')
    @patch('kiwi.command.Command.run')
    def test_process_delete_requests_force(self, mock_run, mock_call):
        self.manager.request_package('vim')
        self.manager.process_delete_requests(True)
        mock_call.assert_called_once_with(
            [
                'chroot', 'root-dir', 'rpm', '-e',
                '--nodeps', '--allmatches', '--noscripts', 'vim'
            ],
            [
                'env'
            ]
        )

    @patch('kiwi.command.Command.run')
    def test_process_delete_requests_all_missing(self, mock_run):
        mock_run.side_effect = Exception
        self.manager.request_package('vim')
        self.manager.process_delete_requests()
        mock_run.assert_called_once_with(
            ['chroot', 'root-dir', 'rpm', '-q', 'vim']
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

    def test_match_package_installed(self):
        assert self.manager.match_package_installed('foo', 'Installing: foo')

    def test_match_package_deleted(self):
        assert self.manager.match_package_deleted('foo', 'Removing: foo')

    @patch('kiwi.command.Command.run')
    def test_database_consistent(self, mock_command):
        assert self.manager.database_consistent() == True

    @patch('kiwi.command.Command.run')
    def test_database_not_consistent(self, mock_command):
        mock_command.side_effect = Exception
        assert self.manager.database_consistent() == False

    @patch('kiwi.command.Command.run')
    @patch('kiwi.package_manager_zypper.PackageManagerZypper.database_consistent')
    def test_reload_package_database(self, mock_consistent, mock_command):
        mock_consistent.return_value = False
        self.manager.dump_reload_package_database()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'db_dump', '-f', 'root-dir/var/lib/rpm/Name.bak',
                'root-dir/var/lib/rpm/Name'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'rm', '-f', 'root-dir/var/lib/rpm/Name'
            ])
        call = mock_command.call_args_list[2]
        assert mock_command.call_args_list[2] == \
            call([
                'db45_load', '-f', 'root-dir/var/lib/rpm/Name.bak',
                'root-dir/var/lib/rpm/Name'
            ])
        call = mock_command.call_args_list[3]
        assert mock_command.call_args_list[3] == \
            call([
                'rm', '-f', 'root-dir/var/lib/rpm/Name.bak'
            ])
        call = mock_command.call_args_list[4]
        assert mock_command.call_args_list[4] == \
            call([
                'db_dump', '-f', 'root-dir/var/lib/rpm/Packages.bak',
                'root-dir/var/lib/rpm/Packages'
            ])
        call = mock_command.call_args_list[5]
        assert mock_command.call_args_list[5] == \
            call([
                'rm', '-f', 'root-dir/var/lib/rpm/Packages'
            ])
        call = mock_command.call_args_list[6]
        assert mock_command.call_args_list[6] == \
            call([
                'db45_load', '-f', 'root-dir/var/lib/rpm/Packages.bak',
                'root-dir/var/lib/rpm/Packages'
            ])
        call = mock_command.call_args_list[7]
        assert mock_command.call_args_list[7] == \
            call([
                'rm', '-f', 'root-dir/var/lib/rpm/Packages.bak'
            ])
        call = mock_command.call_args_list[8]
        assert mock_command.call_args_list[8] == \
            call([
                'chroot', 'root-dir', 'rpm', '--rebuilddb'
            ])

    @raises(KiwiRpmDatabaseReloadError)
    def test_reload_package_database_wrong_db_version(self):
        self.manager.dump_reload_package_database(42)
