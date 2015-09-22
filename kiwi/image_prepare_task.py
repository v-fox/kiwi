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
usage: kiwi image prepare -h | --help
       kiwi image prepare --description=<directory> --root=<directory>
           [--allow-existing-root]
       kiwi image prepare help

commands:
    prepare
        prepare and install a new system for chroot access
    --description=<directory>
        the description must be a directory containing a kiwi XML
        description and optional metadata files
    --root=<directory>
        the path to the new root directory of the system
    help
        show manual page for prepare command
"""
# project
import xml_parse

from cli_task import CliTask
from help import Help
from root_init import RootInit
from root_bind import RootBind
from repository_zypper import RepositoryZypper
from manager_zypper import ManagerZypper
from command import Command
from xml_state import XMLState
from xml_description import XMLDescription
from uri import Uri

from logger import log

from exceptions import(
    KiwiBootStrapPhaseFailed,
    KiwiSystemInstallPhaseFailed
)


class ImagePrepareTask(CliTask):
    """
        Implements preparation and installation of a new root system
    """
    def process(self):
        self.manual = Help()
        if self.__help():
            return

        if self.command_args['prepare']:
            self.__load_xml()
            self.__setup_new_root()
            self.__bind_new_root_to_host()
            self.__setup_repositories()
            self.__install_bootstrap()
            self.__install_system()

    def __help(self):
        if self.command_args['help']:
            self.manual.show('kiwi::image::prepare')
        else:
            return False
        return self.manual

    def __load_xml(self):
        description = XMLDescription(
            self.command_args['--description'] + '/config.xml'
        )
        self.xml = description.load()

    def __setup_new_root(self):
        self.root = RootInit(
            self.command_args['--root'],
            self.command_args['--allow-existing-root']
        )
        self.root.create()

    def __bind_new_root_to_host(self):
        self.root_bind = RootBind(self.root)
        self.root_bind.setup_intermediate_config()
        self.root_bind.mount_kernel_file_systems()
        # self.root_bind.mount_shared_directory()

    def __setup_repositories(self):
        self.uri = []
        repository_sections = XMLState.profiled(
            self.xml.get_repository(), self.__profiles()
        )
        self.repo = RepositoryZypper(
            self.root_bind
        )
        for xml_repo in repository_sections:
            repo_type = xml_repo.get_type()
            repo_source = xml_repo.get_source().get_path()
            repo_alias = xml_repo.get_alias()

            uri = Uri(repo_source, repo_type)
            repo_source_translated = uri.translate()
            if not uri.is_remote():
                self.root_bind.mount_shared_directory(repo_source_translated)
            if not repo_alias:
                repo_alias = uri.alias()

            self.uri.append(uri)
            self.repo.add_bootstrap_repo(
                repo_alias, repo_source_translated, repo_type
            )

    def __install_bootstrap(self):
        manager = self.__manager()
        bootstrap_packages = self.__bootstrap_packages()
        bootstrap_packages.append(self.__package_manager())
        for package in bootstrap_packages:
            manager.request_package(package)

        install = manager.install_requests_bootstrap()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.info('bootstrap: %s', line.rstrip('\n'))

        if install.process.returncode != 0:
            raise KiwiBootStrapPhaseFailed(
                'Bootstrap installation failed'
            )

    def __install_system(self):
        manager = self.__manager()
        system_packages = self.__system_packages()
        for package in system_packages:
            manager.request_package(package)

        install = manager.install_requests()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.info('system: %s', line.rstrip('\n'))

        if install.process.returncode != 0:
            raise KiwiSystemInstallPhaseFailed(
                'System installation failed'
            )

    def __manager(self):
        package_manager = self.__package_manager()
        if package_manager == 'zypper':
            manager = ManagerZypper(self.repo)
        else:
            raise NotImplementedError(
                'Support for package manager %s not implemented' %
                package_manager
            )
        return manager

    def __package_manager(self):
        preferences_sections = XMLState.profiled(
            self.xml.get_preferences(), self.__profiles()
        )
        for preferences in preferences_sections:
            return preferences.get_packagemanager()[0]

    def __bootstrap_packages(self):
        result = []
        packages_sections = XMLState.profiled(
            self.xml.get_packages(), self.__profiles()
        )
        for packages in packages_sections:
            packages_type = packages.get_type()
            if packages_type == 'bootstrap':
                for package in packages.get_package():
                    result.append(package.get_name())
        return result

    def __system_packages(self, build_type=None):
        result = []
        if not build_type:
            build_type = XMLState.build_type(self.xml)
        packages_sections = XMLState.profiled(
            self.xml.get_packages(), self.__profiles()
        )
        for packages in packages_sections:
            packages_type = packages.get_type()
            if packages_type == 'image' or packages_type == build_type:
                for package in packages.get_package():
                    result.append(package.get_name())
        return result

    def __profiles(self):
        if self.global_args['--profile']:
            return self.global_args['--profile'].split(',')
        return []

    def __del__(self):
        try:
            self.root_bind.cleanup()
        except:
            pass
