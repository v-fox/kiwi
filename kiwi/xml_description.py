# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
from lxml import etree
from tempfile import NamedTemporaryFile

# project
from command import Command
import xml_parse

from exceptions import (
    KiwiSchemaImportError,
    KiwiValidationError,
    KiwiDescriptionInvalid,
    KiwiDataStructureError
)


class XMLDescription(object):
    """
        Implements data management of the XML description:
        - XSLT Style Sheet processing to apply on this version of kiwi
        - Schema Validation based on RelaxNG schema
        - Loading XML data into internal data structures
    """
    SCHEMA = "schema/KIWISchema.rng"
    STYLE_SHEET = "xsl/master.xsl"

    def __init__(self, description, schema=SCHEMA, stylesheet=STYLE_SHEET):
        self.description_xslt_processed = NamedTemporaryFile()
        self.description = description
        self.stylesheet = stylesheet
        self.schema = schema

    def load(self):
        self.__xsltproc()
        try:
            relaxng = etree.RelaxNG(
                etree.parse(self.schema)
            )
        except Exception as e:
            raise KiwiSchemaImportError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        try:
            description = etree.parse(self.description_xslt_processed.name)
            validation_ok = relaxng.validate(
                description
            )
        except Exception as e:
            raise KiwiValidationError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        if not validation_ok:
            raise KiwiDescriptionInvalid(
                'Schema validation for %s failed' % self.description
            )
        return self.__parse()

    def __parse(self):
        try:
            return xml_parse.parse(
                self.description_xslt_processed.name, True
            )
        except Exception as e:
            raise KiwiDataStructureError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def __xsltproc(self):
        Command.run(
            [
                'xsltproc', '-o', self.description_xslt_processed.name,
                self.stylesheet,
                self.description
            ]
        )
