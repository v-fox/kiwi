from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.loop_device import LoopDevice


class TestLoopDevice(object):
    @patch('os.path.exists')
    def setup(self, mock_exists):
        mock_exists.return_value = False
        self.loop = LoopDevice('loop-file', 20, 4096)

    @raises(KiwiLoopSetupError)
    def test_loop_setup_invalid(self):
        LoopDevice('loop-file-does-not-exist-and-no-size-given')

    @patch('os.path.exists')
    @patch('kiwi.loop_device.Command.run')
    def test_create(self, mock_command, mock_exists):
        mock_exists.return_value = False
        self.loop.create()
        call = mock_command.call_args_list[0]
        assert mock_command.call_args_list[0] == \
            call([
                'qemu-img', 'create', 'loop-file', '20M'
            ])
        call = mock_command.call_args_list[1]
        assert mock_command.call_args_list[1] == \
            call([
                'losetup', '-f', '--show', 'loop-file'
            ])
        self.loop.node_name = None

    @patch('kiwi.loop_device.Command.run')
    def test_destructor(self, mock_command):
        self.loop.node_name = '/dev/loop0'
        del self.loop
        mock_command.assert_called_once_with(
            ['losetup', '-d', '/dev/loop0']
        )
