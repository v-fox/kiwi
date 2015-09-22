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

    def test_package_manager(self):
        assert XMLState.package_manager(self.xml) == 'zypper'

    def test_bootstrap_packages(self):
        assert XMLState.bootstrap_packages(self.xml) == [
            'udev', 'filesystem', 'glibc-locale',
            'cracklib-dict-full', 'ca-certificates',
            'openSUSE-release'
        ]

    def test_system_packages(self):
        print XMLState.system_packages(self.xml, ['vmxFlavour']) == [
            'gfxboot-branding-openSUSE', 'iputils',
            'grub2-branding-openSUSE', 'patterns-openSUSE-base',
            'vim', 'kernel-default', 'ifplugd', 'openssh',
            'plymouth-branding-openSUSE'
        ]
