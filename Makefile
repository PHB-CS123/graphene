JAR_FILE = lib/antlr-4.5-complete.jar
JAVA_OPTS = "-Dlanguage=Python2"
ANTLR4 = java -cp $(JAR_FILE) org.antlr.v4.Tool $(JAVA_OPTS)
SRC = graphene

default: parser

all: parser docs

clean: clean-parser
	rm -rf $(BUILDDIR)/*
	rm -rf dir/*.rst

parser:
	$(ANTLR4) $(SRC)/parser/GQL.g4

clean-parser:
	rm -rf $(SRC)/parser/GQL*.py $(SRC)/parser/*.tokens

run: all
	./graphene-client

test:
	py.test

docs:
	make -f Makefile.docs html

.PHONY: clean parser clean-parser docs
