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
import xml_parse


class XMLState(object):
    """
        Provides methods to get stateful information from the XML data
    """
    @classmethod
    def profiled(self, xml_data, matching=[]):
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
                    if profile in matching:
                        result.append(section)
                        break
            else:
                result.append(section)
        return result

    @classmethod
    def used_profiles(self, xml_data, profiles=[]):
        """
            return list of profiles to use. The method looks up the
            profiles section in the XML description and searches for
            profiles marked with import=true. Profiles specified in
            the argument list of this method will take the highest
            priority and causes to skip the lookup of import profiles
            in the XML description
        """
        if not profiles:
            profiles_section = xml_data.get_profiles()
            if profiles_section:
                for profile in profiles_section[0].get_profile():
                    name = profile.get_name()
                    import_profile = profile.get_import()
                    if import_profile:
                        profiles.append(name)
        return profiles

    @classmethod
    def build_type(self, xml_data, profiles=[]):
        """
            find default build type
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)

        # lookup all preferences sections for selected profiles
        image_type_sections = []
        preferences_sections = XMLState.profiled(
            xml_data.get_preferences(), profiles
        )
        for preferences in preferences_sections:
            image_type_sections += preferences.get_type()

        # lookup primary type name in preferences or first type listed
        type_names = []
        for image_type in image_type_sections:
            type_name = image_type.get_image()
            if image_type.get_primary():
                return type_name
            type_names.append(type_name)
        return type_names[0]

    @classmethod
    def package_manager(self, xml_data, profiles=[]):
        """
            get configured package manager
        """
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        preferences_sections = XMLState.profiled(
            xml_data.get_preferences(), profiles
        )
        for preferences in preferences_sections:
            return preferences.get_packagemanager()[0]

    @classmethod
    def bootstrap_packages(self, xml_data, profiles=[]):
        """
            get list of bootstrap packages
        """
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        packages_sections = XMLState.profiled(
            xml_data.get_packages(), profiles
        )
        for packages in packages_sections:
            packages_type = packages.get_type()
            if packages_type == 'bootstrap':
                for package in packages.get_package():
                    result.append(package.get_name())
        return result

    @classmethod
    def system_packages(self, xml_data, profiles=[], build_type=None):
        """
            get list of system packages, take build_type into account
        """
        result = []
        if not profiles:
            profiles = XMLState.used_profiles(xml_data, profiles)
        if not build_type:
            build_type = XMLState.build_type(xml_data, profiles)
        packages_sections = XMLState.profiled(
            xml_data.get_packages(), profiles
        )
        for packages in packages_sections:
            packages_type = packages.get_type()
            if packages_type == 'image' or packages_type == build_type:
                for package in packages.get_package():
                    result.append(package.get_name())
        return list(set(result))

    @classmethod
    def set_repository(
        self, xml_data,
        repo_source, repo_type, repo_alias, repo_prio,
        profiles=[]
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
            repository.set_priority(repo_prio)

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
                priority=repo_prio,
                source=xml_parse.source(path=repo_source)
            )
        )
