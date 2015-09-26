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
            return 'line'


class TestSystem(object):
    def setup(self):
        description = XMLDescription('../data/example_config.xml')
        self.xml = description.load()

        self.system = System(
            xml_data=self.xml, profiles=[], allow_existing=True
        )

    @raises(KiwiBootStrapPhaseFailed)
    @patch('kiwi.system.PackageManager.new')
    def test_install_bootstrap_raises(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.process_install_requests_bootstrap = mock.Mock(
            return_value = FakeCommandCall(1)
        )
        self.system.install_bootstrap()

    @raises(KiwiSystemUpdateFailed)
    @patch('kiwi.system.PackageManager.new')
    def test_update_system_raises(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.update = mock.Mock(
            return_value = FakeCommandCall(1)
        )
        self.system.update_system()

    @raises(KiwiSystemInstallPackagesFailed)
    @patch('kiwi.system.PackageManager.new')
    def test_install_packages_raises(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.process_install_requests = mock.Mock(
            return_value = FakeCommandCall(1)
        )
        self.system.install_packages([])

    @raises(KiwiSystemDeletePackagesFailed)
    @patch('kiwi.system.PackageManager.new')
    def test_delete_packages_raises(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.process_delete_requests = mock.Mock(
            return_value = FakeCommandCall(1)
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
    def test_setup_repositories(self, mock_uri, mock_repo):
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

    @patch('kiwi.system.PackageManager.new')
    def test_install_bootstrap(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.process_install_requests_bootstrap = mock.Mock(
            return_value = FakeCommandCall(0)
        )
        self.system.install_bootstrap()
        manager.request_package.assert_called()
        manager.process_install_requests_bootstrap.assert_called_once()

    @patch('kiwi.system.System.install_packages')
    def test_install_system(self, mock_install_packages):
        self.system.install_system()
        self.system.install_packages.assert_called_once()

    @patch('kiwi.system.PackageManager.new')
    def test_install_packages(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.process_install_requests = mock.Mock(
            return_value = FakeCommandCall(0)
        )
        self.system.install_packages(['foo'])
        manager.request_package.assert_called_once_with('foo')

    @patch('kiwi.system.PackageManager.new')
    def test_delete_packages(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.process_delete_requests = mock.Mock(
            return_value = FakeCommandCall(0)
        )
        self.system.delete_packages(['foo'])
        manager.request_package.assert_called_once_with('foo')

    @patch('kiwi.system.PackageManager.new')
    def test_update_system(self, mock_manager):
        self.system.repo = mock.Mock()
        manager = mock.Mock()
        mock_manager.return_value = manager
        manager.update = mock.Mock(
            return_value = FakeCommandCall(0)
        )
        self.system.update_system()
        manager.update.assert_called_once()

    def test_destructor(self):
        root_bind = mock.Mock()
        self.system.root_bind = mock.Mock(
            return_value = root_bind
        )
        del self.system
        root_bind.cleanup.assert_called_once()

    def test_destructor_raising(self):
        self.system.root_bind = mock.Mock()
        self.system.root_bind.cleanup.side_effect = Exception
        del self.system
