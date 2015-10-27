import sys
import mock
from nose.tools import *
from mock import patch

import kiwi

import nose_helper

from kiwi.internal_boot_image_task import BootImageTask
from kiwi.xml_description import XMLDescription
from kiwi.xml_state import XMLState
from kiwi.exceptions import *


class TestBootImageTask(object):
    @patch('os.mkdir')
    def setup(self, mock_mkdir):
        description = XMLDescription('../data/example_config.xml')
        xml_data = description.load()

        self.manager = mock.Mock()
        self.system = mock.Mock()
        self.profile = mock.Mock()
        self.defaults = mock.Mock()
        self.system.setup_repositories = mock.Mock(
            return_value=self.manager
        )
        kiwi.internal_boot_image_task.System = mock.Mock(
            return_value=self.system
        )
        kiwi.internal_boot_image_task.SystemSetup = mock.Mock(
            return_value=mock.Mock()
        )
        kiwi.internal_boot_image_task.Profile = mock.Mock(
            return_value=self.profile
        )

        self.task = BootImageTask(
            XMLState(xml_data), 'some-target-dir'
        )
        self.task.boot_root_directory = 'boot-directory' 
        self.task.boot_target_dir = 'boot-target-directory'

    @patch('kiwi.defaults.Defaults.get_image_description_path')
    def test_prepare(self, mock_boot_path):
        mock_boot_path.return_value = '../data'
        self.task.prepare()
        self.task.system.setup_repositories.assert_called_once_with()
        self.task.system.install_bootstrap.assert_called_once_with(
            self.manager
        )
        self.task.system.install_system.assert_called_once_with(
            self.manager
        )
        self.task.setup.import_shell_environment.assert_called_once_with(
            self.profile
        )
        self.task.setup.import_description.assert_called_once_with()
        self.task.setup.import_overlay_files.assert_called_once_with(
            follow_links=True
        )
        self.task.setup.call_config_script.assert_called_once_with()
        self.task.system.pinch_system.assert_called_once_with(
            manager=self.manager, force=True
        )
        self.task.setup.call_image_script.assert_called_once_with()

    @raises(KiwiConfigFileNotFound)
    @patch('os.path.exists')
    def test_prepare_no_boot_description_found(self, mock_os_path):
        mock_os_path.return_value = False
        self.task.prepare()

    def test_required(self):
        assert self.task.required()

    @patch('kiwi.internal_boot_image_task.Kernel')
    def test_extract_kernel_files(self, mock_kernel):
        kernel = mock.Mock()
        kernel.get_kernel = mock.Mock(
            return_value=True
        )
        kernel.get_xen_hypervisor = mock.Mock(
            return_value=True
        )
        mock_kernel.return_value = kernel
        self.task.extract_kernel_files()
        mock_kernel.assert_called_once_with(self.task.boot_root_directory)
        kernel.get_kernel.assert_called_once_with()
        kernel.extract_kernel.assert_called_once_with(
            self.task.boot_target_dir
        )
        kernel.get_xen_hypervisor.assert_called_once_with()
        kernel.extract_xen_hypervisor.assert_called_once_with(
            self.task.boot_target_dir
        )

    def test_create_initrd(self):
        # TODO
        self.task.create_initrd()
