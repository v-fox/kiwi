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
from command_process import CommandProcess
from logger import log
from defaults import Defaults

from exceptions import (
    KiwiScriptFailed
)


class SystemSetup(object):
    """
        Implementation of system setup steps supported by kiwi.
        kiwi is not responsible for the system configuration, however
        some setup steps needs to be performed in order to provide
        a minimal work environment inside of the image.
    """
    def __init__(self, xml_state, description_dir, root_dir):
        self.xml_state = xml_state
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
            self.xml_state.xml_data.export(outfile=config, level=0)

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
            script_functions = Defaults.get_common_functions_file()
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

    def import_shell_environment(self, profile):
        profile_file = self.root_dir + '/.profile'
        log.info('Creating environment: %s', profile_file)
        profile_environment = profile.create()
        with open(profile_file, 'w') as profile:
            for line in profile_environment:
                profile.write(line + '\n')
                log.info('--> %s', line)

    def import_overlay_files(
        self, follow_links=False, preserve_owner_group=False
    ):
        overlay_directory = self.description_dir + '/root/'
        if os.path.exists(overlay_directory):
            log.info('Copying user defined files to image tree')
            rsync_options = [
                '-r', '-p', '-t', '-D', '-H', '-X', '-A', '--one-file-system'
            ]
            if follow_links:
                rsync_options.append('--copy-links')
            else:
                rsync_options.append('--links')
            if preserve_owner_group:
                rsync_options.append('-o')
                rsync_options.append('-g')
            Command.run(
                ['rsync'] + rsync_options + [
                    overlay_directory, self.root_dir
                ]
            )

    def import_autoyast_profile(self):
        # TODO: import autoyast profile and setup the firstboot launcher
        raise NotImplementedError

    def setup_hardware_clock(self):
        # TODO: setup hwclock from XML data
        raise NotImplementedError

    def setup_keyboard_map(self):
        # TODO: setup keyboard map from XML data
        raise NotImplementedError

    def setup_locale(self):
        # TODO: setup locale from XML data
        raise NotImplementedError

    def setup_timezone(self):
        # TODO: setup timezone from XML data
        raise NotImplementedError

    def setup_groups(self):
        # TODO: setup user groups from XML
        raise NotImplementedError

    def setup_users(self):
        # TODO: setup users from XML
        raise NotImplementedError

    def import_image_identifier(self):
        image_id = self.xml_state.xml_data.get_id()
        if image_id and os.path.exists(self.root_dir + '/etc'):
            image_id_file = self.root_dir + '/etc/ImageID'
            log.info('Creating identifier: %s as %s', image_id, image_id_file)
            with open(image_id_file, 'w') as identifier:
                identifier.write('%s\n' % image_id)

    def call_config_script(self):
        self.__call_script('config.sh')

    def call_image_script(self):
        self.__call_script('images.sh')

    def __call_script(self, name):
        if os.path.exists(self.root_dir + '/image/' + name):
            config_script = Command.call(
                ['chroot', self.root_dir, 'bash', '-x', '/image/' + name]
            )
            process = CommandProcess(
                command=config_script, log_topic='Calling ' + name + ' script'
            )
            result = process.poll_and_watch()
            if result.returncode != 0:
                raise KiwiScriptFailed(
                    '%s failed: %s' % (name, format(result.stderr))
                )
            log.debug(result.stderr)
