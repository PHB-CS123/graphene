# Generated from java-escape by ANTLR 4.5
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
package = globals().get("__package__", None)
ischild = len(package)>0 if package is not None else False
if ischild:
    from .GQLListener import GQLListener
else:
    from GQLListener import GQLListener
def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3")
        buf.write(u"\27m\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write(u"\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\3")
        buf.write(u"\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3\5\3$\n\3\7\3&\n\3")
        buf.write(u"\f\3\16\3)\13\3\3\4\5\4,\n\4\3\4\3\4\5\4\60\n\4\3\5\3")
        buf.write(u"\5\3\5\3\6\3\6\5\6\67\n\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7")
        buf.write(u"\3\7\5\7A\n\7\3\7\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3\b\7\b")
        buf.write(u"L\n\b\f\b\16\bO\13\b\3\t\3\t\3\t\5\tT\n\t\3\n\3\n\3\n")
        buf.write(u"\3\n\3\n\3\n\3\13\3\13\3\13\7\13_\n\13\f\13\16\13b\13")
        buf.write(u"\13\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\r\3\r\2\2\16\2")
        buf.write(u"\4\6\b\n\f\16\20\22\24\26\30\2\3\3\2\17\20i\2\32\3\2")
        buf.write(u"\2\2\4\35\3\2\2\2\6+\3\2\2\2\b\61\3\2\2\2\n\64\3\2\2")
        buf.write(u"\2\f=\3\2\2\2\16G\3\2\2\2\20P\3\2\2\2\22U\3\2\2\2\24")
        buf.write(u"[\3\2\2\2\26c\3\2\2\2\30g\3\2\2\2\32\33\5\4\3\2\33\34")
        buf.write(u"\7\2\2\3\34\3\3\2\2\2\35\36\5\6\4\2\36\'\b\3\1\2\37#")
        buf.write(u"\7\3\2\2 !\5\6\4\2!\"\b\3\1\2\"$\3\2\2\2# \3\2\2\2#$")
        buf.write(u"\3\2\2\2$&\3\2\2\2%\37\3\2\2\2&)\3\2\2\2\'%\3\2\2\2\'")
        buf.write(u"(\3\2\2\2(\5\3\2\2\2)\'\3\2\2\2*,\7\n\2\2+*\3\2\2\2+")
        buf.write(u",\3\2\2\2,/\3\2\2\2-\60\5\b\5\2.\60\5\20\t\2/-\3\2\2")
        buf.write(u"\2/.\3\2\2\2\60\7\3\2\2\2\61\62\7\13\2\2\62\63\5\16\b")
        buf.write(u"\2\63\t\3\2\2\2\64\66\7\4\2\2\65\67\7\21\2\2\66\65\3")
        buf.write(u"\2\2\2\66\67\3\2\2\2\678\3\2\2\289\7\5\2\29:\7\22\2\2")
        buf.write(u":;\7\6\2\2;<\b\6\1\2<\13\3\2\2\2=@\7\7\2\2>?\7\21\2\2")
        buf.write(u"?A\7\5\2\2@>\3\2\2\2@A\3\2\2\2AB\3\2\2\2BC\7\23\2\2C")
        buf.write(u"D\3\2\2\2DE\7\b\2\2EF\b\7\1\2F\r\3\2\2\2GM\5\n\6\2HI")
        buf.write(u"\5\f\7\2IJ\5\n\6\2JL\3\2\2\2KH\3\2\2\2LO\3\2\2\2MK\3")
        buf.write(u"\2\2\2MN\3\2\2\2N\17\3\2\2\2OM\3\2\2\2PS\7\f\2\2QT\5")
        buf.write(u"\22\n\2RT\5\30\r\2SQ\3\2\2\2SR\3\2\2\2T\21\3\2\2\2UV")
        buf.write(u"\7\r\2\2VW\7\22\2\2WX\7\4\2\2XY\5\24\13\2YZ\7\6\2\2Z")
        buf.write(u"\23\3\2\2\2[`\5\26\f\2\\]\7\t\2\2]_\5\26\f\2^\\\3\2\2")
        buf.write(u"\2_b\3\2\2\2`^\3\2\2\2`a\3\2\2\2a\25\3\2\2\2b`\3\2\2")
        buf.write(u"\2cd\7\21\2\2de\7\5\2\2ef\t\2\2\2f\27\3\2\2\2gh\7\16")
        buf.write(u"\2\2hi\7\23\2\2ij\7\22\2\2jk\7\22\2\2k\31\3\2\2\2\13")
        buf.write(u"#\'+/\66@MS`")
        return buf.getvalue()


class GQLParser ( Parser ):

    grammarFileName = "java-escape"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"';'", u"'('", u"':'", u"')'", u"'-'", 
                     u"'->'", u"','" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"K_EXPLAIN", u"K_MATCH", u"K_CREATE", u"K_TYPE", 
                      u"K_RELATION", u"T_INT", u"T_STR", u"I_NAME", u"I_TYPE", 
                      u"I_RELATION", u"SPACES", u"BLOCK_COMMENT", u"LINE_COMMENT", 
                      u"UNEXPECTED_CHAR" ]

    RULE_parse = 0
    RULE_stmt_list = 1
    RULE_stmt = 2
    RULE_match_stmt = 3
    RULE_node = 4
    RULE_relation = 5
    RULE_node_chain = 6
    RULE_create_stmt = 7
    RULE_create_type = 8
    RULE_type_list = 9
    RULE_type_decl = 10
    RULE_create_relation = 11

    ruleNames =  [ u"parse", u"stmt_list", u"stmt", u"match_stmt", u"node", 
                   u"relation", u"node_chain", u"create_stmt", u"create_type", 
                   u"type_list", u"type_decl", u"create_relation" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    K_EXPLAIN=8
    K_MATCH=9
    K_CREATE=10
    K_TYPE=11
    K_RELATION=12
    T_INT=13
    T_STR=14
    I_NAME=15
    I_TYPE=16
    I_RELATION=17
    SPACES=18
    BLOCK_COMMENT=19
    LINE_COMMENT=20
    UNEXPECTED_CHAR=21

    def __init__(self, input):
        super(GQLParser, self).__init__(input)
        self.checkVersion("4.5")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class ParseContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.ParseContext, self).__init__(parent, invokingState)
            self.parser = parser

        def stmt_list(self):
            return self.getTypedRuleContext(GQLParser.Stmt_listContext,0)


        def EOF(self):
            return self.getToken(GQLParser.EOF, 0)

        def getRuleIndex(self):
            return GQLParser.RULE_parse

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterParse(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitParse(self)




    def parse(self):

        localctx = GQLParser.ParseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_parse)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self.stmt_list()
            self.state = 25
            self.match(GQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Stmt_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Stmt_listContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.stmts = None
            self.s1 = None # StmtContext
            self.si = None # StmtContext

        def stmt(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GQLParser.StmtContext)
            else:
                return self.getTypedRuleContext(GQLParser.StmtContext,i)


        def getRuleIndex(self):
            return GQLParser.RULE_stmt_list

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterStmt_list(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitStmt_list(self)




    def stmt_list(self):

        localctx = GQLParser.Stmt_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_stmt_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            localctx.s1 = self.stmt()
            localctx.stmts = [localctx.s1]
            self.state = 37
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GQLParser.T__0:
                self.state = 29
                self.match(GQLParser.T__0)
                self.state = 33
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GQLParser.K_EXPLAIN) | (1 << GQLParser.K_MATCH) | (1 << GQLParser.K_CREATE))) != 0):
                    self.state = 30
                    localctx.si = self.stmt()
                    localctx.stmts.append(localctx.si)


                self.state = 39
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class StmtContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.StmtContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.c = None # Match_stmtContext

        def K_EXPLAIN(self):
            return self.getToken(GQLParser.K_EXPLAIN, 0)

        def match_stmt(self):
            return self.getTypedRuleContext(GQLParser.Match_stmtContext,0)


        def create_stmt(self):
            return self.getTypedRuleContext(GQLParser.Create_stmtContext,0)


        def getRuleIndex(self):
            return GQLParser.RULE_stmt

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterStmt(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitStmt(self)




    def stmt(self):

        localctx = GQLParser.StmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            _la = self._input.LA(1)
            if _la==GQLParser.K_EXPLAIN:
                self.state = 40
                self.match(GQLParser.K_EXPLAIN)


            self.state = 45
            token = self._input.LA(1)
            if token in [GQLParser.K_MATCH]:
                self.state = 43
                localctx.c = self.match_stmt()

            elif token in [GQLParser.K_CREATE]:
                self.state = 44
                localctx.c = self.create_stmt()

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Match_stmtContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Match_stmtContext, self).__init__(parent, invokingState)
            self.parser = parser

        def K_MATCH(self):
            return self.getToken(GQLParser.K_MATCH, 0)

        def node_chain(self):
            return self.getTypedRuleContext(GQLParser.Node_chainContext,0)


        def getRuleIndex(self):
            return GQLParser.RULE_match_stmt

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterMatch_stmt(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitMatch_stmt(self)




    def match_stmt(self):

        localctx = GQLParser.Match_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_match_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self.match(GQLParser.K_MATCH)
            self.state = 48
            self.node_chain()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class NodeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.NodeContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.node_data = None
            self.nn = None # Token
            self.nt = None # Token

        def I_TYPE(self):
            return self.getToken(GQLParser.I_TYPE, 0)

        def I_NAME(self):
            return self.getToken(GQLParser.I_NAME, 0)

        def getRuleIndex(self):
            return GQLParser.RULE_node

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterNode(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitNode(self)




    def node(self):

        localctx = GQLParser.NodeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_node)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.match(GQLParser.T__1)
            self.state = 52
            _la = self._input.LA(1)
            if _la==GQLParser.I_NAME:
                self.state = 51
                localctx.nn = self.match(GQLParser.I_NAME)


            self.state = 54
            self.match(GQLParser.T__2)

            self.state = 55
            localctx.nt = self.match(GQLParser.I_TYPE)
            self.state = 56
            self.match(GQLParser.T__3)

            localctx.node_data = { "name": (None if localctx.nn is None else localctx.nn.text), "type": (None if localctx.nt is None else localctx.nt.text) }
              
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RelationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.RelationContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.relation_data = None
            self.rn = None # Token
            self.rel = None # Token

        def I_RELATION(self):
            return self.getToken(GQLParser.I_RELATION, 0)

        def I_NAME(self):
            return self.getToken(GQLParser.I_NAME, 0)

        def getRuleIndex(self):
            return GQLParser.RULE_relation

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterRelation(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitRelation(self)




    def relation(self):

        localctx = GQLParser.RelationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_relation)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self.match(GQLParser.T__4)

            self.state = 62
            _la = self._input.LA(1)
            if _la==GQLParser.I_NAME:
                self.state = 60
                localctx.rn = self.match(GQLParser.I_NAME)
                self.state = 61
                self.match(GQLParser.T__2)


            self.state = 64
            localctx.rel = self.match(GQLParser.I_RELATION)
            self.state = 66
            self.match(GQLParser.T__5)

            localctx.relation_data = { "name": (None if localctx.rn is None else localctx.rn.text), "type": (None if localctx.rel is None else localctx.rel.text)[1:-1] }
              
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Node_chainContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Node_chainContext, self).__init__(parent, invokingState)
            self.parser = parser

        def node(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GQLParser.NodeContext)
            else:
                return self.getTypedRuleContext(GQLParser.NodeContext,i)


        def relation(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GQLParser.RelationContext)
            else:
                return self.getTypedRuleContext(GQLParser.RelationContext,i)


        def getRuleIndex(self):
            return GQLParser.RULE_node_chain

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterNode_chain(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitNode_chain(self)




    def node_chain(self):

        localctx = GQLParser.Node_chainContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_node_chain)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self.node()
            self.state = 75
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GQLParser.T__4:
                self.state = 70
                self.relation()
                self.state = 71
                self.node()
                self.state = 77
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Create_stmtContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Create_stmtContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.c = None

        def K_CREATE(self):
            return self.getToken(GQLParser.K_CREATE, 0)

        def create_type(self):
            return self.getTypedRuleContext(GQLParser.Create_typeContext,0)


        def create_relation(self):
            return self.getTypedRuleContext(GQLParser.Create_relationContext,0)


        def getRuleIndex(self):
            return GQLParser.RULE_create_stmt

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterCreate_stmt(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitCreate_stmt(self)




    def create_stmt(self):

        localctx = GQLParser.Create_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_create_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(GQLParser.K_CREATE)
            self.state = 81
            token = self._input.LA(1)
            if token in [GQLParser.K_TYPE]:
                self.state = 79
                self.create_type()

            elif token in [GQLParser.K_RELATION]:
                self.state = 80
                self.create_relation()

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Create_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Create_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def K_TYPE(self):
            return self.getToken(GQLParser.K_TYPE, 0)

        def type_list(self):
            return self.getTypedRuleContext(GQLParser.Type_listContext,0)


        def I_TYPE(self):
            return self.getToken(GQLParser.I_TYPE, 0)

        def getRuleIndex(self):
            return GQLParser.RULE_create_type

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterCreate_type(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitCreate_type(self)




    def create_type(self):

        localctx = GQLParser.Create_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_create_type)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(GQLParser.K_TYPE)

            self.state = 84
            self.match(GQLParser.I_TYPE)
            self.state = 85
            self.match(GQLParser.T__1)
            self.state = 86
            self.type_list()
            self.state = 87
            self.match(GQLParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Type_listContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Type_listContext, self).__init__(parent, invokingState)
            self.parser = parser

        def type_decl(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GQLParser.Type_declContext)
            else:
                return self.getTypedRuleContext(GQLParser.Type_declContext,i)


        def getRuleIndex(self):
            return GQLParser.RULE_type_list

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterType_list(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitType_list(self)




    def type_list(self):

        localctx = GQLParser.Type_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_type_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.type_decl()
            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GQLParser.T__6:
                self.state = 90
                self.match(GQLParser.T__6)
                self.state = 91
                self.type_decl()
                self.state = 96
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Type_declContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Type_declContext, self).__init__(parent, invokingState)
            self.parser = parser

        def I_NAME(self):
            return self.getToken(GQLParser.I_NAME, 0)

        def T_INT(self):
            return self.getToken(GQLParser.T_INT, 0)

        def T_STR(self):
            return self.getToken(GQLParser.T_STR, 0)

        def getRuleIndex(self):
            return GQLParser.RULE_type_decl

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterType_decl(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitType_decl(self)




    def type_decl(self):

        localctx = GQLParser.Type_declContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_type_decl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.match(GQLParser.I_NAME)
            self.state = 98
            self.match(GQLParser.T__2)
            self.state = 99
            _la = self._input.LA(1)
            if not(_la==GQLParser.T_INT or _la==GQLParser.T_STR):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Create_relationContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(GQLParser.Create_relationContext, self).__init__(parent, invokingState)
            self.parser = parser

        def K_RELATION(self):
            return self.getToken(GQLParser.K_RELATION, 0)

        def I_RELATION(self):
            return self.getToken(GQLParser.I_RELATION, 0)

        def I_TYPE(self, i=None):
            if i is None:
                return self.getTokens(GQLParser.I_TYPE)
            else:
                return self.getToken(GQLParser.I_TYPE, i)

        def getRuleIndex(self):
            return GQLParser.RULE_create_relation

        def enterRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.enterCreate_relation(self)

        def exitRule(self, listener):
            if isinstance( listener, GQLListener ):
                listener.exitCreate_relation(self)




    def create_relation(self):

        localctx = GQLParser.Create_relationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_create_relation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self.match(GQLParser.K_RELATION)
            self.state = 102
            self.match(GQLParser.I_RELATION)
            self.state = 103
            self.match(GQLParser.I_TYPE)
            self.state = 104
            self.match(GQLParser.I_TYPE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx




