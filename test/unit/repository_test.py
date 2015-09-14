from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    UriStyleUnknown,
    UriTypeUnknown
)

from kiwi.repository import Repository
from kiwi.root_bind import RootBind

class TestRepository(object):
    def __init__(self):
        root_bind = mock.Mock()
        self.repo = Repository(root_bind)
        self.repo.root_dir = 'root-dir'
        self.repo.shared_location = 'shared-dir'

    @raises(UriStyleUnknown)
    def test_is_remote_raises_style_error(self):
        self.repo.is_remote('xxx')

    @raises(UriTypeUnknown)
    def test_is_remote_raises_type_error(self):
        self.repo.is_remote('xtp://download.example.com')

    @raises(NotImplementedError)
    def test_add_bootstrap_repo(self):
        self.repo.add_bootstrap_repo('name', 'uri', 'type', 'prio')

    @raises(NotImplementedError)
    def test_delete_bootstrap_repo(self):
        self.repo.delete_bootstrap_repo('name')

    @raises(NotImplementedError)
    def test_add_repo(self):
        self.repo.add_repo('name', 'uri', 'type', 'prio')

    @raises(NotImplementedError)
    def test_delete_repo(self):
        self.repo.delete_repo('name')

    def test_is_remote(self):
        # TODO
        pass
