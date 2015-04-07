JAR_FILE = lib/antlr-4.5-complete.jar
JAVA_OPTS = "-Dlanguage=Python2"
ANTLR4 = java -cp $(JAR_FILE) org.antlr.v4.Tool $(JAVA_OPTS)

all: parser

clean: clean-parser

parser:
	$(ANTLR4) parser/GQL.g4

clean-parser:
	rm -rf parser/GQL*.py parser/*.tokens

.PHONY: parser clean-parser
