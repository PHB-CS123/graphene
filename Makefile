JAR_FILE = lib/antlr-4.5-complete.jar
JAVA_OPTS = "-Dlanguage=Python2"
ANTLR4 = java -cp $(JAR_FILE) org.antlr.v4.Tool $(JAVA_OPTS)
SRC = graphene
BUILD_DIR = build/
TEST_DIR = tests/
COV_OPTS = --cov-report term-missing --cov-report html --cov-config .coveragerc --cov $(SRC) $(TEST_DIR)

default: parser

all: parser docs

clean: clean-parser clean-docs clean-build

parser:
	$(ANTLR4) $(SRC)/parser/GQL.g4

clean-parser:
	rm -rf $(SRC)/parser/GQL*.py* $(SRC)/parser/*.tokens

run: default
	./graphene-client

test: default build-index
	py.test $(COV_OPTS)

# need to make parser here since docs will run parser code
docs: build-index parser
	make -f Makefile.docs html

clean-docs:
	make -f Makefile.docs clean

clean-build:
	rm -rf build

build-server: build-index
	cd $(BUILD_DIR); python2 -m SimpleHTTPServer 12323; cd ..

build-index:
	mkdir -p build
	cp res/build-index.html build/index.html

.PHONY: clean clean-parser docs
