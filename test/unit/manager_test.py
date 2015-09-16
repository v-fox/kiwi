from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.manager import Manager


class TestManager(object):
    def __init__(self):
        repository = mock.Mock()
        repository.root_dir = 'root-dir'
        self.manager = Manager(repository)

    @raises(NotImplementedError)
    def test_request_package(self):
        self.manager.request_package('name')

    @raises(NotImplementedError)
    def test_request_collection(self):
        self.manager.request_collection('name')

    @raises(NotImplementedError)
    def test_request_product(self):
        self.manager.request_product('name')

    @raises(NotImplementedError)
    def test_install_requests_bootstrap(self):
        self.manager.install_requests_bootstrap()

    @raises(NotImplementedError)
    def test_install_requests(self):
        self.manager.install_requests()

    def test_cleanup_requests(self):
        self.manager.cleanup_requests()
        assert self.manager.package_requests == []
        assert self.manager.product_requests == []
        assert self.manager.collection_requests == []
