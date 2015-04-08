JAR_FILE = lib/antlr-4.5-complete.jar
JAVA_OPTS = "-Dlanguage=Python2"
ANTLR4 = java -cp $(JAR_FILE) org.antlr.v4.Tool $(JAVA_OPTS)
SRC = graphene

all: parser

clean: clean-parser

parser:
	$(ANTLR4) $(SRC)/parser/GQL.g4

clean-parser:
	rm -rf $(SRC)/parser/GQL*.py $(SRC)/parser/*.tokens

run: all
	./graphene-client

.PHONY: parser clean-parser
