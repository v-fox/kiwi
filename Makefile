all: xml_parser

xml_parser: schema/KIWISchema.xsd
	# XML parser code is auto generated from schema using generateDS
	# http://pythonhosted.org/generateDS
	generateDS.py --external-encoding='utf-8' \
		-o kiwi/xml.py schema/KIWISchema.xsd

schema/KIWISchema.xsd: schema/KIWISchema.rnc
	trang -I rnc -O xsd schema/KIWISchema.rnc schema/KIWISchema.xsd

clean:
	${MAKE} -C schema clean
	find -name *.pyc | xargs rm -f
	rm -rf kiwi.egg-info
	rm -rf build
	rm -rf dist
