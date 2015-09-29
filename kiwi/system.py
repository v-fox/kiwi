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
    def __init__(self, xml_data, root_dir, profiles=[], allow_existing=False):
        """
            setup and host bind new root system at given root_dir directory
        """
        log.info('Setup root directory: %s', root_dir)
        root = RootInit(
            root_dir, allow_existing
        )
        root.create()
        root_bind = RootBind(
            root
        )
        root_bind.setup_intermediate_config()
        root_bind.mount_kernel_file_systems()
        # root_bind.mount_shared_directory()

        self.xml = xml_data
        self.profiles = profiles
        self.allow_existing = allow_existing
        self.root_bind = root_bind

        # A list of Uri references is stored inside of the System instance
        # in order to delay the Uri destructors until the System instance
        # dies. This is needed to keep bind mounted Uri locations alive
        # for System operations
        self.uri_list = []

    def setup_repositories(self):
        """
            set up repositories for software installation and return a
            package manager for performing software installation tasks
        """
        repository_sections = XMLState.profiled(
            self.xml.get_repository(), self.profiles
        )
        package_manager = XMLState.package_manager(
            self.xml, self.profiles
        )
        repo = Repository.new(
            self.root_bind, package_manager
        )
        if self.allow_existing:
            repo.delete_all_repos()
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

            repo.add_bootstrap_repo(
                repo_alias, repo_source_translated, repo_type, repo_priority
            )
            self.uri_list.append(uri)
        return PackageManager.new(
            repo, package_manager
        )

    def install_bootstrap(self, manager):
        """
            install system software using the package manager
            from the host, also known as bootstrapping
        """
        bootstrap_packages = XMLState.bootstrap_packages(
            self.xml, self.profiles
        )
        bootstrap_packages.append(
            XMLState.package_manager(self.xml, self.profiles)
        )
        # TODO: bootstrap: collections and -type, archives, products, ignores
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
                    bootstrap_packages,
                    packages_processed,
                    packages_requested,
                    manager,
                    line
                )

        self.__stop_progress()
        if install.process.returncode != 0:
            raise KiwiBootStrapPhaseFailed(
                'Bootstrap installation failed: %s' % install.error.read()
            )

    def install_system(self, manager, build_type=None):
        """
            install system software using the package manager inside
            of the new root directory. This is done via a chroot operation
            and requires the desired package manager to became installed
            via the bootstrap phase
        """
        if not build_type:
            build_type = XMLState.build_type(self.xml, self.profiles)
        log.info('Installing system (chroot) for build type: %s', build_type)
        collection_type = XMLState.system_collection_type(
            self.xml, self.profiles, build_type
        )
        log.info('--> collection type: %s', collection_type)
        system_packages = XMLState.system_packages(
            self.xml, self.profiles, build_type
        )
        system_collections = XMLState.system_collections(
            self.xml, self.profiles, build_type
        )
        system_products = XMLState.system_products(
            self.xml, self.profiles, build_type
        )
        # TODO: install_system: archives, ignores
        items_requested = 0
        items_processed = 0
        if collection_type == 'onlyRequired':
            manager.process_only_required()

        if system_packages:
            for package in system_packages:
                log.info('--> package: %s', package)
                manager.request_package(package)
                items_requested += 1
        if system_collections:
            for collection in system_collections:
                log.info('--> collection: %s', collection)
                manager.request_collection(collection)
                items_requested += 1
        if system_products:
            for product in system_products:
                log.info('--> product: %s', product)
                manager.request_product(product)
                items_requested += 1

        all_install_items = \
            manager.package_requests + \
            manager.collection_requests + \
            manager.product_requests

        self.__init_progress(items_requested)
        install = manager.process_install_requests()
        while install.process.poll() is None:
            line = install.output.readline()
            if line:
                log.debug('system: %s', line.rstrip('\n'))
                items_processed = self.__update_progress(
                    all_install_items,
                    items_processed,
                    items_requested,
                    manager,
                    line
                )

        self.__stop_progress()
        if install.process.returncode != 0:
            raise KiwiSystemInstallPackagesFailed(
                'System installation failed: %s' % install.error.read()
            )

    def install_packages(self, manager, packages):
        """
            install one or more packages using the package manager inside
            of the new root directory
        """
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
                    packages,
                    packages_processed,
                    packages_requested,
                    manager,
                    line
                )

        self.__stop_progress()
        if install.process.returncode != 0:
            raise KiwiSystemInstallPackagesFailed(
                'Package installation failed: %s' % install.error.read()
            )

    def delete_packages(self, manager, packages):
        """
            delete one or more packages using the package manager inside
            of the new root directory
        """
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
                    packages,
                    packages_processed,
                    packages_requested,
                    manager,
                    line,
                    'deleted'
                )

        self.__stop_progress()
        if delete.process.returncode != 0:
            raise KiwiSystemDeletePackagesFailed(
                'Package deletion failed: %s' % delete.error.read()
            )

    def update_system(self, manager):
        """
            install package updates from the used repositories.
            the process uses the package manager from inside of the
            new root directory
        """
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
                100, 100, 'INFO: Processing'
            )
            print

    def __update_progress(
        self, packages, packages_processed, packages_requested,
        manager, data, mode='installed'
    ):
        if not log.level == logging.DEBUG:
            for package in packages:
                if manager.match_package(package, data, mode):
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
