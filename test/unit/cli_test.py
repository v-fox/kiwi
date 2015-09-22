import sys
from nose.tools import *

import nose_helper

from kiwi.cli import Cli
from kiwi.exceptions import *


class TestCli(object):
    def setup(self):
        self.help_global_args = {
            'help': False,
            'image': True,
            '-h': False,
            '--version': False,
            '--debug': False,
            '--profile': None,
            '--help': False
        }
        self.command_args = {
            '--description': 'description',
            '--allow-existing-root': False,
            '--help': False,
            '--root': 'directory',
            '--type': None,
            '-h': False,
            'help': False,
            'image': 1,
            'prepare': True
        }
        sys.argv = [
            sys.argv[0],
            'image', 'prepare',
            '--description', 'description',
            '--root', 'directory'
        ]
        self.cli = Cli()
        self.loaded_command = self.cli.load_command()

    def test_show_help(self):
        assert self.cli.show_help() == False

    def test_get_servicename(self):
        assert self.cli.get_servicename() == 'image'

    def test_get_command(self):
        assert self.cli.get_command() == 'prepare'

    def test_get_command_args(self):
        print self.cli.get_command_args()
        assert self.cli.get_command_args() == self.command_args

    def test_get_global_args(self):
        print self.cli.get_global_args()
        assert self.cli.get_global_args() == self.help_global_args

    def test_load_command(self):
        assert self.cli.load_command() == self.loaded_command

    @raises(KiwiUnknownCommand)
    def test_load_command_unknown(self):
        self.cli.loaded = False
        self.cli.all_args['<command>'] = 'foo'
        self.cli.load_command()

    @raises(KiwiLoadCommandUndefined)
    def test_load_command_undefined(self):
        self.cli.loaded = False
        self.cli.all_args['<command>'] = None
        self.cli.load_command()

    @raises(KiwiCommandNotLoaded)
    def test_get_command_args_not_loaded(self):
        self.cli.loaded = False
        self.cli.get_command_args()

    @raises(KiwiUnknownServiceName)
    def test_get_servicename_unknown(self):
        self.cli.all_args['image'] = False
        self.cli.all_args['foo'] = False
        self.cli.get_servicename()
