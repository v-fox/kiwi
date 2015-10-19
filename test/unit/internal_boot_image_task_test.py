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
    def setup(self):
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

    @patch('os.mkdir')
    @patch('kiwi.defaults.Defaults.get_image_description_path')
    def test_process(self, mock_boot_path, mock_mkdir):
        mock_boot_path.return_value = '../data'
        # TODO
        mock_mkdir.return_value = 'boot-directory'
        self.task.process()
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
        self.task.system.pinch_system.assert_called_once_with(self.manager)
        self.task.setup.call_image_script.assert_called_once_with()

    @raises(KiwiConfigFileNotFound)
    @patch('os.path.exists')
    def test_process_no_boot_description_found(self, mock_os_path):
        mock_os_path.return_value = False
        self.task.process()

    def test_required(self):
        assert self.task.required()

    def test_get_result(self):
        assert self.task.get_result() == None
