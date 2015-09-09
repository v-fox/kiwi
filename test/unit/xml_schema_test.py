from nose.tools import *
from mock import patch

import mock

import nose_helper

from kiwi.exceptions import (
    KiwiSchemaImportError,
    KiwiValidationError,
    KiwiDescriptionInvalid
)
from kiwi.xml_schema import Schema


class TestSchema(object):
    def __init__(self):
        self.schema = Schema('description')

    @raises(KiwiSchemaImportError)
    @patch('lxml.etree.RelaxNG')
    def test_validate_schema_import_error(self, mock_relax):
        mock_relax.side_effect = KiwiSchemaImportError(
            'ImportError'
        )
        self.schema.validate()

    @raises(KiwiValidationError)
    @patch('lxml.etree.RelaxNG')
    @patch('lxml.etree.parse')
    def test_validate_schema_validation_error(self, mock_parse, mock_relax):
        mock_validate = mock.Mock()
        mock_validate.validate.side_effect = KiwiValidationError(
            'ValidationError'
        )
        mock_relax.return_value = mock_validate
        self.schema.validate()

    @raises(KiwiDescriptionInvalid)
    @patch('lxml.etree.RelaxNG')
    @patch('lxml.etree.parse')
    def test_validate_schema_description_invalid(self, mock_parse, mock_relax):
        mock_validate = mock.Mock()
        mock_validate.validate = mock.Mock(
            return_value=False
        )
        mock_relax.return_value = mock_validate
        self.schema.validate()

    def test_process_style(self):
        # TODO
        self.schema.process_style()
