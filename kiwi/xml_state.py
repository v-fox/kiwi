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
import re
import platform
from collections import namedtuple

# project
import xml_parse
from defaults import Defaults

from exceptions import(
    KiwiProfileNotFound,
    KiwiTypeNotFound,
    KiwiInvalidVolumeName
)


class XMLState(object):
    """
        Provides methods to get stateful information from the XML data
    """
    def __init__(self, xml_data, profiles=None, build_type=None):
        self.xml_data = xml_data
        self.profiles = self.__used_profiles(
            profiles
        )
        self.build_type = self.__build_type_section(
            build_type
        )

    def get_preferences_sections(self):
        """
            get all preferences sections for selected profiles
        """
        return self.__profiled(
            self.xml_data.get_preferences()
        )

    def get_users_sections(self):
        return self.__profiled(
            self.xml_data.get_users()
        )

    def get_build_type_name(self):
        """
            get default build type name
        """
        return self.build_type.get_image()

    def get_package_manager(self):
        """
            get configured package manager
        """
        for preferences in self.get_preferences_sections():
            package_manager = preferences.get_packagemanager()
            if package_manager:
                return package_manager[0]

    def get_packages_sections(self, section_types='image'):
        """
            get list of packages sections matching given section type
        """
        result = []
        packages_sections = self.__profiled(
            self.xml_data.get_packages()
        )
        for packages in packages_sections:
            packages_type = packages.get_type()
            if packages_type in section_types:
                result.append(packages)
        return result

    def get_package_sections(self, packages_sections):
        """
            get list of package sections from the given packages sections.
            If a package entry specfies an architecture, it is only taken if
            the host architecture matches the configured architecture
        """
        result = []
        if packages_sections:
            host_architecture = platform.machine()
            for packages in packages_sections:
                package_list = packages.get_package()
                if package_list:
                    for package in package_list:
                        package_architecture = package.get_arch()
                        if package_architecture:
                            if package_architecture == host_architecture:
                                result.append(package)
                        else:
                            result.append(package)
        return result

    def get_to_become_deleted_packages(self):
        """
            get list of packages from the type = delete section
        """
        result = []
        to_become_deleted_packages_sections = self.get_packages_sections(
            ['delete']
        )
        package_list = self.get_package_sections(
            to_become_deleted_packages_sections
        )
        if package_list:
            for package in package_list:
                result.append(package.get_name())
        return result

    def get_bootstrap_packages_sections(self):
        """
            get list of bootstrap packages sections
        """
        return self.get_packages_sections(['bootstrap'])

    def get_bootstrap_packages(self):
        """
            get list of bootstrap packages
        """
        result = []
        bootstrap_packages_sections = self.get_bootstrap_packages_sections()
        package_list = self.get_package_sections(
            bootstrap_packages_sections
        )
        if package_list:
            for package in package_list:
                result.append(package.get_name())
        return list(set(result))

    def get_system_packages(self):
        """
            get list of system packages, take build_type into account
        """
        result = []
        image_packages_sections = self.get_packages_sections(
            ['image', self.get_build_type_name()]
        )
        package_list = self.get_package_sections(
            image_packages_sections
        )
        if package_list:
            for package in package_list:
                result.append(package.get_name())
        return list(set(result))

    def get_bootstrap_archives(self):
        """
            get list of bootstrap archives
        """
        result = []
        bootstrap_packages_sections = self.get_bootstrap_packages_sections()
        if bootstrap_packages_sections:
            for bootstrap_packages_section in bootstrap_packages_sections:
                archive_list = bootstrap_packages_section.get_archive()
                if archive_list:
                    for archive in archive_list:
                        result.append(archive.get_name())
        return result

    def get_system_archives(self):
        """
            get list of system archives, take build_type into account
        """
        result = []
        image_packages_sections = self.get_packages_sections(
            ['image', self.get_build_type_name()]
        )
        for packages in image_packages_sections:
            for archive in packages.get_archive():
                result.append(archive.get_name())
        return result

    def get_collection_type(self, section_type='image'):
        """
            get collection type specified in system packages sections
            if no collection type is specified only required packages
            are taken into account
        """
        typed_packages_sections = self.get_packages_sections(
            [section_type, self.get_build_type_name()]
        )
        collection_type = 'onlyRequired'
        for packages in typed_packages_sections:
            packages_collection_type = packages.get_patternType()
            if packages_collection_type:
                collection_type = packages_collection_type
                break
        return collection_type

    def get_bootstrap_collection_type(self):
        return self.get_collection_type('bootstrap')

    def get_system_collection_type(self):
        return self.get_collection_type('image')

    def get_collections(self, section_type='image'):
        """
            get list of collections matching given section and build type
        """
        result = []
        typed_packages_sections = self.get_packages_sections(
            [section_type, self.get_build_type_name()]
        )
        for packages in typed_packages_sections:
            for collection in packages.get_namedCollection():
                result.append(collection.get_name())
        return list(set(result))

    def get_bootstrap_collections(self):
        """
            collections defined in bootstrap section
        """
        return self.get_collections('bootstrap')

    def get_system_collections(self):
        """
            collections defined in image sections
        """
        return self.get_collections('image')

    def get_products(self, section_type='image'):
        """
            get list of products matching section and build type
        """
        result = []
        typed_packages_sections = self.get_packages_sections(
            [section_type, self.get_build_type_name()]
        )
        for packages in typed_packages_sections:
            for product in packages.get_product():
                result.append(product.get_name())
        return list(set(result))

    def get_bootstrap_products(self):
        """
            get list of products in bootstrap section
        """
        return self.get_products('bootstrap')

    def get_system_products(self):
        """
            get list of products in system sections
        """
        return self.get_products('image')

    def get_build_type_system_disk_section(self):
        """
            get system disk section
        """
        systemdisk_sections = self.build_type.get_systemdisk()
        if systemdisk_sections:
            return systemdisk_sections[0]

    def get_build_type_machine_section(self):
        """
            get machine section from build type
        """
        machine_sections = self.build_type.get_machine()
        if machine_sections:
            return machine_sections[0]

    def get_build_type_oemconfig_section(self):
        """
            get oemconfig section from build type
        """
        oemconfig_sections = self.build_type.get_oemconfig()
        if oemconfig_sections:
            return oemconfig_sections[0]

    def get_volumes(self):
        """
            get volumes section from systemdisk
        """
        defaults = Defaults()
        volume_type_list = []
        systemdisk_section = self.get_build_type_system_disk_section()
        if systemdisk_section:
            volumes = systemdisk_section.get_volume()
            if volumes:
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
                for volume in volumes:
                    name = volume.get_name()
                    mountpoint = volume.get_mountpoint()
                    size = volume.get_size()
                    freespace = volume.get_freespace()
                    path = None
                    fullsize = False
                    realpath = None
                    if mountpoint:
                        realpath = mountpoint
                    elif '@root' not in name:
                        realpath = name

                    if not mountpoint:
                        # if no mountpoint is specified the name attribute is
                        # both, the path information as well as the name of
                        # the volume. However turning a path value into a
                        # variable requires to introduce a directory separator
                        # different from '/'. In kiwi the '_' is used and that
                        # forbids to use this letter as part of name if no
                        # mountpoint is specified:
                        if '_' in name:
                            raise KiwiInvalidVolumeName(
                                'mountpoint attribute required for volume %s' %
                                name
                            )
                        name = 'LV' + self.__to_volume_name(name)
                    else:
                        # if a mountpoint path is specified the value is turned
                        # into a path variable and name stays untouched. However
                        # the mountpoint path currently is not allowed to
                        # contain the directory separator '_'. In order to fix
                        # this limitation the way the kiwi initrd code handles
                        # the volume information needs to change first
                        if '_' in mountpoint:
                            raise KiwiInvalidVolumeName(
                                'mountpoint %s must not contain "_"' %
                                mountpoint
                            )
                        mountpoint = 'LV' + self.__to_volume_name(mountpoint)

                    if size:
                        size = 'size:' + format(
                            self.__to_mega_byte(size)
                        )
                    elif freespace:
                        size = 'freespace:' + format(
                            self.__to_mega_byte(freespace)
                        )
                    else:
                        size = 'freespace:' + format(
                            defaults.get('kiwi_freespace')
                        )

                    if ':all' in size:
                        size = None
                        fullsize = True

                    volume_type_list.append(
                        volume_type(
                            name=name,
                            size=size,
                            fullsize=fullsize,
                            realsize=0,
                            mountpoint=mountpoint,
                            realpath=realpath
                        )
                    )
        return volume_type_list

    def get_volume_management(self):
        """
            provide information if a volume management system is
            selected and if so return the name
        """
        volume_filesystems = ['btrfs', 'zfs']
        selected_filesystem = self.build_type.get_filesystem()
        selected_system_disk = self.get_build_type_system_disk_section()
        volume_management = None
        if not selected_system_disk:
            # no systemdisk section exists, no volume management requested
            pass
        elif selected_system_disk.get_preferlvm():
            # LVM volume management is preferred, use it
            volume_management = 'lvm'
        elif selected_filesystem in volume_filesystems:
            # specified filesystem has its own volume management system
            volume_management = selected_filesystem
        else:
            # systemdisk section is specified with non volume capable
            # filesystem and no volume management preference. So let's
            # use LVM by default
            volume_management = 'lvm'
        return volume_management

    def get_drivers_list(self):
        """
            provide list of drivers for configured profiles
        """
        drivers_sections = self.__profiled(
            self.xml_data.get_drivers()
        )
        result = []
        if drivers_sections:
            for driver in drivers_sections:
                for file_section in driver.get_file():
                    result.append(file_section.get_name())
        return result

    def get_strip_list(self, section_type):
        """
            provide list of strip names of the given type for
            configured profiles
        """
        strip_sections = self.__profiled(
            self.xml_data.get_strip()
        )
        result = []
        if strip_sections:
            for strip in strip_sections:
                if strip.get_type() == section_type:
                    for file_section in strip.get_file():
                        result.append(file_section.get_name())
        return result

    def get_strip_files_to_delete(self):
        """
            strip names for delete type
        """
        return self.get_strip_list('delete')

    def get_strip_tools_to_keep(self):
        """
            strip names for tools type
        """
        return self.get_strip_list('tools')

    def get_strip_libraries_to_keep(self):
        """
            strip names for libs type
        """
        return self.get_strip_list('libs')

    def get_repository_sections(self):
        """
            provide repository sections for configured profiles
        """
        return self.__profiled(
            self.xml_data.get_repository()
        )

    def set_repository(self, repo_source, repo_type, repo_alias, repo_prio):
        """
            overwrite repository data for the first repo in the list
        """
        repository = self.get_repository_sections()[0]
        if repo_alias:
            repository.set_alias(repo_alias)
        if repo_type:
            repository.set_type(repo_type)
        if repo_source:
            repository.get_source().set_path(repo_source)
        if repo_prio:
            repository.set_priority(int(repo_prio))

    def add_repository(self, repo_source, repo_type, repo_alias, repo_prio):
        """
            add a new repository section as specified
        """
        self.xml_data.add_repository(
            xml_parse.repository(
                type_=repo_type,
                alias=repo_alias,
                priority=int(repo_prio),
                source=xml_parse.source(path=repo_source)
            )
        )

    def copy_displayname(self, target_state):
        displayname = self.xml_data.get_displayname()
        if displayname:
            target_state.xml_data.set_displayname(displayname)

    def copy_drivers_sections(self, target_state):
        drivers_sections = self.__profiled(
            self.xml_data.get_drivers()
        )
        if drivers_sections:
            for drivers_section in drivers_sections:
                target_state.xml_data.add_drivers(drivers_section)

    def copy_systemdisk_section(self, target_state):
        systemdisk_section = self.get_build_type_system_disk_section()
        if systemdisk_section:
            target_state.build_type.set_systemdisk(
                [systemdisk_section]
            )

    def copy_strip_sections(self, target_state):
        strip_sections = self.__profiled(
            self.xml_data.get_strip()
        )
        if strip_sections:
            for strip_section in strip_sections:
                target_state.xml_data.add_strip(strip_section)

    def copy_machine_section(self, target_state):
        machine_section = self.get_build_type_machine_section()
        if machine_section:
            target_state.build_type.set_machine(
                [machine_section]
            )

    def copy_oemconfig_section(self, target_state):
        oemconfig_section = self.get_build_type_oemconfig_section()
        if oemconfig_section:
            target_state.build_type.set_oemconfig(
                [oemconfig_section]
            )

    def copy_repository_sections(self, target_state, wipe=False):
        repository_sections = self.__profiled(
            self.xml_data.get_repository()
        )
        if repository_sections:
            if wipe:
                target_state.xml_data.set_repository([])
            for repository_section in repository_sections:
                target_state.xml_data.add_repository(repository_section)

    def copy_preferences_subsections(self, section_names, target_state):
        target_preferences_sections = target_state.get_preferences_sections()
        if target_preferences_sections:
            target_preferences_section = target_preferences_sections[0]
            for preferences_section in self.get_preferences_sections():
                for section_name in section_names:
                    get_section_method = getattr(
                        preferences_section, 'get_' + section_name
                    )
                    section = get_section_method()
                    if section:
                        set_section_method = getattr(
                            target_preferences_section, 'set_' + section_name
                        )
                        set_section_method(section)

    def copy_build_type_attributes(self, attribute_names, target_state):
        for attribute in attribute_names:
            get_type_method = getattr(
                self.build_type, 'get_' + attribute
            )
            attribute_value = get_type_method()
            if attribute_value:
                set_type_method = getattr(
                    target_state.build_type, 'set_' + attribute
                )
                set_type_method(attribute_value)

    def copy_bootincluded_packages(self, target_state):
        """
            add packages marked as bootinclude to the packages type=bootstrap
            section. The package will also be removed from the packages
            type=delete section if added there
        """
        target_bootstrap_packages_sections = \
            target_state.get_bootstrap_packages_sections()
        if target_bootstrap_packages_sections:
            target_bootstrap_packages_section = \
                target_bootstrap_packages_sections[0]
            package_names_added = []
            packages_sections = self.get_packages_sections(
                ['image', 'bootstrap', self.get_build_type_name()]
            )
            package_list = self.get_package_sections(
                packages_sections
            )
            if package_list:
                for package in package_list:
                    if package.get_bootinclude():
                        target_bootstrap_packages_section.add_package(
                            xml_parse.package(
                                name=package.get_name()
                            )
                        )
                        package_names_added.append(
                            package.get_name()
                        )
            delete_packages_sections = target_state.get_packages_sections(
                ['delete']
            )
            package_list = self.get_package_sections(
                delete_packages_sections
            )
            if package_list:
                for package in package_list:
                    if package.get_name() in package_names_added:
                        package.set_name(None)

    def copy_bootincluded_archives(self, target_state):
        """
            add archives marked as bootinclude to the
            packages type=bootstrap section
        """
        target_bootstrap_packages_sections = \
            target_state.get_bootstrap_packages_sections()
        if target_bootstrap_packages_sections:
            target_bootstrap_packages_section = \
                target_bootstrap_packages_sections[0]
            package_names_added = []
            packages_sections = self.get_packages_sections(
                ['image', 'bootstrap', self.get_build_type_name()]
            )
            for packages_section in packages_sections:
                archive_list = packages_section.get_archive()
                if archive_list:
                    for archive in archive_list:
                        if archive.get_bootinclude():
                            target_bootstrap_packages_section.add_archive(
                                xml_parse.archive(
                                    name=archive.get_name()
                                )
                            )

    def copy_bootdelete_packages(self, target_state):
        """
            add packages marked as bootdelete to the
            packages type=delete section
        """
        target_delete_packages_sections = target_state.get_packages_sections(
            ['delete']
        )
        if target_delete_packages_sections:
            target_delete_packages_section = \
                target_delete_packages_sections[0]
            packages_sections = self.get_packages_sections(
                ['image', 'bootstrap', self.get_build_type_name()]
            )
            package_list = self.get_package_sections(
                packages_sections
            )
            if package_list:
                for package in package_list:
                    if package.get_bootdelete():
                        target_delete_packages_section.add_package(
                            xml_parse.package(
                                name=package.get_name()
                            )
                        )

    def __used_profiles(self, profiles=None):
        """
            return list of profiles to use. The method looks up the
            profiles section in the XML description and searches for
            profiles marked with import=true. Profiles specified in
            the argument list of this method will take the highest
            priority and causes to skip the lookup of import profiles
            in the XML description
        """
        profile_names = []
        import_profiles = []
        profiles_section = self.xml_data.get_profiles()
        if profiles_section:
            for profile in profiles_section[0].get_profile():
                name = profile.get_name()
                profile_names.append(name)
                if profile.get_import():
                    import_profiles.append(name)
        if not profiles:
            return import_profiles
        else:
            for profile in profiles:
                if profile not in profile_names:
                    raise KiwiProfileNotFound(
                        'profile %s not found' % profile
                    )
            return profiles

    def __build_type_section(self, build_type=None):
        """
            find type section matching build type and profiles or default
        """
        # lookup all preferences sections for selected profiles
        image_type_sections = []
        for preferences in self.get_preferences_sections():
            image_type_sections += preferences.get_type()

        # lookup if build type matches provided type
        if build_type:
            for image_type in image_type_sections:
                if build_type == image_type.get_image():
                    return image_type
            raise KiwiTypeNotFound(
                'build type %s not found' % build_type
            )

        # lookup if build type matches primary type
        for image_type in image_type_sections:
            if image_type.get_primary():
                return image_type

        # build type is first type section in XML sequence
        if image_type_sections:
            return image_type_sections[0]

    def __profiled(self, xml_abstract):
        """
            return only those sections matching the instance stored
            profile list from the given XML abstract. Sections without
            a profile are wildcard sections and will be used in any
            case
        """
        result = []
        for section in xml_abstract:
            profiles = section.get_profiles()
            if profiles:
                for profile in profiles.split(','):
                    if self.profiles and profile in self.profiles:
                        result.append(section)
                        break
            else:
                result.append(section)
        return result

    def __to_volume_name(self, name):
        """
            build a valid volume name
        """
        name = name.strip()
        name = re.sub(r'^\/+', r'', name)
        name = name.replace('/', '_')
        return name

    def __to_mega_byte(self, size):
        value = re.search('(\d+)([MG]*)', format(size))
        if value:
            number = value.group(1)
            unit = value.group(2)
            if unit == 'G':
                return int(number) * 1024
            else:
                return int(number)
        else:
            return size
