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
from collections import namedtuple

# project
from root_init import RootInit
from root_bind import RootBind
from repository import Repository
from package_manager import PackageManager
from command import Command
from command_process import CommandProcess
from xml_state import XMLState
from uri import Uri

from logger import log

from exceptions import(
    KiwiBootStrapPhaseFailed,
    KiwiCommandError,
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
        log.info('Installing bootstrap packages')
        bootstrap_packages = XMLState.bootstrap_packages(
            self.xml, self.profiles
        )
        bootstrap_packages.append(
            XMLState.package_manager(self.xml, self.profiles)
        )
        collection_type = XMLState.bootstrap_collection_type(
            self.xml, self.profiles
        )
        log.info('--> collection type: %s', collection_type)
        bootstrap_collections = XMLState.bootstrap_collections(
            self.xml, self.profiles
        )
        bootstrap_products = XMLState.bootstrap_products(
            self.xml, self.profiles
        )
        # TODO: bootstrap: archives
        if collection_type == 'onlyRequired':
            manager.process_only_required()
        all_install_items = self.__setup_requests(
            manager,
            bootstrap_packages,
            bootstrap_collections,
            bootstrap_products
        )
        process = CommandProcess(
            command=manager.process_install_requests_bootstrap(),
            log_topic='bootstrap'
        )
        try:
            process.poll_show_progress(
                items_to_complete=all_install_items,
                match_method=process.create_match_method(
                    manager.match_package_installed
                )
            )
        except Exception as e:
            raise KiwiBootStrapPhaseFailed(
                'Bootstrap installation failed: %s' % format(e)
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
        # TODO: archives, type=delete packages
        if collection_type == 'onlyRequired':
            manager.process_only_required()
        all_install_items = self.__setup_requests(
            manager,
            system_packages,
            system_collections,
            system_products
        )
        process = CommandProcess(
            command=manager.process_install_requests(), log_topic='system'
        )
        try:
            process.poll_show_progress(
                items_to_complete=all_install_items,
                match_method=process.create_match_method(
                    manager.match_package_installed
                )
            )
        except Exception as e:
            raise KiwiSystemInstallPackagesFailed(
                'System installation failed: %s' % format(e)
            )

    def install_packages(self, manager, packages):
        """
            install one or more packages using the package manager inside
            of the new root directory
        """
        log.info('Installing system packages (chroot)')
        all_install_items = self.__setup_requests(
            manager, packages
        )
        process = CommandProcess(
            command=manager.process_install_requests(), log_topic='system'
        )
        try:
            process.poll_show_progress(
                items_to_complete=all_install_items,
                match_method=process.create_match_method(
                    manager.match_package_installed
                )
            )
        except Exception as e:
            raise KiwiSystemInstallPackagesFailed(
                'Package installation failed: %s' % format(e)
            )

    def delete_packages(self, manager, packages):
        """
            delete one or more packages using the package manager inside
            of the new root directory
        """
        log.info('Deleting system packages (chroot)')
        all_delete_items = self.__setup_requests(
            manager, packages
        )
        process = CommandProcess(
            command=manager.process_delete_requests(), log_topic='system'
        )
        try:
            process.poll_show_progress(
                items_to_complete=all_delete_items,
                match_method=process.create_match_method(
                    manager.match_package_deleted
                )
            )
        except Exception as e:
            raise KiwiSystemDeletePackagesFailed(
                'Package deletion failed: %s' % format(e)
            )

    def update_system(self, manager):
        """
            install package updates from the used repositories.
            the process uses the package manager from inside of the
            new root directory
        """
        log.info('Update system (chroot)')
        process = CommandProcess(
            command=manager.update(), log_topic='update'
        )
        try:
            process.poll()
        except Exception as e:
            raise KiwiSystemUpdateFailed(
                'System update failed: %s' % format(e)
            )

    def __setup_requests(self, manager, packages, collections=[], products=[]):
        if packages:
            for package in packages:
                log.info('--> package: %s', package)
                manager.request_package(package)
        if collections:
            for collection in collections:
                log.info('--> collection: %s', collection)
                manager.request_collection(collection)
        if products:
            for product in products:
                log.info('--> product: %s', product)
                manager.request_product(product)
        return \
            manager.package_requests + \
            manager.collection_requests + \
            manager.product_requests

    def __del__(self):
        log.info('Cleaning up Prepare instance')
        try:
            self.root_bind.cleanup()
        except:
            pass
