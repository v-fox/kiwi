from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiRepoTypeUnknown
)

from kiwi.repository_zypper import RepositoryZypper
from kiwi.root_bind import RootBind
from kiwi.manager import Manager


class TestRepositoryZypper(object):
    @patch('kiwi.command.Command.run')
    def setup(self, mock_command):
        root_bind = mock.Mock()
        root_bind.root_dir = '../data'
        root_bind.shared_location = '/shared-dir'
        self.repo = RepositoryZypper(root_bind)

    @raises(KiwiRepoTypeUnknown)
    @patch('kiwi.command.Command.run')
    def test_add_bootstrap_repo_raises(self, mock_command):
        self.repo.add_bootstrap_repo('foo', 'uri', 'xxx')

    def test_runtime_config(self):
        assert self.repo.runtime_config()['zypper_args'] == \
            self.repo.zypper_args
        assert self.repo.runtime_config()['command_env'] == \
            self.repo.command_env

    @patch('kiwi.command.Command.run')
    def test_add_bootstrap_repo(self, mock_command):
        self.repo.add_bootstrap_repo('foo', 'uri', 'rpm-md', 42)
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == call(
            ['zypper'] + self.repo.zypper_args + [
                '--root', '../data',
                'addrepo', '-f',
                '--type', 'YUM',
                '--keep-packages',
                'uri',
                'foo'
            ], self.repo.command_env
        )
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == call(
            ['zypper'] + self.repo.zypper_args + [
                '--root', '../data',
                'modifyrepo', '-p', '42', 'foo'
            ], self.repo.command_env
        )

    @patch('kiwi.command.Command.run')
    def test_delete_bootstrap_repo(self, mock_command):
        self.repo.delete_bootstrap_repo('foo')
        mock_command.assert_called_once_with(
            ['zypper'] + self.repo.zypper_args + [
                '--root', '../data', 'removerepo', 'foo'
            ], self.repo.command_env
        )

    @patch('kiwi.command.Command.run')
    def test_add_repo(self, mock_command):
        self.repo.add_repo('foo', 'uri', 'rpm-md', 42)
        chroot_zypper_args = Manager.move_to_root(
            '../data', self.repo.zypper_args
        )
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == call(
            ['chroot', '../data', 'zypper'] + chroot_zypper_args + [
                'addrepo', '-f',
                '--type', 'YUM',
                '--keep-packages',
                'uri',
                'foo'
            ], self.repo.command_env
        )
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == call(
            ['chroot', '../data', 'zypper'] + chroot_zypper_args + [
                'modifyrepo', '-p', '42', 'foo'
            ], self.repo.command_env
        )

    @patch('kiwi.command.Command.run')
    def test_delete_repo(self, mock_command):
        self.repo.delete_repo('foo')
        chroot_zypper_args = Manager.move_to_root(
            '../data', self.repo.zypper_args
        )
        mock_command.assert_called_once_with(
            ['chroot', '../data', 'zypper'] + chroot_zypper_args + [
                'removerepo', 'foo'
            ], self.repo.command_env
        )

    @patch('kiwi.command.Command.run')
    def test_delete_all_repos(self, mock_command):
        self.repo.delete_all_repos()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'rm', '-r', '-f', '../data/shared-dir/zypper/repos'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'mkdir', '../data/shared-dir/zypper/repos'
            ])
