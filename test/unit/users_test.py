from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.users import Users


class TestUsers(object):
    def setup(self):
        self.users = Users('root_dir')

    @patch('kiwi.users.Command.run')
    def test_user_exists(self, mock_command):
        self.users.user_exists('user')
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'grep', '-q', '^user:', '/etc/passwd']
        )

    @patch('kiwi.users.Command.run')
    def test_user_exists_return_value(self, mock_command):
        assert self.users.user_exists('user') == True
        mock_command.side_effect = Exception
        assert self.users.user_exists('user') == False

    @patch('kiwi.users.Command.run')
    def test_group_exists(self, mock_command):
        self.users.group_exists('group')
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'grep', '-q', '^group:', '/etc/group']
        )

    @patch('kiwi.users.Command.run')
    def test_group_add(self, mock_command):
        self.users.group_add('group', ['--option', 'value'])
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'addgroup', '--option', 'value', 'group']
        )

    @patch('kiwi.users.Command.run')
    def test_user_add(self, mock_command):
        self.users.user_add('user', ['--option', 'value'])
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'useradd', '--option', 'value', 'user']
        )

    @patch('kiwi.users.Command.run')
    def test_user_modify(self, mock_command):
        self.users.user_modify('user', ['--option', 'value'])
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'usermod', '--option', 'value', 'user']
        )

    @patch('kiwi.users.Command.run')
    def test_setup_home_for_user(self, mock_command):
        self.users.setup_home_for_user('user', 'group', '/home/path')
        mock_command.assert_called_once_with(
            ['chroot', 'root_dir', 'chown', '-R', 'user:group', '/home/path']
        )
