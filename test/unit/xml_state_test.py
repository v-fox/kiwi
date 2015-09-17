from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.xml_state import XMLState
from kiwi.xml_description import XMLDescription


class TestXMLState(object):
    def __init__(self):
        description = XMLDescription('../data/example_config.xml')
        self.xml = description.load()

    def test_profiled(self):
        # TODO
        pass

    def test_build_type(self):
        # TODO
        pass
