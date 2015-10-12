all: xml_parser

pep8:
	tools/run-pep8

.PHONY: test
test:
	nosetests --with-coverage --cover-erase --cover-package=kiwi --cover-xml
	tools/coverage-check

coverage:
	nosetests --with-coverage --cover-erase --cover-package=kiwi --cover-xml
	mv test/unit/coverage.xml test/unit/coverage.reference.xml

list_tests:
	@for i in test/unit/*_test.py; do basename $$i;done | sort

%.py:
	nosetests $@

kiwi/xml_parse.py: schema/KIWISchema.xsd
	# XML parser code is auto generated from schema using generateDS
	# http://pythonhosted.org/generateDS
	generateDS.py --external-encoding='utf-8' \
		-o kiwi/xml_parse.py schema/KIWISchema.xsd

schema/KIWISchema.xsd: schema/KIWISchema.rnc
	trang -I rnc -O xsd schema/KIWISchema.rnc schema/KIWISchema.xsd

clean:
	find -name *.pyc | xargs rm -f
	rm -rf kiwi.egg-info
	rm -rf build
	rm -rf dist
