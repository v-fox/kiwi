all: KIWISchema.rng KIWISchema.xsd

KIWISchema.rng: KIWISchema.rnc
	@echo "*** Converting KIWI RNC -> RNG..."
	trang -I rnc -O rng KIWISchema.rnc KIWISchema.rng

KIWISchema.xsd: KIWISchema.rnc
	@echo "*** Converting KIWI RNC -> XSD..."
	trang -I rnc -O xsd KIWISchema.rnc KIWISchema.xsd

clean:
	rm -f *.xsd *.rng
