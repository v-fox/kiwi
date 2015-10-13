from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.xml_state import XMLState
from kiwi.xml_description import XMLDescription
from kiwi.exceptions import *
from collections import namedtuple


class TestXMLState(object):
    def setup(self):
        description = XMLDescription(
            '../data/example_config.xml'
        )
        xml_data = description.load()
        self.state = XMLState(xml_data)

    def test_build_type_primary_selected(self):
        assert self.state.build_type_name() == 'iso'

    def test_build_type_first_selected(self):
        self.state.xml_data.get_preferences()[1].get_type()[0].set_primary(
            False
        )
        assert self.state.build_type_name() == 'iso'

    def test_package_manager(self):
        assert self.state.package_manager() == 'zypper'

    def test_bootstrap_packages(self):
        assert self.state.bootstrap_packages() == [
            'filesystem'
        ]

    def test_system_packages(self):
        assert self.state.system_packages() == [
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
        assert self.state.system_collections() == [
            'base'
        ]

    def test_system_products(self):
        assert self.state.system_products() == [
            'openSUSE'
        ]

    def test_system_archives(self):
        assert self.state.system_archives() == [
            'image.tgz'
        ]

    def test_system_collection_type(self):
        assert self.state.system_collection_type() == 'plusRecommended'

    def test_bootstrap_collections(self):
        assert self.state.bootstrap_collections() == [
            'bootstrap-collection'
        ]

    def test_bootstrap_products(self):
        assert self.state.bootstrap_products() == ['kiwi']

    def test_bootstrap_archives(self):
        assert self.state.bootstrap_archives() == ['bootstrap.tgz']

    def test_bootstrap_collection_type(self):
        assert self.state.bootstrap_collection_type() == 'onlyRequired'

    def test_set_repository(self):
        self.state.set_repository('repo', 'type', 'alias', 1)
        assert self.state.xml_data.get_repository()[0].get_source().get_path() \
            == 'repo'
        assert self.state.xml_data.get_repository()[0].get_type() == 'type'
        assert self.state.xml_data.get_repository()[0].get_alias() == 'alias'
        assert self.state.xml_data.get_repository()[0].get_priority() == 1

    def test_add_repository(self):
        self.state.add_repository('repo', 'type', 'alias', 1)
        assert self.state.xml_data.get_repository()[1].get_source().get_path() \
            == 'repo'
        assert self.state.xml_data.get_repository()[1].get_type() == 'type'
        assert self.state.xml_data.get_repository()[1].get_alias() == 'alias'
        assert self.state.xml_data.get_repository()[1].get_priority() == 1

    def test_to_become_deleted_packages(self):
        assert self.state.to_become_deleted_packages() == ['kernel-debug']

    def test_system_disk(self):
        assert self.state.system_disk() == None

    def test_volume_management(self):
        assert self.state.volume_management() == None

    def test_build_type_preferences_sections(self):
        preferences = self.state.build_type_preferences_sections()
        assert preferences[1].get_version()[0] == '1.13.2'

    def test_volume_management_none(self):
        assert self.state.volume_management() == None

    def test_volume_management_btrfs(self):
        description = XMLDescription('../data/example_btrfs_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data)
        assert state.volume_management() == 'btrfs'

    def test_volume_management_lvm_prefer(self):
        description = XMLDescription('../data/example_lvm_preferred_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data)
        assert state.volume_management() == 'lvm'

    def test_volume_management_lvm_default(self):
        description = XMLDescription('../data/example_lvm_default_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data)
        assert state.volume_management() == 'lvm'

    def test_build_type_explicitly_selected(self):
        description = XMLDescription('../data/example_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data, ['vmxFlavour'], 'vmx')
        assert state.build_type_name() == 'vmx'

    @raises(KiwiTypeNotFound)
    def test_build_type_not_found(self):
        description = XMLDescription('../data/example_config.xml')
        xml_data = description.load()
        XMLState(xml_data, ['vmxFlavour'], 'foo')

    @raises(KiwiProfileNotFound)
    def test_profile_not_found(self):
        description = XMLDescription('../data/example_config.xml')
        xml_data = description.load()
        XMLState(xml_data, ['foo'])

    def test_volumes(self):
        description = XMLDescription('../data/example_lvm_default_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data)
        volume_type = namedtuple(
            'volume_type', [
                'name',
                'size',
                'realsize',
                'realpath',
                'mountpoint',
                'fullsize'
            ]
        )
        assert state.volumes() == [
            volume_type(
                name='LVusr_lib', size='size:1024',
                realsize=0, realpath='usr/lib',
                mountpoint=None, fullsize=False
            ),
            volume_type(
                name='LV@root', size='freespace:500',
                realsize=0, realpath=None,
                mountpoint=None, fullsize=False
            ),
            volume_type(
                name='etc-volume', size='freespace:20',
                realsize=0, realpath='etc',
                mountpoint='LVetc', fullsize=False
            ),
            volume_type(
                name='bin-volume', size=None,
                realsize=0, realpath='/usr/bin',
                mountpoint='LVusr_bin', fullsize=True
            )
        ]

    @raises(KiwiInvalidVolumeName)
    def test_volumes_invalid_name(self):
        description = XMLDescription('../data/example_lvm_invalid_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data, ['invalid_volume_a'])
        state.volumes()

    @raises(KiwiInvalidVolumeName)
    def test_volumes_invalid_mountpoint(self):
        description = XMLDescription('../data/example_lvm_invalid_config.xml')
        xml_data = description.load()
        state = XMLState(xml_data, ['invalid_volume_b'])
        state.volumes()

    def test_empty_volumes(self):
        assert self.state.volumes() == []
