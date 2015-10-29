from nose.tools import *
from mock import patch

import mock

import nose_helper

from collections import namedtuple

from kiwi.exceptions import *
from kiwi.kernel import Kernel


class TestKernel(object):
    def setup(self):
        self.kernel = Kernel('root-dir')

    @patch('os.path.exists')
    @patch('kiwi.command.Command.run')
    def test_get_kernel(self, mock_run, mock_os):
        run = namedtuple(
            'run', ['output']
        )
        result = run(output='42')
        mock_os.return_value = True
        mock_run.return_value = result
        data = self.kernel.get_kernel()
        mock_run.assert_called_once_with(
            ['kversion', 'root-dir/boot/vmlinux']
        )
        assert data.filename == 'root-dir/boot/vmlinux'
        assert data.version == '42'

    @patch('os.path.exists')
    @patch('kiwi.command.Command.run')
    def test_get_kernel_no_version(self, mock_run, mock_os):
        run = namedtuple(
            'run', ['output']
        )
        result = run(output=None)
        mock_os.return_value = True
        mock_run.return_value = result
        data = self.kernel.get_kernel()
        mock_run.assert_called_once_with(
            ['kversion', 'root-dir/boot/vmlinux']
        )
        assert data.filename == 'root-dir/boot/vmlinux'
        assert data.version == 'no-version-found'

    @patch('os.path.exists')
    def test_get_xen_hypervisor(self, mock_os):
        mock_os.return_value = True
        data = self.kernel.get_xen_hypervisor()
        assert data.filename == 'root-dir/boot/xen.gz'
        assert data.name == 'xen.gz'

    @patch('kiwi.kernel.Kernel.get_kernel')
    @patch('kiwi.command.Command.run')
    def test_extract_kernel(self, mock_run, mock_get_kernel):
        result = mock.MagicMock()
        result.version = '42'
        result.filename = 'kernel'
        mock_get_kernel.return_value = result
        self.kernel.extract_kernel('target-dir')
        mock_run.assert_called_once_with(
            ['mv', 'kernel', 'target-dir/kernel-42']
        )
        self.kernel.extracted['kernel'] == 'target-dir/kernel-42'

    @patch('kiwi.kernel.Kernel.get_xen_hypervisor')
    @patch('kiwi.command.Command.run')
    def test_extract_xen_hypervisor(self, mock_run, mock_get_xen):
        result = mock.MagicMock()
        result.name = 'xen.gz'
        result.filename = 'some/xen.gz'
        mock_get_xen.return_value = result
        self.kernel.extract_xen_hypervisor('target-dir')
        mock_run.assert_called_once_with(
            ['mv', 'some/xen.gz', 'target-dir/hypervisor-xen.gz']
        )
        self.kernel.extracted['xen_hypervisor'] == \
            'target-dir/hypervisor-xen.gz'
