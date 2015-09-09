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
import xml_parse
from xml_schema import Schema


class App(object):
    """
        Application class to create task instances and process them
    """
    def __init__(self):
        # playground, some testing code
        # image_xml = xml_parse.parse('/home/ms/config.xml', True)
        # print image_xml.get_name()
        # print image_xml.get_preferences()[0].get_type()[0].get_image()
        # image_xml.get_packages()[0].add_package(xml_parse.package(name='foo'))
        # for p in image_xml.get_packages()[0].get_package():
        #    print p.get_name()

        schema = Schema('/home/ms/Project/kiwi-maintenance/kiwi/template/ix86/suse-13.2-JeOS/config.xml')
        schema.validate()
