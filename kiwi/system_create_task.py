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
"""
usage: kiwi system create -h | --help
       kiwi system create --root=<directory> --target-dir=<directory>
       kiwi system create help

commands:
    create
        create a system image from the specified root directory
        the root directory is the result of a system prepare
        command
    create help
        show manual page for create command

options:
    --root=<directory>
        the path to the root directory, usually the result of
        a former system prepare call
    --target-dir=<directory>
        the target directory to store the system image file(s)
"""
# project
import xml_parse

from cli_task import CliTask
from help import Help
from xml_description import XMLDescription
from system import System
from system_setup import SystemSetup
from defaults import Defaults
from profile import Profile
from internal_boot_image_task import BootImageTask
from logger import log

from exceptions import (
    KiwiRequestedTypeError
)


class SystemCreateTask(CliTask):
    """
        Implements creation of system images
    """
    def process(self):
        self.manual = Help()
        if self.__help():
            return

        self.load_xml_description(
            self.command_args['--root']
        )

        if self.command_args['create']:
            boot_image_task = BootImageTask(
                self.xml_state, self.command_args['--target-dir']
            )
            if boot_image_task.required():
                boot_image_task.prepare()
                boot_image_task.extract_kernel_files()
                boot_image_task.create_initrd()

            requested_image_type = self.xml_state.get_build_type_name()
            if requested_image_type in Defaults.get_filesystem_image_types():
                # TODO: pass task to a filesystem builder
                pass
            elif requested_image_type in Defaults.get_disk_image_types():
                install_image = self.xml_state.build_type.get_installiso()
                if not install_image:
                    install_image = self.xml_state.build_type.get_installstick()
                if not install_image:
                    install_image = self.xml_state.build_type.get_installpxe()
                # TODO: pass task to a disk builder
            elif requested_image_type in Defaults.get_live_image_types():
                # TODO: pass task to an iso builder
                pass
            elif requested_image_type in Defaults.get_network_image_types():
                # TODO: pass task to a net builder
                pass
            elif requested_image_type in Defaults.get_archive_image_types():
                # TODO: pass task to an archive builder
                pass
            elif requested_image_type in Defaults.get_container_image_types():
                # TODO: pass task to a container builder
                pass
            else:
                raise KiwiRequestedTypeError(
                    'requested image type %s not supported' %
                    requested_image_type
                )

    def __help(self):
        if self.command_args['help']:
            self.manual.show('kiwi::system::create')
        else:
            return False
        return self.manual
