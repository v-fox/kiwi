from nose.tools import *
from mock import patch

import mock

import nose_helper

from collections import namedtuple
from kiwi.system_size import SystemSize


class TestSystemSize(object):
    def setup(self):
        size_type = namedtuple(
            'size_type', ['mbytes', 'additive']
        )
        size = size_type(
            mbytes=42, additive=True
        )
        self.xml_state = mock.Mock()
        self.xml_state.get_build_type_name = mock.Mock(
            return_value='ext4'
        )
        self.xml_state.get_build_type_size = mock.Mock(
            return_value=size
        )
        self.size = SystemSize(mock.Mock(), 'source_dir')

    @patch('kiwi.system_size.Command.run')
    def test_get_size_mbytes_calculated(self, mock_command):
        out_type = namedtuple(
            'out_type', ['output']
        )
        output = out_type(
            output='0'
        )
        mock_command.return_value = output
        self.size.configured_size = None
        result = self.size.get_size_mbytes()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'du', '-s', '--apparent-size', '--block-size', '1', 'source_dir'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'bash', '-c', 'find source_dir | wc -l'
            ])
        assert result == 0

    @patch('kiwi.system_size.Command.run')
    def test_get_size_mbytes_configured_additive(self, mock_command):
        out_type = namedtuple(
            'out_type', ['output']
        )
        output = out_type(
            output='0'
        )
        mock_command.return_value = output
        self.size.configured_size.mbytes = 20
        self.size.configured_size.additive = True
        assert self.size.get_size_mbytes() == 20

    @patch('kiwi.system_size.Command.run')
    @patch('kiwi.logger.log.warning')
    def test_get_size_mbytes_configured(self, mock_log_warn, mock_command):
        out_type = namedtuple(
            'out_type', ['output']
        )
        output = out_type(
            output='3145728'
        )
        mock_command.return_value = output
        self.size.configured_size.mbytes = 3
        self.size.configured_size.additive = False
        assert self.size.get_size_mbytes() == 3
        assert mock_log_warn.called

    @patch('kiwi.system_size.Command.run')
    def test_get_size_mbytes_customized_btrfs(self, mock_command):
        out_type = namedtuple(
            'out_type', ['output']
        )
        output = out_type(
            output='3145728'
        )
        mock_command.return_value = output
        self.size.configured_size = None
        self.size.requested_filesystem = 'btrfs'
        assert self.size.get_size_mbytes() == 4

    @patch('kiwi.system_size.Command.run')
    def test_get_size_mbytes_customized_xfs(self, mock_command):
        out_type = namedtuple(
            'out_type', ['output']
        )
        output = out_type(
            output='3145728'
        )
        mock_command.return_value = output
        self.size.configured_size = None
        self.size.requested_filesystem = 'xfs'
        assert self.size.get_size_mbytes() == 3
