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
        preferences_sections = XMLState.profiled(
            self.xml.get_preferences(), ['ec2Flavour']
        )
        for preferences in preferences_sections:
            profiles = preferences.get_profiles()
            if profiles:
                assert profiles == 'ec2Flavour'

    def test_build_type_primary_selected(self):
        assert XMLState.build_type(self.xml) == 'iso'

    def test_build_type_first_selected(self):
        self.xml.get_preferences()[0].get_type()[0].set_primary(False)
        assert XMLState.build_type(self.xml) == 'iso'
