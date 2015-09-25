from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiUriStyleUnknown,
    KiwiUriTypeUnknown
)

from kiwi.repository_base import RepositoryBase
from kiwi.root_bind import RootBind


class TestRepositoryBase(object):
    def setup(self):
        root_bind = mock.Mock()
        self.repo = RepositoryBase(root_bind)
        self.repo.root_dir = 'root-dir'
        self.repo.shared_location = 'shared-dir'

    @raises(NotImplementedError)
    def test_runtime_config(self):
        self.repo.runtime_config()

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

    @raises(NotImplementedError)
    def test_delete_all_repos(self):
        self.repo.delete_all_repos()
