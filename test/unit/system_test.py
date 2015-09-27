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
    def setup(self):
        description = XMLDescription('../data/example_config.xml')
        self.xml = description.load()
        self.system = System(
            xml_data=self.xml, profiles=[], allow_existing=True
        )
        self.system.manager = mock.MagicMock(
            return_value=mock.MagicMock()
        )

    @raises(KiwiBootStrapPhaseFailed)
    def test_install_bootstrap_raises(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_install_requests_bootstrap = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.install_bootstrap()

    @raises(KiwiSystemUpdateFailed)
    def test_update_system_raises(self):
        self.system.repo = mock.Mock()
        self.system.manager.update = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.update_system()

    @raises(KiwiSystemInstallPackagesFailed)
    def test_install_packages_raises(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.install_packages([])

    @raises(KiwiSystemInstallPackagesFailed)
    def test_install_system_raises(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.install_system()

    @raises(KiwiSystemDeletePackagesFailed)
    def test_delete_packages_raises(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_delete_requests = mock.Mock(
            return_value=FakeCommandCall(1)
        )
        self.system.delete_packages([])

    @patch('kiwi.system.RootInit')
    @patch('kiwi.system.RootBind')
    def test_setup_root(self, mock_root_bind, mock_root_init):
        self.system.setup_root('root_dir')
        mock_root_init.assert_called_once_with(
            'root_dir', True
        )
        self.system.root.create.assert_called_once()
        mock_root_bind.assert_called_once_with(
            self.system.root
        )
        self.system.root_bind.setup_intermediate_config.assert_called_once()
        self.system.root_bind.mount_kernel_file_systems.assert_called_once()

    @patch('kiwi.system.Repository.new')
    @patch('kiwi.system.Uri')
    @patch('kiwi.system.PackageManager.new')
    def test_setup_repositories(self, mock_manager, mock_uri, mock_repo):
        uri = mock.Mock()
        mock_uri.return_value = uri
        self.system.root_bind = mock.Mock()
        uri.is_remote = mock.Mock(return_value=False)
        uri.translate = mock.Mock(return_value='foo')
        uri.alias = mock.Mock(return_value='foo-alias')
        self.system.setup_repositories()
        mock_repo.assert_called_once_with(
            self.system.root_bind, self.system.package_manager
        )
        self.system.repo.delete_all_repos.assert_called_once()
        uri.translate.assert_called_once()
        self.system.root_bind.mount_shared_directory.assert_called_once_with(
            'foo'
        )
        uri.alias.assert_called_once()
        self.system.repo.add_bootstrap_repo.assert_called_once_with(
            'foo-alias', 'foo', 'yast2', 42
        )
        assert self.system.uri == [uri]

    def test_install_bootstrap(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_install_requests_bootstrap = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.install_bootstrap()
        self.system.manager.request_package.assert_called()
        self.system.manager.process_install_requests_bootstrap.assert_called_once()

    @patch('kiwi.xml_state.XMLState.system_collection_type')
    def test_install_system(self, mock_collection_type):
        mock_collection_type.return_value = 'onlyRequired'
        self.system.repo = mock.Mock()
        self.system.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.install_system()
        self.system.manager.process_only_required.assert_called_once()
        self.system.manager.request_package.assert_called_with(
            'plymouth-branding-openSUSE'
        )
        self.system.manager.request_collection.assert_called_once_with(
            'base'
        )
        self.system.manager.request_product.assert_called_once_with(
            'openSUSE'
        )

    def test_install_packages(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_install_requests = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.install_packages(['foo'])
        self.system.manager.request_package.assert_called_once_with('foo')

    def test_delete_packages(self):
        self.system.repo = mock.Mock()
        self.system.manager.process_delete_requests = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.delete_packages(['foo'])
        self.system.manager.request_package.assert_called_once_with('foo')

    def test_update_system(self):
        self.system.repo = mock.Mock()
        self.system.manager.update = mock.Mock(
            return_value=FakeCommandCall(0)
        )
        self.system.update_system()
        self.system.manager.update.assert_called_once()

    def test_destructor(self):
        root_bind = mock.Mock()
        self.system.root_bind = mock.Mock(
            return_value=root_bind
        )
        del self.system
        root_bind.cleanup.assert_called_once()

    def test_destructor_raising(self):
        self.system.root_bind = mock.Mock()
        self.system.root_bind.cleanup.side_effect = Exception
        del self.system
