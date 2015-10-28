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
    @patch('os.path.exists')
    def setup(self, mock_os_path, mock_mkdir):
        mock_os_path.return_value = True
        description = XMLDescription('../data/example_config.xml')
        self.xml_state = XMLState(
            description.load()
        )

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
            self.xml_state, 'some-target-dir'
        )
        self.task.boot_root_directory = 'boot-directory'
        self.task.boot_target_directory = 'boot-target-directory'

    @raises(KiwiTargetDirectoryNotFound)
    def test_boot_image_task_raises(self):
        BootImageTask(None, 'target-dir-does-not-exist')

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

    def test_required_true(self):
        assert self.task.required()

    @patch('kiwi.internal_boot_image_task.Command.run')
    def test_required_false(self, mock_run):
        self.xml_state.build_type.set_boot(None)
        assert self.task.required() == False
        mock_run.assert_called_once_with(
            ['rm', '-r', '-f', 'boot-directory', 'boot-target-directory']
        )

    @patch('kiwi.internal_boot_image_task.Kernel')
    def test_extract_kernel_files(self, mock_kernel):
        kernel = mock.Mock()
        kernel.get_extracted = mock.Mock(
            return_value={}
        )
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
            self.task.boot_target_directory
        )
        kernel.get_xen_hypervisor.assert_called_once_with()
        kernel.extract_xen_hypervisor.assert_called_once_with(
            self.task.boot_target_directory
        )

    @patch('kiwi.internal_boot_image_task.ArchiveCpio')
    def test_create_initrd(self, mock_cpio):
        cpio = mock.Mock()
        mock_cpio.return_value = cpio
        self.task.create_initrd()
        mock_cpio.assert_called_once_with(
            self.task.boot_target_directory + '/initrd.cpio'
        )
        cpio.create.assert_called_once_with(
            source_dir=self.task.boot_root_directory,
            exclude=['/boot', '/var/cache']
        )
