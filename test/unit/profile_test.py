from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiUriStyleUnknown,
    KiwiUriTypeUnknown
)

from kiwi.profile import Profile
from kiwi.xml_state import XMLState
from kiwi.xml_description import XMLDescription


class TestProfile(object):
    def setup(self):
        description = XMLDescription('../data/example_dot_profile_config.xml')
        self.profile = Profile(
            XMLState(description.load())
        )

    def test_create(self):
        self.profile.create()
        assert self.profile.dot_profile == {
            'kiwi_allFreeVolume_bin-volume': 'size:all:LVusr_bin',
            'kiwi_allFreeVolume_LVusr_bin': 'size:all',
            'kiwi_bootkernel': None,
            'kiwi_bootloader': 'grub2',
            'kiwi_bootprofile': None,
            'kiwi_boot_timeout': None,
            'kiwi_cmdline': 'splash',
            'kiwi_compressed': None,
            'kiwi_delete': '',
            'kiwi_devicepersistency': None,
            'kiwi_displayname': None,
            'kiwi_drivers': '',
            'kiwi_firmware': 'efi',
            'kiwi_fsmountoptions': None,
            'kiwi_hwclock': 'utc',
            'kiwi_hybrid': None,
            'kiwi_hybridpersistent_filesystem': None,
            'kiwi_hybridpersistent': None,
            'kiwi_iname': 'LimeJeOS-openSUSE-13.2',
            'kiwi_installboot': None,
            'kiwi_iversion': '1.13.2',
            'kiwi_keytable': 'us.map.gz',
            'kiwi_language': 'en_US',
            'kiwi_loader_theme': 'openSUSE',
            'kiwi_LVM_etc-volume': 'freespace:20:LVetc',
            'kiwi_lvmgroup': None,
            'kiwi_LVM_LVRoot': 'freespace:500',
            'kiwi_LVM_LVusr_lib': 'size:1024',
            'kiwi_lvm': True,
            'kiwi_oemataraid_scan': None,
            'kiwi_oembootwait': None,
            'kiwi_oemdevicefilter': None,
            'kiwi_oemkboot': None,
            'kiwi_oemmultipath_scan': None,
            'kiwi_oempartition_install': None,
            'kiwi_oemrebootinteractive': None,
            'kiwi_oemreboot': None,
            'kiwi_oemrecoveryID': None,
            'kiwi_oemrecoveryInPlace': None,
            'kiwi_oemrecovery': False,
            'kiwi_oemrecoveryPartSize': None,
            'kiwi_oemrootMB': 2048,
            'kiwi_oemshutdowninteractive': None,
            'kiwi_oemshutdown': None,
            'kiwi_oemsilentboot': None,
            'kiwi_oemsilentinstall': None,
            'kiwi_oemsilentverify': None,
            'kiwi_oemskipverify': None,
            'kiwi_oemswapMB': None,
            'kiwi_oemswap': True,
            'kiwi_oemtitle': None,
            'kiwi_oemunattended_id': None,
            'kiwi_oemunattended': None,
            'kiwi_oemvmcp_parmfile': None,
            'kiwi_profiles': '',
            'kiwi_ramonly': None,
            'kiwi_showlicense': None,
            'kiwi_splash_theme': 'openSUSE',
            'kiwi_strip_delete': '',
            'kiwi_strip_libs': '',
            'kiwi_strip_tools': '',
            'kiwi_target_blocksize': None,
            'kiwi_timezone': 'Europe/Berlin',
            'kiwi_type': 'oem',
            'kiwi_vga': None,
            'kiwi_wwid_wait_timeout': None,
            'kiwi_xendomain': None
        }

    def test_create_cpio(self):
        description = XMLDescription('../data/example_dot_profile_config.xml')
        profile = Profile(
            XMLState(description.load(), None, 'cpio')
        )
        profile.create()
        assert profile.dot_profile['kiwi_cpio_name'] == 'LimeJeOS-openSUSE-13.2'
