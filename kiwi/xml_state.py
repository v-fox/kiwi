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

# project
import xml_parse

from exceptions import(
    KiwiProfileNotFound,
    KiwiTypeNotFound
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

    def preferences_sections(self):
        """
            get all preferences sections for selected profiles
        """
        return self.__profiled(
            self.xml_data.get_preferences()
        )

    def build_type_name(self):
        """
            get default build type name
        """
        return self.build_type.get_image()

    def build_type_preferences_sections(self):
        """
            find preferences sections which belongs to
            the build type and profiles
        """
        preferences_result_sections = []
        for preferences in self.preferences_sections():
            image_types = preferences.get_type()
            if not image_types:
                preferences_result_sections.append(preferences)
            else:
                for image_type in image_types:
                    if image_type.get_image() == self.build_type_name():
                        preferences_result_sections.append(preferences)
                        break
        return preferences_result_sections

    def package_manager(self):
        """
            get configured package manager
        """
        for preferences in self.preferences_sections():
            package_manager = preferences.get_packagemanager()
            if package_manager:
                return package_manager[0]

    def packages_sections(self, section_types='image'):
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

    def to_become_deleted_packages(self):
        """
            get list of packages from the type = delete section
        """
        result = []
        to_become_deleted_packages_sections = self.packages_sections(
            ['delete']
        )
        for packages in to_become_deleted_packages_sections:
            for package in packages.get_package():
                result.append(package.get_name())
        return result

    def bootstrap_packages(self):
        """
            get list of bootstrap packages
        """
        result = []
        bootstrap_packages_sections = self.packages_sections(
            ['bootstrap']
        )
        for packages in bootstrap_packages_sections:
            for package in packages.get_package():
                result.append(package.get_name())
        return result

    def system_packages(self):
        """
            get list of system packages, take build_type into account
        """
        result = []
        image_packages_sections = self.packages_sections(
            ['image', self.build_type_name()]
        )
        for packages in image_packages_sections:
            for package in packages.get_package():
                result.append(package.get_name())
        return list(set(result))

    def bootstrap_archives(self):
        """
            get list of bootstrap archives
        """
        result = []
        bootstrap_packages_sections = self.packages_sections(
            ['bootstrap']
        )
        for packages in bootstrap_packages_sections:
            for archive in packages.get_archive():
                result.append(archive.get_name())
        return result

    def system_archives(self):
        """
            get list of system archives, take build_type into account
        """
        result = []
        image_packages_sections = self.packages_sections(
            ['image', self.build_type_name()]
        )
        for packages in image_packages_sections:
            for archive in packages.get_archive():
                result.append(archive.get_name())
        return result

    def collection_type(self, section_type='image'):
        """
            get collection type specified in system packages sections
            if no collection type is specified only required packages
            are taken into account
        """
        typed_packages_sections = self.packages_sections(
            [section_type, self.build_type_name()]
        )
        collection_type = 'onlyRequired'
        for packages in typed_packages_sections:
            packages_collection_type = packages.get_patternType()
            if packages_collection_type:
                collection_type = packages_collection_type
                break
        return collection_type

    def bootstrap_collection_type(self):
        return self.collection_type('bootstrap')

    def system_collection_type(self):
        return self.collection_type('image')

    def collections(self, section_type='image'):
        """
            get list of collections matching given section and build type
        """
        result = []
        typed_packages_sections = self.packages_sections(
            [section_type, self.build_type_name()]
        )
        for packages in typed_packages_sections:
            for collection in packages.get_namedCollection():
                result.append(collection.get_name())
        return list(set(result))

    def bootstrap_collections(self):
        """
            collections defined in bootstrap section
        """
        return self.collections('bootstrap')

    def system_collections(self):
        """
            collections defined in image sections
        """
        return self.collections('image')

    def products(self, section_type='image'):
        """
            get list of products matching section and build type
        """
        result = []
        typed_packages_sections = self.packages_sections(
            [section_type, self.build_type_name()]
        )
        for packages in typed_packages_sections:
            for product in packages.get_product():
                result.append(product.get_name())
        return list(set(result))

    def bootstrap_products(self):
        """
            get list of products in bootstrap section
        """
        return self.products('bootstrap')

    def system_products(self):
        """
            get list of products in system sections
        """
        return self.products('image')

    def system_disk(self):
        """
            get system disk section
        """
        for systemdisk in self.build_type.get_systemdisk():
            if systemdisk:
                return systemdisk

    def volume_management(self):
        """
            provide information if a volume management system is
            selected and if so return the name
        """
        volume_filesystems = ['btrfs', 'zfs']
        selected_filesystem = self.build_type.get_filesystem()
        selected_system_disk = self.system_disk()
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

    def repository_sections(self):
        return self.__profiled(
            self.xml_data.get_repository()
        )

    def set_repository(self, repo_source, repo_type, repo_alias, repo_prio):
        """
            overwrite repository data for the first repo in the list
        """
        repository = self.repository_sections()[0]
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
        for preferences in self.preferences_sections():
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
