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
import os
from tempfile import mkdtemp

from defaults import Defaults
from xml_description import XMLDescription
from xml_state import XMLState
from system import System
from profile import Profile
from system_setup import SystemSetup
from logger import log

from exceptions import(
    KiwiConfigFileNotFound
)


class BootImageTask(object):
    """
        Implements preparation and creation of boot(initrd) images
    """
    def __init__(self, xml_state, target_dir):
        self.xml_state = xml_state
        self.target_dir = target_dir

    def prepare(self):
        """
            build the boot(initrd) image and store the result in
            the given target directory
        """
        self.__load_boot_xml_description()
        self.__import_system_description_elements()

        log.info('Preparing boot image')
        self.boot_root_directory = mkdtemp(
            prefix='boot-', dir=self.target_dir
        )
        self.system = System(
            xml_state=self.boot_xml_state,
            root_dir=self.boot_root_directory,
            allow_existing=True
        )
        manager = self.system.setup_repositories()
        self.system.install_bootstrap(
            manager
        )
        self.system.install_system(
            manager
        )

        profile = Profile(self.boot_xml_state)

        defaults = Defaults()
        defaults.to_profile(profile)

        self.setup = SystemSetup(
            self.boot_xml_state,
            self.__boot_description_directory(),
            self.boot_root_directory
        )
        self.setup.import_shell_environment(profile)
        self.setup.import_description()
        self.setup.import_overlay_files(
            follow_links=True
        )
        self.setup.call_config_script()

        self.system.pinch_system(
            manager=manager, force=True
        )

        self.setup.call_image_script()

    def required(self):
        """
            check if building a boot image is required according to
            the selected system image type. if the type specifies a
            boot attribute containing the path to a boot image
            description, this indicates we need one
        """
        if self.__boot_description_directory():
            return True

    def extract_kernel(self):
        # TODO: extract kernel files, needs an extract class
        pass

    def create_initrd(self):
        # TODO: create cpio image from prepared tree
        pass

    def __import_system_description_elements(self):
        self.xml_state.copy_displayname(
            self.boot_xml_state
        )
        self.xml_state.copy_repository_sections(
            target_state=self.boot_xml_state,
            wipe=True
        )
        self.xml_state.copy_drivers_sections(
            self.boot_xml_state
        )
        strip_description = XMLDescription(
            Defaults.get_boot_image_strip_file()
        )
        strip_xml_state = XMLState(strip_description.load())
        strip_xml_state.copy_strip_sections(
            self.boot_xml_state
        )
        preferences_subsection_names = [
            'bootloader_theme',
            'bootsplash_theme',
            'locale',
            'packagemanager',
            'rpm_check_signatures',
            'showlicense'
        ]
        self.xml_state.copy_preferences_subsections(
            preferences_subsection_names, self.boot_xml_state
        )
        self.xml_state.copy_bootincluded_packages(
            self.boot_xml_state
        )
        self.xml_state.copy_bootincluded_archives(
            self.boot_xml_state
        )
        self.xml_state.copy_bootdelete_packages(
            self.boot_xml_state
        )
        type_attributes = [
            'bootkernel',
            'bootloader',
            'bootprofile',
            'boottimeout',
            'devicepersistency',
            'filesystem',
            'firmware',
            'fsmountoptions',
            'hybrid',
            'hybridpersistent',
            'hybridpersistent_filesystem',
            'installboot',
            'installprovidefailsafe',
            'kernelcmdline',
            'ramonly',
            'vga',
            'wwid_wait_timeout'
        ]
        self.xml_state.copy_build_type_attributes(
            type_attributes, self.boot_xml_state
        )
        self.xml_state.copy_systemdisk_section(
            self.boot_xml_state
        )
        self.xml_state.copy_machine_section(
            self.boot_xml_state
        )
        self.xml_state.copy_oemconfig_section(
            self.boot_xml_state
        )

    def __load_boot_xml_description(self):
        log.info('Loading Boot XML description')
        boot_description_directory = self.__boot_description_directory()
        boot_config_file = boot_description_directory + '/config.xml'
        if not os.path.exists(boot_config_file):
            raise KiwiConfigFileNotFound(
                'no Boot XML description found in %s' %
                boot_description_directory
            )
        boot_description = XMLDescription(
            boot_config_file
        )
        self.boot_xml_data = boot_description.load()
        self.boot_config_file = boot_config_file

        boot_image_profile = self.xml_state.build_type.get_bootprofile()
        if not boot_image_profile:
            boot_image_profile = 'default'
        boot_kernel_profile = self.xml_state.build_type.get_bootkernel()
        if not boot_kernel_profile:
            boot_kernel_profile = 'std'

        self.boot_xml_state = XMLState(
            self.boot_xml_data, [boot_image_profile, boot_kernel_profile]
        )
        log.info('--> loaded %s', self.boot_config_file)
        if self.boot_xml_state.build_type:
            log.info(
                '--> Selected build type: %s',
                self.boot_xml_state.get_build_type_name()
            )
        if self.boot_xml_state.profiles:
            log.info(
                '--> Selected boot profiles: image: %s, kernel: %s',
                boot_image_profile, boot_kernel_profile
            )

    def __boot_description_directory(self):
        boot_description = self.xml_state.build_type.get_boot()
        if boot_description:
            if not boot_description[0] == '/':
                boot_description = Defaults.get_image_description_path() + \
                    '/' + boot_description
            return boot_description
