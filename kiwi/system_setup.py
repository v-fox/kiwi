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
from command import Command
from logger import log


class SystemSetup(object):
    """
        Implementation of system setup steps regarding the
        the root directory contents to match the requirements
        of the system description. This includes:
        + import of overlay files
        + creation of .profile environment (boot images)
        + import of config.sh script
        + import of images.sh script
        + calling config.sh|images.sh scripts
        + import of stateful XML description
    """
    def __init__(self, xml_data, description_dir, root_dir):
        self.xml = xml_data
        self.description_dir = description_dir
        self.root_dir = root_dir

    def import_description(self):
        """
            import XML descriptions, custom scripts and script helper methods
        """
        description = self.root_dir + '/image/config.xml'
        log.info('Writing description to %s', description)
        Command.run(['mkdir', '-p', self.root_dir + '/image'])
        with open(description, 'w') as config:
            config.write('<?xml version="1.0" encoding="utf-8"?>')
            self.xml.export(outfile=config, level=0)

        need_script_helper_functions = False
        config_script = self.description_dir + '/config.sh'
        image_script = self.description_dir + '/images.sh'
        script_target = self.root_dir + '/image'

        if os.path.exists(config_script):
            log.info(
                '--> Importing config.sh script to %s', script_target
            )
            Command.run(['cp', config_script, script_target])
            need_script_helper_functions = True

        if os.path.exists(image_script):
            log.info(
                '--> Importing image.sh script to %s', script_target
            )
            Command.run(['cp', image_script, script_target])
            need_script_helper_functions = True

        if need_script_helper_functions:
            script_functions = self.__get_script_helper_functions()
            script_functions_target = self.root_dir + '/.kconfig'
            log.info(
                '--> Importing script helper methods to %s',
                script_functions_target
            )
            Command.run([
                'cp', script_functions, script_functions_target
            ])

    def cleanup(self):
        """
            delete all traces of a kiwi description which are not
            required in the later image
        """
        Command.run(['rm', '-r', '-f', '/.kconfig', '/image'])

    def import_shell_environment(self):
        # TODO
        raise NotImplementedError

    def import_overlay_files(self):
        # TODO
        raise NotImplementedError

    def call_config_script(self):
        # TODO
        raise NotImplementedError

    def call_image_script(self):
        # TODO
        raise NotImplementedError

    def __get_script_helper_functions(self):
        return 'config/functions.sh'
