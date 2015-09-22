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
from root_init import RootInit
from root_bind import RootBind
from repository_zypper import RepositoryZypper
from manager_zypper import ManagerZypper
from command import Command
from xml_state import XMLState
from uri import Uri

from logger import log

from exceptions import(
    KiwiBootStrapPhaseFailed,
    KiwiSystemInstallPhaseFailed
)


class Prepare(object):
    """
        Implements preparation and installation of a new root system
    """
    def __init__(self, xml_data, profiles=[]):
        self.xml = xml_data
        self.profiles = profiles

    def setup_root(self, root_dir, allow_existing=False):
        log.info('Creating new root directory: %s', root_dir)
        self.root = RootInit(
            root_dir, allow_existing
        )
        self.root.create()
        self.root_bind = RootBind(
            self.root
        )
        self.root_bind.setup_intermediate_config()
        self.root_bind.mount_kernel_file_systems()
        # self.root_bind.mount_shared_directory()

    def setup_repositories(self):
        self.uri = []
        repository_sections = XMLState.profiled(
            self.xml.get_repository(), self.profiles
        )
        self.repo = RepositoryZypper(
            self.root_bind
        )
        for xml_repo in repository_sections:
            repo_type = xml_repo.get_type()
            repo_source = xml_repo.get_source().get_path()
            repo_alias = xml_repo.get_alias()
            log.info('Setting up repository %s', repo_source)
            log.info('--> Type: %s', repo_type)

            uri = Uri(repo_source, repo_type)
            repo_source_translated = uri.translate()
            log.info('--> Translated: %s', repo_source_translated)
            if not uri.is_remote():
                self.root_bind.mount_shared_directory(repo_source_translated)
            if not repo_alias:
                repo_alias = uri.alias()
            log.info('--> Alias: %s', repo_alias)

            self.uri.append(uri)
            self.repo.add_bootstrap_repo(
                repo_alias, repo_source_translated, repo_type
            )

    def install_bootstrap(self):
        manager = self.__manager()
        bootstrap_packages = XMLState.bootstrap_packages(
            self.xml, self.profiles
        )
        bootstrap_packages.append(
            XMLState.package_manager(self.xml, self.profiles)
        )
        log.info('Installing bootstrap packages')
        for package in bootstrap_packages:
            log.info('--> package: %s', package)
            manager.request_package(package)

        install = manager.install_requests_bootstrap()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.debug('bootstrap: %s', line.rstrip('\n'))

        if install.process.returncode != 0:
            raise KiwiBootStrapPhaseFailed(
                'Bootstrap installation failed'
            )

    def install_system(self, build_type=None):
        manager = self.__manager()
        system_packages = XMLState.system_packages(
            self.xml, self.profiles, build_type
        )
        log.info('Installing system packages (chroot)')
        for package in system_packages:
            log.info('--> package: %s', package)
            manager.request_package(package)

        install = manager.install_requests()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.debug('system: %s', line.rstrip('\n'))

        if install.process.returncode != 0:
            raise KiwiSystemInstallPhaseFailed(
                'System installation failed'
            )

    def __manager(self):
        package_manager = XMLState.package_manager(self.xml, self.profiles)
        if package_manager == 'zypper':
            manager = ManagerZypper(self.repo)
        else:
            raise NotImplementedError(
                'Support for package manager %s not implemented' %
                package_manager
            )
        log.info(
            'Using package manager backend: %s', package_manager
        )
        return manager

    def __del__(self):
        log.info('Cleaning up Prepare instance')
        try:
            self.root_bind.cleanup()
        except:
            pass
