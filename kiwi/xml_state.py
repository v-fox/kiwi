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
from xml_description import XMLDescription

from exceptions import (
    KiwiConfigFileNotFound
)


class XMLState(object):
    """
        Provides methods to get stateful information from the XML data
    """
    @classmethod
    def load_xml(self, directory):
        config_file = directory + '/config.xml'
        if not os.path.exists(config_file):
            config_file = directory + '/image/config.xml'
        if not os.path.exists(config_file):
            raise KiwiConfigFileNotFound(
                'no XML description found in %s' % directory
            )
        description = XMLDescription(
            config_file
        )
        return [description.load(), config_file.replace('//', '/')]

    @classmethod
    def profiled(self, xml_data, matching=None):
        """
            return only those sections matching the given profiles
            sections without a profile are wildcard sections and will
            be used in any case
        """
        result = []
        for section in xml_data:
            profiles = section.get_profiles()
            if profiles:
                for profile in profiles.split(','):
                    if matching and profile in matching:
                        result.append(section)
                        break
            else:
                result.append(section)
        return result

    @classmethod
    def used_profiles(self, xml_data, profiles=None):
        """
            return list of profiles to use. The method looks up the
            profiles section in the XML description and searches for
            profiles marked with import=true. Profiles specified in
            the argument list of this method will take the highest
            priority and causes to skip the lookup of import profiles
            in the XML description
        """
        if not profiles:
            profiles = []
            profiles_section = xml_data.get_profiles()
            if profiles_section:
                for profile in profiles_section[0].get_profile():
                    name = profile.get_name()
                    import_profile = profile.get_import()
                    if import_profile:
                        profiles.append(name)
        return profiles

    @classmethod
    def preferences_sections(self, xml_data, profiles=None):
        """
            find all preferences sections for selected profiles
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        return XMLState.profiled(
            xml_data.get_preferences(), profiles
        )

    @classmethod
    def default_build_type(self, xml_data, profiles=None):
        """
            find default build type
        """
        return self.build_type_section(xml_data, profiles).get_image()

    @classmethod
    def build_type_section(self, xml_data, profiles=None, build_type=None):
        """
            find type section matching build type or default
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)

        # lookup all preferences sections for selected profiles
        image_type_sections = []
        preferences_sections = self.preferences_sections(xml_data, profiles)
        for preferences in preferences_sections:
            image_type_sections += preferences.get_type()

        # lookup if build type matches provided type
        if build_type:
            for image_type in image_type_sections:
                if build_type == image_type.get_image():
                    return image_type

        # lookup if build type matches primary type
        for image_type in image_type_sections:
            if image_type.get_primary():
                return image_type

        # build type is first type section in XML sequence
        return image_type_sections[0]

    @classmethod
    def build_type_preferences_sections(
        self, xml_data, profiles=None, build_type=None
    ):
        """
            find preferences sections which belongs to
            the build type and profiles
        """
        preferences_result_sections = []
        build_type = self.build_type_section(
            xml_data, profiles, build_type
        ).get_image()
        preferences_sections = self.preferences_sections(xml_data, profiles)
        for preferences in preferences_sections:
            image_types = preferences.get_type()
            if not image_types:
                preferences_result_sections.append(preferences)
            else:
                for image_type in image_types:
                    if image_type.get_image() == build_type:
                        preferences_result_sections.append(preferences)
                        break
        return preferences_result_sections

    @classmethod
    def package_manager(self, xml_data, profiles=None):
        """
            get configured package manager
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        preferences_sections = self.preferences_sections(xml_data, profiles)
        for preferences in preferences_sections:
            return preferences.get_packagemanager()[0]

    @classmethod
    def packages_sections(self, xml_data, profiles=None, section_types='image'):
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        packages_sections = XMLState.profiled(
            xml_data.get_packages(), profiles
        )
        for packages in packages_sections:
            packages_type = packages.get_type()
            if packages_type in section_types:
                result.append(packages)
        return result

    @classmethod
    def to_become_deleted_packages(self, xml_data, profiles=None):
        """
            get list of packages from the type = delete section
        """
        result = []
        to_become_deleted_packages_sections = XMLState.packages_sections(
            xml_data, profiles, ['delete']
        )
        for packages in to_become_deleted_packages_sections:
            for package in packages.get_package():
                result.append(package.get_name())
        return result

    @classmethod
    def bootstrap_packages(self, xml_data, profiles=None):
        """
            get list of bootstrap packages
        """
        result = []
        bootstrap_packages_sections = XMLState.packages_sections(
            xml_data, profiles, ['bootstrap']
        )
        for packages in bootstrap_packages_sections:
            for package in packages.get_package():
                result.append(package.get_name())
        return result

    @classmethod
    def system_packages(self, xml_data, profiles=None, build_type=None):
        """
            get list of system packages, take build_type into account
        """
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        if not build_type:
            build_type = XMLState.default_build_type(xml_data, profiles)
        image_packages_sections = XMLState.packages_sections(
            xml_data, profiles, ['image', build_type]
        )
        for packages in image_packages_sections:
            for package in packages.get_package():
                result.append(package.get_name())
        return list(set(result))

    @classmethod
    def bootstrap_archives(self, xml_data, profiles=None):
        """
            get list of bootstrap archives
        """
        result = []
        bootstrap_packages_sections = XMLState.packages_sections(
            xml_data, profiles, ['bootstrap']
        )
        for packages in bootstrap_packages_sections:
            for archive in packages.get_archive():
                result.append(archive.get_name())
        return result

    @classmethod
    def system_archives(self, xml_data, profiles=None, build_type=None):
        """
            get list of system archives, take build_type into account
        """
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        if not build_type:
            build_type = XMLState.default_build_type(xml_data, profiles)
        image_packages_sections = XMLState.packages_sections(
            xml_data, profiles, ['image', build_type]
        )
        for packages in image_packages_sections:
            for archive in packages.get_archive():
                result.append(archive.get_name())
        return result

    @classmethod
    def bootstrap_collection_type(self, xml_data, profiles=None):
        return self.collection_type(
            xml_data, profiles, None, 'bootstrap'
        )

    @classmethod
    def system_collection_type(self, xml_data, profiles=None, build_type=None):
        return self.collection_type(
            xml_data, profiles, build_type, 'image'
        )

    @classmethod
    def collection_type(
        self, xml_data, profiles=None, build_type=None, section_type='image'
    ):
        """
            get collection type specified in system packages sections
            if no collection type is specified only required packages
            are taken into account
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        if not build_type:
            build_type = XMLState.default_build_type(xml_data, profiles)
        typed_packages_sections = XMLState.packages_sections(
            xml_data, profiles, [section_type, build_type]
        )
        collection_type = 'onlyRequired'
        for packages in typed_packages_sections:
            packages_collection_type = packages.get_patternType()
            if packages_collection_type:
                collection_type = packages_collection_type
                break
        return collection_type

    @classmethod
    def bootstrap_collections(self, xml_data, profiles=None):
        return self.collections(
            xml_data, profiles, None, 'bootstrap'
        )

    @classmethod
    def system_collections(self, xml_data, profiles=None, build_type=None):
        return self.collections(
            xml_data, profiles, build_type, 'image'
        )

    @classmethod
    def collections(
        self, xml_data, profiles=None, build_type=None, section_type='image'
    ):
        """
            get list of system collections, take build_type into account
        """
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        if not build_type:
            build_type = XMLState.default_build_type(xml_data, profiles)
        typed_packages_sections = XMLState.packages_sections(
            xml_data, profiles, [section_type, build_type]
        )
        for packages in typed_packages_sections:
            for collection in packages.get_namedCollection():
                result.append(collection.get_name())
        return list(set(result))

    @classmethod
    def bootstrap_products(self, xml_data, profiles=None):
        return self.products(
            xml_data, profiles, None, 'bootstrap'
        )

    @classmethod
    def system_products(self, xml_data, profiles=None, build_type=None):
        return self.products(
            xml_data, profiles, build_type, 'image'
        )

    @classmethod
    def products(
        self, xml_data, profiles=None, build_type=None, section_type='image'
    ):
        """
            get list of system products, take build_type into account
        """
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        if not build_type:
            build_type = XMLState.default_build_type(xml_data, profiles)
        typed_packages_sections = XMLState.packages_sections(
            xml_data, profiles, [section_type, build_type]
        )
        for packages in typed_packages_sections:
            for product in packages.get_product():
                result.append(product.get_name())
        return list(set(result))

    @classmethod
    def set_repository(
        self, xml_data,
        repo_source, repo_type, repo_alias, repo_prio,
        profiles=None
    ):
        """
            overwrite repository data for the first repo in the list
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        repository_sections = XMLState.profiled(
            xml_data.get_repository(), profiles
        )
        repository = repository_sections[0]
        if repo_alias:
            repository.set_alias(repo_alias)
        if repo_type:
            repository.set_type(repo_type)
        if repo_source:
            repository.get_source().set_path(repo_source)
        if repo_prio:
            repository.set_priority(int(repo_prio))

    @classmethod
    def add_repository(
        self, xml_data,
        repo_source, repo_type, repo_alias, repo_prio
    ):
        """
            add a new repository section as specified
        """
        xml_data.add_repository(
            xml_parse.repository(
                type_=repo_type,
                alias=repo_alias,
                priority=int(repo_prio),
                source=xml_parse.source(path=repo_source)
            )
        )
