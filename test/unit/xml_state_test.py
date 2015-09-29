from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.xml_state import XMLState
from kiwi.xml_description import XMLDescription
from kiwi.exceptions import (
    KiwiConfigFileNotFound
)


class TestXMLState(object):
    def setup(self):
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

    def test_package_manager(self):
        assert XMLState.package_manager(self.xml) == 'zypper'

    def test_bootstrap_packages(self):
        assert XMLState.bootstrap_packages(self.xml) == [
            'udev', 'filesystem', 'glibc-locale',
            'cracklib-dict-full', 'ca-certificates',
            'openSUSE-release'
        ]

    def test_system_packages(self):
        print XMLState.system_packages(self.xml)
        assert XMLState.system_packages(self.xml) == [
            'gfxboot-branding-openSUSE',
            'iputils',
            'grub2-branding-openSUSE',
            'vim',
            'kernel-default',
            'ifplugd',
            'openssh',
            'plymouth-branding-openSUSE'
        ]

    def test_system_collections(self):
        assert XMLState.system_collections(self.xml) == [
            'base'
        ]

    def test_system_products(self):
        assert XMLState.system_products(self.xml) == [
            'openSUSE'
        ]

    def test_system_collection_type(self):
        assert XMLState.system_collection_type(self.xml) == 'plusRecommended'

    def test_set_repository(self):
        XMLState.set_repository(self.xml, 'repo', 'type', 'alias', 1)
        assert self.xml.get_repository()[0].get_source().get_path() == 'repo'
        assert self.xml.get_repository()[0].get_type() == 'type'
        assert self.xml.get_repository()[0].get_alias() == 'alias'
        assert self.xml.get_repository()[0].get_priority() == 1

    def test_add_repository(self):
        XMLState.add_repository(self.xml, 'repo', 'type', 'alias', 1)
        assert self.xml.get_repository()[1].get_source().get_path() == 'repo'
        assert self.xml.get_repository()[1].get_type() == 'type'
        assert self.xml.get_repository()[1].get_alias() == 'alias'
        assert self.xml.get_repository()[1].get_priority() == 1

    @raises(KiwiConfigFileNotFound)
    def test_load_xml(self):
        XMLState.load_xml('foo')

    def test_load_xml_first_choice(self):
        assert XMLState.load_xml('../data/description')[1] == \
            '../data/description/config.xml'

    def test_load_xml_second_choice(self):
        assert XMLState.load_xml('../data/root-dir')[1] == \
            '../data/root-dir/image/config.xml'
