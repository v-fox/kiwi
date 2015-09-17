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


class XMLState(object):
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
    def build_type(self, xml_data, profiles=[]):
        """
            find default build type to use. take profiles into account
        """
        if not profiles:
            # no profiles specified, lookup profiles marked with import
            profiles_section = xml_data.get_profiles()
            if profiles_section:
                for profile in profiles_section[0].get_profile():
                    name = profile.get_name()
                    import_profile = profile.get_import()
                    if import_profile:
                        profiles.append(name)

        # lookup all preferences sections for configured profiles
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
