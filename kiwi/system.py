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
import re
import logging

# project
from root_init import RootInit
from root_bind import RootBind
from repository import Repository
from package_manager import PackageManager
from command import Command
from xml_state import XMLState
from uri import Uri

from logger import log

from exceptions import(
    KiwiBootStrapPhaseFailed,
    KiwiSystemUpdateFailed,
    KiwiSystemInstallPackagesFailed,
    KiwiSystemDeletePackagesFailed
)


class System(object):
    """
        Implements preparation and installation of a new root system
    """
    def __init__(self, xml_data, profiles=[], allow_existing=False):
        self.xml = xml_data
        self.profiles = profiles
        self.allow_existing = allow_existing
        self.package_manager = XMLState.package_manager(
            self.xml, self.profiles
        )

    def setup_root(self, root_dir):
        log.info('Setup root directory: %s', root_dir)
        self.root = RootInit(
            root_dir, self.allow_existing
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
        self.repo = Repository.new(
            self.root_bind, self.package_manager
        )
        if self.allow_existing:
            self.repo.delete_all_repos()
        for xml_repo in repository_sections:
            repo_type = xml_repo.get_type()
            repo_source = xml_repo.get_source().get_path()
            repo_alias = xml_repo.get_alias()
            repo_priority = xml_repo.get_priority()
            log.info('Setting up repository %s', repo_source)
            log.info('--> Type: %s', repo_type)
            if repo_priority:
                log.info('--> Priority: %s', repo_priority)

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
                repo_alias, repo_source_translated, repo_type, repo_priority
            )

    def install_bootstrap(self):
        manager = PackageManager.new(self.repo, self.package_manager)
        bootstrap_packages = XMLState.bootstrap_packages(
            self.xml, self.profiles
        )
        bootstrap_packages.append(
            XMLState.package_manager(self.xml, self.profiles)
        )
        log.info('Installing bootstrap packages')
        packages_requested = 0
        packages_processed = 0
        for package in bootstrap_packages:
            log.info('--> package: %s', package)
            manager.request_package(package)
            packages_requested += 1

        self.__init_progress(packages_requested)
        install = manager.process_install_requests_bootstrap()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.debug('bootstrap: %s', line.rstrip('\n'))
                packages_processed = self.__update_progress(
                    bootstrap_packages, packages_processed, packages_requested,
                    line
                )

        self.__stop_progress()
        if install.process.returncode != 0:
            raise KiwiBootStrapPhaseFailed(
                'Bootstrap installation failed: %s' % install.error.read()
            )

    def install_system(self, build_type=None):
        if not build_type:
            build_type = XMLState.build_type(self.xml, self.profiles)
        log.info('Installing system packages for build type: %s', build_type)
        system_packages = XMLState.system_packages(
            self.xml, self.profiles, build_type
        )
        self.install_packages(system_packages)

    def install_packages(self, packages):
        manager = PackageManager.new(self.repo, self.package_manager)
        log.info('Installing system packages (chroot)')
        packages_requested = 0
        packages_processed = 0
        for package in packages:
            log.info('--> package: %s', package)
            manager.request_package(package)
            packages_requested += 1

        self.__init_progress(packages_requested)
        install = manager.process_install_requests()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.debug('system: %s', line.rstrip('\n'))
                packages_processed = self.__update_progress(
                    packages, packages_processed, packages_requested, line
                )

        self.__stop_progress()
        if install.process.returncode != 0:
            raise KiwiSystemInstallPackagesFailed(
                'Package installation failed: %s' % install.error.read()
            )

    def delete_packages(self, packages):
        manager = PackageManager.new(self.repo, self.package_manager)
        log.info('Deleting system packages (chroot)')
        packages_requested = 0
        packages_processed = 0
        for package in packages:
            log.info('--> package: %s', package)
            manager.request_package(package)
            packages_requested += 1

        self.__init_progress(packages_requested)
        delete = manager.process_delete_requests()
        while delete.process.poll() is None:
            line = delete.output.readline()
            if line:
                log.debug('system: %s', line.rstrip('\n'))
                packages_processed = self.__update_progress(
                    packages, packages_processed, packages_requested,
                    line, 'Removing: '
                )

        self.__stop_progress()
        if delete.process.returncode != 0:
            raise KiwiSystemDeletePackagesFailed(
                'Package deletion failed: %s' % delete.error.read()
            )

    def update_system(self):
        manager = PackageManager.new(self.repo, self.package_manager)
        log.info('Update system (chroot)')
        update = manager.update()
        while update.process.poll() is None:
            line = update.output.readline()
            if line:
                log.debug('system: %s', line.rstrip('\n'))

        if update.process.returncode != 0:
            raise KiwiSystemUpdateFailed(
                'System update failed: %s' % update.error.read()
            )

    def __init_progress(self, packages_requested):
        if not log.level == logging.DEBUG:
            log.progress(
                0, packages_requested,
                'INFO: Processing'
            )

    def __stop_progress(self):
        if not log.level == logging.DEBUG:
            log.progress(
                100, 100,
                'INFO: Processing'
            )
            print

    def __update_progress(
        self, packages, packages_processed, packages_requested,
        data, search='Installing: '
    ):
        if not log.level == logging.DEBUG:
            for package in packages:
                # this match for the package to be installed in the output
                # of the zypper command is not 100% accurate. There might
                # be false positives due to sub package names starting with
                # the same base package name
                if re.match('.*' + search + package + '.*', data):
                    packages_processed += 1
                    if packages_processed <= packages_requested:
                        log.progress(
                            packages_processed, packages_requested,
                            'INFO: Processing'
                        )
        return packages_processed

    def __del__(self):
        log.info('Cleaning up Prepare instance')
        try:
            self.root_bind.cleanup()
        except:
            pass
