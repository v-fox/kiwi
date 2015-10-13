# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
# project
from shell import Shell


class Profile(object):
    """
        create bash readable .profile environment from the XML
        description. The information is used by the kiwi first
        boot code.
    """
    def __init__(self, xml_state):
        self.xml_state = xml_state
        self.dot_profile = {}

    def write(self):
        self.__image_names_to_profile()
        self.__profile_names_to_profile()
        self.__packages_marked_for_deletion_to_profile()
        self.__type_to_profile()
        self.__preferences_to_profile()
        self.__systemdisk_to_profile()
        # TODO

    def __drivers_to_profile(self):
        # kiwi_drivers
        # TODO
        pass

    def __oemconfig_to_profile(self):
        # kiwi_oemataraid_scan
        # kiwi_oemvmcp_parmfile
        # kiwi_oemmultipath_scan
        # kiwi_oemswapMB
        # kiwi_oemrootMB
        # kiwi_oemswap
        # kiwi_oempartition_install
        # kiwi_oemdevicefilter
        # kiwi_oemtitle
        # kiwi_oemkboot
        # kiwi_oemreboot
        # kiwi_oemrebootinteractive
        # kiwi_oemshutdown
        # kiwi_oemshutdowninteractive
        # kiwi_oemsilentboot
        # kiwi_oemsilentinstall
        # kiwi_oemsilentverify
        # kiwi_oemskipverify
        # kiwi_oembootwait
        # kiwi_oemunattended
        # kiwi_oemunattended_id
        # kiwi_oemrecovery
        # kiwi_oemrecoveryID
        # kiwi_oemrecoveryPartSize
        # kiwi_oemrecoveryInPlace

        # NOTE:
        # + kiwi_oemataraid_scan requires to be added if set to false
        # + kiwi_oemmultipath_scan requires to be added if set to false
        # Reason is they are matched against 'false' in suse-dump. This should
        # be fixed in the kiwi linuxrc code to allow this code to stay simple
        # TODO
        pass

    def __machine_to_profile(self):
        # kiwi_xendomain
        # TODO
        pass

    def __strip_to_profile(self):
        # kiwi_strip_delete
        # kiwi_strip_tools
        # kiwi_strip_libs
        # TODO
        pass

    def __systemdisk_to_profile(self):
        # kiwi_lvmgroup
        # kiwi_lvm
        # kiwi_LVM_LVRoot
        # kiwi_allFreeVolume_X
        # kiwi_LVM_X
        systemdisk = self.xml_state.system_disk()
        if not systemdisk:
            return
        self.dot_profile['kiwi_lvmgroup'] = systemdisk.get_name()
        if self.xml_state.get_volume_management():
            self.dot_profile['kiwi_lvm'] = True
        for volume in self.xml_state.get_volumes():
            if volume.name == 'LV@root':
                if not volume.fullsize:
                    self.dot_profile['kiwi_LVM_LVRoot'] = volume.size
            elif volume.fullsize:
                if volume.mountpoint:
                    self.dot_profile['kiwi_allFreeVolume_' + volume.name] = \
                        'size:all:' + volume.mountpoint
                else:
                    self.dot_profile['kiwi_allFreeVolume_' + volume.name] = \
                        'size:all'
            else:
                if volume.mountpoint:
                    self.dot_profile['kiwi_LVM_' + volume.name] = \
                        volume.size + ':' + volume.mountpoint
                else:
                    self.dot_profile['kiwi_LVM_' + volume.name] = \
                        volume.size

    def __preferences_to_profile(self):
        # kiwi_iversion
        # kiwi_showlicense
        # kiwi_keytable
        # kiwi_timezone
        # kiwi_hwclock
        # kiwi_language
        # kiwi_splash_theme
        # kiwi_loader_theme
        for preferences in self.xml_state.get_build_type_preferences_sections():
            self.dot_profile['kiwi_iversion'] = \
                self.__text(preferences.get_version())
            self.dot_profile['kiwi_showlicense'] = \
                self.__text(preferences.get_showlicense())
            self.dot_profile['kiwi_keytable'] = \
                self.__text(preferences.get_keytable())
            self.dot_profile['kiwi_timezone'] = \
                self.__text(preferences.get_timezone())
            self.dot_profile['kiwi_hwclock'] = \
                self.__text(preferences.get_hwclock())
            self.dot_profile['kiwi_language'] = \
                self.__text(preferences.get_locale())
            self.dot_profile['kiwi_splash_theme'] = \
                self.__text(preferences.get_bootsplash_theme())
            self.dot_profile['kiwi_loader_theme'] = \
                self.__text(preferences.get_bootloader_theme())

    def __type_to_profile(self):
        # kiwi_type
        # kiwi_compressed
        # kiwi_boot_timeout
        # kiwi_wwid_wait_timeout
        # kiwi_hybrid
        # kiwi_hybridpersistent
        # kiwi_hybridpersistent_filesystem
        # kiwi_ramonly
        # kiwi_target_blocksize
        # kiwi_cmdline
        # kiwi_firmware
        # kiwi_bootloader
        # kiwi_devicepersistency
        # kiwi_installboot
        # kiwi_bootkernel
        # kiwi_fsmountoptions
        # kiwi_bootprofile
        # kiwi_vga
        type_section = self.xml_state.build_type
        self.dot_profile['kiwi_type'] = \
            type_section.get_image()
        self.dot_profile['kiwi_compressed'] = \
            type_section.get_compressed()
        self.dot_profile['kiwi_boot_timeout'] = \
            type_section.get_boottimeout()
        self.dot_profile['kiwi_wwid_wait_timeout'] = \
            type_section.get_wwid_wait_timeout()
        self.dot_profile['kiwi_hybrid'] = \
            type_section.get_hybrid()
        self.dot_profile['kiwi_hybridpersistent'] = \
            type_section.get_hybridpersistent()
        self.dot_profile['kiwi_hybridpersistent_filesystem'] = \
            type_section.get_hybridpersistent_filesystem()
        self.dot_profile['kiwi_ramonly'] = \
            type_section.get_ramonly()
        self.dot_profile['kiwi_target_blocksize'] = \
            type_section.get_target_blocksize()
        self.dot_profile['kiwi_cmdline'] = \
            type_section.get_kernelcmdline()
        self.dot_profile['kiwi_firmware'] = \
            type_section.get_firmware()
        self.dot_profile['kiwi_bootloader'] = \
            type_section.get_bootloader()
        self.dot_profile['kiwi_devicepersistency'] = \
            type_section.get_devicepersistency()
        self.dot_profile['kiwi_installboot'] = \
            type_section.get_installboot()
        self.dot_profile['kiwi_bootkernel'] = \
            type_section.get_bootkernel()
        self.dot_profile['kiwi_fsmountoptions'] = \
            type_section.get_fsmountoptions()
        self.dot_profile['kiwi_bootprofile'] = \
            type_section.get_bootprofile()
        self.dot_profile['kiwi_vga'] = \
            type_section.get_vga()

    def __profile_names_to_profile(self):
        # kiwi_profiles
        self.dot_profile['kiwi_profiles'] = ','.join(
            self.xml_state.profiles
        )

    def __packages_marked_for_deletion_to_profile(self):
        # kiwi_delete
        self.dot_profile['kiwi_delete'] = ' '.join(
            self.xml_state.get_to_become_deleted_packages()
        )

    def __image_names_to_profile(self):
        # kiwi_displayname
        # kiwi_cpio_name
        # kiwi_iname
        self.dot_profile['kiwi_iname'] = \
            self.xml_state.xml_data.get_name()
        self.dot_profile['kiwi_displayname'] = \
            self.xml_state.xml_data.get_displayname()

        if self.xml_state.get_build_type_name() == 'cpio':
            self.dot_profile['kiwi_cpio_name'] = self.dot_profile['kiwi_iname']

    def __text(self, section_content):
        """
            helper method to return the text for XML elements of the
            following structure: <section>text</section>. The data
            structure builder will return the text as a list
        """
        if section_content:
            return section_content[0]
