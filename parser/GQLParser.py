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
        buf.write(u"\27x\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write(u"\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\3")
        buf.write(u"\2\7\2\34\n\2\f\2\16\2\37\13\2\3\2\3\2\3\3\7\3$\n\3\f")
        buf.write(u"\3\16\3\'\13\3\3\3\3\3\6\3+\n\3\r\3\16\3,\3\3\7\3\60")
        buf.write(u"\n\3\f\3\16\3\63\13\3\3\3\7\3\66\n\3\f\3\16\39\13\3\3")
        buf.write(u"\4\5\4<\n\4\3\4\3\4\5\4@\n\4\3\5\3\5\3\5\3\6\3\6\5\6")
        buf.write(u"G\n\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\b\3\b")
        buf.write(u"\3\b\3\b\7\bW\n\b\f\b\16\bZ\13\b\3\t\3\t\3\t\5\t_\n\t")
        buf.write(u"\3\n\3\n\3\n\3\n\3\n\3\n\3\13\3\13\3\13\7\13j\n\13\f")
        buf.write(u"\13\16\13m\13\13\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\r")
        buf.write(u"\3\r\2\2\16\2\4\6\b\n\f\16\20\22\24\26\30\2\3\3\2\17")
        buf.write(u"\20v\2\35\3\2\2\2\4%\3\2\2\2\6;\3\2\2\2\bA\3\2\2\2\n")
        buf.write(u"D\3\2\2\2\fM\3\2\2\2\16R\3\2\2\2\20[\3\2\2\2\22`\3\2")
        buf.write(u"\2\2\24f\3\2\2\2\26n\3\2\2\2\30r\3\2\2\2\32\34\5\4\3")
        buf.write(u"\2\33\32\3\2\2\2\34\37\3\2\2\2\35\33\3\2\2\2\35\36\3")
        buf.write(u"\2\2\2\36 \3\2\2\2\37\35\3\2\2\2 !\7\2\2\3!\3\3\2\2\2")
        buf.write(u"\"$\7\3\2\2#\"\3\2\2\2$\'\3\2\2\2%#\3\2\2\2%&\3\2\2\2")
        buf.write(u"&(\3\2\2\2\'%\3\2\2\2(\61\5\6\4\2)+\7\3\2\2*)\3\2\2\2")
        buf.write(u"+,\3\2\2\2,*\3\2\2\2,-\3\2\2\2-.\3\2\2\2.\60\5\6\4\2")
        buf.write(u"/*\3\2\2\2\60\63\3\2\2\2\61/\3\2\2\2\61\62\3\2\2\2\62")
        buf.write(u"\67\3\2\2\2\63\61\3\2\2\2\64\66\7\3\2\2\65\64\3\2\2\2")
        buf.write(u"\669\3\2\2\2\67\65\3\2\2\2\678\3\2\2\28\5\3\2\2\29\67")
        buf.write(u"\3\2\2\2:<\7\n\2\2;:\3\2\2\2;<\3\2\2\2<?\3\2\2\2=@\5")
        buf.write(u"\b\5\2>@\5\20\t\2?=\3\2\2\2?>\3\2\2\2@\7\3\2\2\2AB\7")
        buf.write(u"\13\2\2BC\5\16\b\2C\t\3\2\2\2DF\7\4\2\2EG\7\21\2\2FE")
        buf.write(u"\3\2\2\2FG\3\2\2\2GH\3\2\2\2HI\7\5\2\2IJ\7\22\2\2JK\7")
        buf.write(u"\6\2\2KL\b\6\1\2L\13\3\2\2\2MN\7\7\2\2NO\7\23\2\2OP\7")
        buf.write(u"\b\2\2PQ\b\7\1\2Q\r\3\2\2\2RX\5\n\6\2ST\5\f\7\2TU\5\n")
        buf.write(u"\6\2UW\3\2\2\2VS\3\2\2\2WZ\3\2\2\2XV\3\2\2\2XY\3\2\2")
        buf.write(u"\2Y\17\3\2\2\2ZX\3\2\2\2[^\7\f\2\2\\_\5\22\n\2]_\5\30")
        buf.write(u"\r\2^\\\3\2\2\2^]\3\2\2\2_\21\3\2\2\2`a\7\r\2\2ab\7\22")
        buf.write(u"\2\2bc\7\4\2\2cd\5\24\13\2de\7\6\2\2e\23\3\2\2\2fk\5")
        buf.write(u"\26\f\2gh\7\t\2\2hj\5\26\f\2ig\3\2\2\2jm\3\2\2\2ki\3")
        buf.write(u"\2\2\2kl\3\2\2\2l\25\3\2\2\2mk\3\2\2\2no\7\21\2\2op\7")
        buf.write(u"\5\2\2pq\t\2\2\2q\27\3\2\2\2rs\7\16\2\2st\7\23\2\2tu")
        buf.write(u"\7\22\2\2uv\7\22\2\2v\31\3\2\2\2\r\35%,\61\67;?FX^k")
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

        def EOF(self):
            return self.getToken(GQLParser.EOF, 0)

        def stmt_list(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(GQLParser.Stmt_listContext)
            else:
                return self.getTypedRuleContext(GQLParser.Stmt_listContext,i)


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
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GQLParser.T__0) | (1 << GQLParser.K_EXPLAIN) | (1 << GQLParser.K_MATCH) | (1 << GQLParser.K_CREATE))) != 0):
                self.state = 24
                self.stmt_list()
                self.state = 29
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 30
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
            self.state = 35
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GQLParser.T__0:
                self.state = 32
                self.match(GQLParser.T__0)
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 38
            self.stmt()
            self.state = 47
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 40 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while True:
                        self.state = 39
                        self.match(GQLParser.T__0)
                        self.state = 42 
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if not (_la==GQLParser.T__0):
                            break

                    self.state = 44
                    self.stmt() 
                self.state = 49
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

            self.state = 53
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 50
                    self.match(GQLParser.T__0) 
                self.state = 55
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

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
            self.state = 57
            _la = self._input.LA(1)
            if _la==GQLParser.K_EXPLAIN:
                self.state = 56
                self.match(GQLParser.K_EXPLAIN)


            self.state = 61
            token = self._input.LA(1)
            if token in [GQLParser.K_MATCH]:
                self.state = 59
                localctx.c = self.match_stmt()

            elif token in [GQLParser.K_CREATE]:
                self.state = 60
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
            self.state = 63
            self.match(GQLParser.K_MATCH)
            self.state = 64
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
            self.state = 66
            self.match(GQLParser.T__1)
            self.state = 68
            _la = self._input.LA(1)
            if _la==GQLParser.I_NAME:
                self.state = 67
                localctx.nn = self.match(GQLParser.I_NAME)


            self.state = 70
            self.match(GQLParser.T__2)

            self.state = 71
            localctx.nt = self.match(GQLParser.I_TYPE)
            self.state = 72
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
            self.rel = None # Token

        def I_RELATION(self):
            return self.getToken(GQLParser.I_RELATION, 0)

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
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75
            self.match(GQLParser.T__4)

            self.state = 76
            localctx.rel = self.match(GQLParser.I_RELATION)
            self.state = 77
            self.match(GQLParser.T__5)

            localctx.relation_data = (None if localctx.rel is None else localctx.rel.text)[1:-1]
              
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
            self.state = 80
            self.node()
            self.state = 86
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GQLParser.T__4:
                self.state = 81
                self.relation()
                self.state = 82
                self.node()
                self.state = 88
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
            self.state = 89
            self.match(GQLParser.K_CREATE)
            self.state = 92
            token = self._input.LA(1)
            if token in [GQLParser.K_TYPE]:
                self.state = 90
                self.create_type()

            elif token in [GQLParser.K_RELATION]:
                self.state = 91
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
            self.state = 94
            self.match(GQLParser.K_TYPE)

            self.state = 95
            self.match(GQLParser.I_TYPE)
            self.state = 96
            self.match(GQLParser.T__1)
            self.state = 97
            self.type_list()
            self.state = 98
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
            self.state = 100
            self.type_decl()
            self.state = 105
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==GQLParser.T__6:
                self.state = 101
                self.match(GQLParser.T__6)
                self.state = 102
                self.type_decl()
                self.state = 107
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
            self.state = 108
            self.match(GQLParser.I_NAME)
            self.state = 109
            self.match(GQLParser.T__2)
            self.state = 110
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
            self.state = 112
            self.match(GQLParser.K_RELATION)
            self.state = 113
            self.match(GQLParser.I_RELATION)
            self.state = 114
            self.match(GQLParser.I_TYPE)
            self.state = 115
            self.match(GQLParser.I_TYPE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx




