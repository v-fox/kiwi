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
from lxml import etree

# project
from exceptions import (
    KiwiSchemaImportError,
    KiwiValidationError,
    KiwiDescriptionInvalid
)


class Schema(object):
    """
        Implements RelaxNG Schema Validation for kiwi description
    """
    KIWI_SCHEMA = "schema/KIWISchema.rng"

    def __init__(self, description, schema=KIWI_SCHEMA):
        self.description = description
        self.schema = schema

    def validate(self):
        try:
            relaxng = etree.RelaxNG(
                etree.parse(self.schema)
            )
        except Exception as e:
            raise KiwiSchemaImportError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        try:
            validation_ok = relaxng.validate(
                etree.parse(self.description)
            )
        except Exception as e:
            raise KiwiValidationError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        if not validation_ok:
            raise KiwiDescriptionInvalid(
                'Schema validation for %s failed' % self.description
            )

    def process_style(self):
        # TODO
        pass
