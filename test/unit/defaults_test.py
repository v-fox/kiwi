from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.defaults import Defaults


class TestDefaults(object):
    def setup(self):
        self.defaults = Defaults()

    def test_get(self):
        assert self.defaults.get('kiwi_align') == 1048576
        assert self.defaults.get('kiwi_startsector') == 2048
        assert self.defaults.get('kiwi_sectorsize') == 512
        assert self.defaults.get('kiwi_freespace') == 20
        assert self.defaults.get('kiwi_inode_size') == 256
        assert self.defaults.get('kiwi_inode_ratio') == 16384
        assert self.defaults.get('kiwi_min_inodes') == 20000
        assert self.defaults.get('kiwi_revision')

    def test_to_profile(self):
        profile = mock.MagicMock()
        self.defaults.to_profile(profile)
        profile.add.assert_any_call('kiwi_align', 1048576)
        profile.add.assert_any_call('kiwi_startsector', 2048)
        profile.add.assert_any_call('kiwi_sectorsize', 512)
        profile.add.assert_any_call(
            'kiwi_revision', self.defaults.get('kiwi_revision')
        )
