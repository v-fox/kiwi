from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import *
from kiwi.shell import Shell


class TestShell(object):
    def test_quote(self):
        assert Shell.quote('aa\!') == 'aa\\\\\\!'

    def test_quote_key_value_file(self):
        assert Shell.quote_key_value_file('../data/key_value') == [
            "foo='bar'",
            "bar='xxx'",
            "name='bob'",
            "strange='$a_foo'"
        ]
