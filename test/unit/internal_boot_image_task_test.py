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

        self.task = BootImageTask(
            XMLState(xml_data), 'some-target-dir'
        )

    def test_process(self):
        # TODO
        self.task.process()

    @raises(KiwiConfigFileNotFound)
    @patch('os.path.exists')
    def test_process_no_boot_description_found(self, mock_os_path):
        mock_os_path.return_value = False
        self.task.process()

    def test_required(self):
        assert self.task.required()

    def test_get_result(self):
        assert self.task.get_result() == None
