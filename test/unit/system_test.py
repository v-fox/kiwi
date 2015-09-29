from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiBootStrapPhaseFailed,
    KiwiSystemUpdateFailed,
    KiwiSystemInstallPackagesFailed,
    KiwiSystemDeletePackagesFailed
)

import kiwi

from kiwi.system import System
from kiwi.xml_description import XMLDescription
from kiwi.command import Command


class FakeCommandCall(object):
    def __init__(self, returncode=0):
        self.process = self.__poll(returncode)
        self.output = self.__readline()
        self.error = self.__read()

    class __poll(object):
        def __init__(self, returncode):
            self.toggle_return_value = False
            self.returncode = returncode

        def returncode(self):
            return self.returncode

        def poll(self):
            if not self.toggle_return_value:
                self.toggle_return_value = True
            else:
                return True

    class __readline(object):
        def readline(self):
            return 'Installing: foo'

    class __read(object):
        def read(self):
            return 'error'


class TestSystem(object):
    @patch('kiwi.system.RootInit')
    @patch('kiwi.system.RootBind')
    def setup(self, mock_root_bind, mock_root_init):
        description = XMLDescription('../data/example_config.xml')
        self.xml = description.load()

        self.manager = mock.MagicMock(
            return_value=mock.MagicMock()
        )
        self.manager.package_requests = ['foo']
        self.manager.collection_requests = ['foo']
        self.manager.product_requests = ['foo']

        root_init = mock.MagicMock()
        mock_root_init.return_value = root_init
        root_bind = mock.MagicMock()
        mock_root_bind.return_value = root_bind
        self.system = System(
            xml_data=self.xml, root_dir='root_dir',
            profiles=[], allow_existing=True
        )
        mock_root_init.assert_called_once_with(
            'root_dir', True
        )
        root_init.create.assert_called_once_with()
        mock_root_bind.assert_called_once_with(
            root_init
        )
        root_bind.setup_intermediate_config.assert_called_once_with()
        root_bind.mount_kernel_file_systems.assert_called_once_with()

    @raises(KiwiBootStrapPhaseFailed)
    def test_install_bootstrap_raises(self):
        self.manager.process_install_requests_bootstrap = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.install_bootstrap(self.manager)

    @raises(KiwiSystemUpdateFailed)
    def test_update_system_raises(self):
        self.manager.update = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.update_system(self.manager)

    @raises(KiwiSystemInstallPackagesFailed)
    def test_install_packages_raises(self):
        self.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.install_packages(self.manager, ['package'])

    @raises(KiwiSystemInstallPackagesFailed)
    def test_install_system_raises(self):
        self.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.install_system(self.manager)

    @raises(KiwiSystemDeletePackagesFailed)
    def test_delete_packages_raises(self):
        self.manager.process_delete_requests = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.delete_packages(self.manager, ['package'])

    @patch('kiwi.system.Repository.new')
    @patch('kiwi.system.Uri')
    @patch('kiwi.system.PackageManager.new')
    @patch('kiwi.system.XMLState.package_manager')
    def test_setup_repositories(
        self, mock_package_manager, mock_manager, mock_uri, mock_repo
    ):
        mock_package_manager.return_value = 'package-manager-name'
        uri = mock.Mock()
        mock_uri.return_value = uri
        self.system.root_bind = mock.Mock()
        uri.is_remote = mock.Mock(
            return_value=False
        )
        uri.translate = mock.Mock(
            return_value='uri'
        )
        uri.alias = mock.Mock(
            return_value='uri-alias'
        )
        repo = mock.Mock()
        mock_repo.return_value = repo

        self.system.setup_repositories()

        mock_repo.assert_called_once_with(
            self.system.root_bind, 'package-manager-name'
        )
        # allow_existing is set to true in setup
        repo.delete_all_repos.assert_called_once_with()
        # simulated local repo will be translated and bind mounted
        uri.translate.assert_called_once_with()
        self.system.root_bind.mount_shared_directory.assert_called_once_with(
            'uri'
        )
        uri.alias.assert_called_once_with()
        repo.add_bootstrap_repo.assert_called_once_with(
            'uri-alias', 'uri', 'yast2', 42
        )

    @patch('kiwi.xml_state.XMLState.bootstrap_collection_type')
    def test_install_bootstrap(self, mock_collection_type):
        mock_collection_type.return_value = 'onlyRequired'
        self.manager.process_install_requests_bootstrap = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.install_bootstrap(self.manager)
        self.manager.process_only_required.assert_called_once_with()
        self.manager.request_package.assert_any_call(
            'filesystem'
        )
        self.manager.request_package.assert_any_call(
            'zypper'
        )
        self.manager.request_collection.assert_called_once_with(
            'bootstrap-collection'
        )
        self.manager.request_product.assert_called_once_with(
            'kiwi'
        )
        self.manager.process_install_requests_bootstrap.assert_called_once_with()

    @patch('kiwi.xml_state.XMLState.system_collection_type')
    def test_install_system(self, mock_collection_type):
        mock_collection_type.return_value = 'onlyRequired'
        self.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.install_system(self.manager)
        self.manager.process_only_required.assert_called_once_with()
        self.manager.request_package.assert_called_with(
            'plymouth-branding-openSUSE'
        )
        self.manager.request_collection.assert_called_once_with(
            'base'
        )
        self.manager.request_product.assert_called_once_with(
            'openSUSE'
        )
        self.manager.process_install_requests.assert_called_once_with()

    def test_install_packages(self):
        self.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.install_packages(self.manager, ['foo'])
        self.manager.request_package.assert_called_once_with('foo')

    def test_delete_packages(self):
        self.manager.process_delete_requests = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.delete_packages(self.manager, ['foo'])
        self.manager.request_package.assert_called_once_with('foo')

    def test_update_system(self):
        self.manager.update = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.update_system(self.manager)
        self.manager.update.assert_called_once_with()

    def test_destructor(self):
        self.system.__del__()
        self.system.root_bind.cleanup.assert_called_once_with()

    def test_destructor_raising(self):
        self.system.root_bind = mock.Mock()
        self.system.root_bind.cleanup.side_effect = Exception
        del self.system
