grammar GQL;

@header {
from graphene.commands import *
from graphene.expressions import *
}

// General parsing, including statement lists
parse : stmt_list EOF;

stmt_list returns [stmts]
  : s1=stmt {$stmts = [$s1.ctx]}
    (';' (si=stmt {$stmts.append($si.ctx)})? )*
  ;

stmt
  : ( c=match_stmt
    | c=create_stmt | c=delete_stmt
    | c=exit_stmt
    | c=show_stmt | c=desc_stmt
    | c=insert_stmt
    )
  ;

// EXIT command
exit_stmt returns [cmd]
  : (K_EXIT | K_QUIT)
  {$cmd = ExitCommand()}
  ;

// MATCH command
match_stmt returns [cmd]
  @init {$cmd = None}
  : K_MATCH (nc=node_chain) (K_WHERE (qc=query_chain))?
  {$cmd = MatchCommand($nc.ctx, $qc.ctx)}
  ;

node_chain returns [chain]
  @init {$chain = []}
  : (n1=node {$chain.append($n1.ctx)})
    (ri=relation {$chain.append($ri.ctx)}
     ni=node {$chain.append($ni.ctx)})*
  {return $chain}
  ;

node
  : '('
    (nn=I_NAME ':')?
    (nt=I_TYPE)
    ')'
  {return MatchNode($nn.text, $nt.text)}
  ;

// Queries

logic_op : (K_AND/* | K_OR*/) ;
logic_test : (('!' | '>' | '<')? '=' | '<' | '>') ;

query_chain returns [queries]
  @init {$queries = []}
  : ( ((i1=I_NAME) '.')? n1=I_NAME t1=logic_test v1=Literal {$queries.append(($i1.text, $n1.text, $t1.text, $v1.text))})
    (op=logic_op {$queries.append($op.text)}
     ((ii=I_NAME) '.')? ni=I_NAME ti=logic_test vi=Literal {$queries.append(($ii.text, $ni.text, $ti.text, $vi.text))})*
  {return $queries}
  ;

node_query
  : (t=I_TYPE {$t=$t.text})
    ('(' (qc=query_chain) ')')?
  {return ($t, $qc.ctx or ())}
  ;

relation_query
  : '-' '['
    (rel=(I_RELATION|I_TYPE) {$rel.text.isupper()}? {$rel = $rel.text})
    ('(' (qc=query_chain) ')')?
    ']' '->'
  {return ($rel, $qc.ctx or ())}
  ;

/*
 * I_RELATION matches all totally uppercase strings, and I_TYPE matches all
 * strings that start with a capital letter... but if the string is one
 * character long, this is ambiguous. Hence we allow both identifier
 * possibilities, but ensure they pass the fully uppercase predicate.
 */
relation
  : '-' '[' (rn=I_NAME ':')? (rel=(I_RELATION|I_TYPE) {$rel.text.isupper()}?) ']' '->'
  {return MatchRelation($rn.text, $rel.text)}
  ;

// CREATE command
create_stmt returns [cmd]
  @init {$cmd = None}
  : K_CREATE ( ct=create_type
             | cr=create_relation
             )
  {
if $ct.ctx is not None:
    $cmd = CreateTypeCommand($ct.ctx)
else:
    $cmd = CreateRelationCommand($cr.ctx)
  }
  ;

create_type
  : K_TYPE
    (t=I_TYPE {$t=$t.text})
    '(' (tl=type_list) ')'
  ;

type_list returns [tds]
  : td1=type_decl {$tds = [$td1.ctx]}
    (',' (tdi=type_decl {$tds.append($tdi.ctx)}))*
  {return $tds}
  ;

prop_type : (T_INT | T_LONG | T_BOOL | T_SHORT
            | T_CHAR | T_FLOAT | T_DOUBLE | T_STRING)
          ;

type_decl
  : (n=I_NAME) ':' (t=prop_type)
  {return ($n.text, $t.text)}
  ;

create_relation
  : K_RELATION
    (r=(I_RELATION|I_TYPE) {$r.text.isupper()}? {$r=$r.text})
    ('(' (tl=type_list)? ')')?;

// DELETE command
delete_stmt returns [cmd]
  @init {$cmd = None}
  : K_DELETE ( dt=delete_type
             //| dr=delete_relation
             )
{
if $dt.ctx is not None:
    $cmd = DeleteTypeCommand($dt.ctx)
}
  ;

delete_type
  : K_TYPE (t=I_TYPE {$t=$t.text})
  ;

// SHOW command
show_stmt returns [cmd]
  @init {$cmd = None}
  : K_SHOW (K_TYPES {t = ShowCommand.ShowType.TYPES}
           | K_RELATIONS {t = ShowCommand.ShowType.RELATIONS})
  {$cmd = ShowCommand(t)}
  ;

// DESC command
desc_stmt returns [cmd]
  @init {$cmd = None}
  : K_DESC (K_TYPE (t=I_TYPE {$t=$t.text}))
  {$cmd = DescTypeCommand($t)}
  ;

// INSERT command
insert_stmt returns [cmd]
  @init {$cmd = None}
  : K_INSERT ( inode=insert_node
             | irel=insert_relation
             //| igraph=insert_graph
             )
  {
if $inode.ctx is not None:
    $cmd = InsertNodeCommand($inode.ctx)
if $irel.ctx is not None:
    $cmd = InsertRelationCommand($irel.ctx)
  }
  ;

insert_node returns [nodeprops]
  : K_NODE np1=node_with_props {$nodeprops = [$np1.ctx]}
    (',' (npi=node_with_props {$nodeprops.append($npi.ctx)}))*
  {return $nodeprops}
  ;

node_with_props
  : (t=I_TYPE {$t=$t.text})
    '(' (pl=prop_list) ')'
  ;

relation_with_props
  : '-' '['
    (rel=(I_RELATION|I_TYPE) {$rel.text.isupper()}? {$rel = $rel.text})
    ('(' (pl=prop_list) ')')?
    ']' '->'
  {return ($rel, $pl.ctx)}
  ;

prop_list returns [props]
  : p1=prop_value {$props = [$p1.ctx]}
    (',' (pi=prop_value {$props.append($pi.ctx)}))*
  {return $props}
  ;

prop_value
  : (v=Literal)
  {return $v.text}
  ;

insert_relation
  : K_RELATION (n1=node_query) (r=relation_with_props) (n2=node_query)
  {return ($r.ctx, $n1.ctx, $n2.ctx)}
  ;

// Literals
Literal : (StringLiteral | IntLiteral | BooleanLiteral) ;
IntLiteral : DIGIT+;
StringLiteral : '"' StringChars? '"' ;
BooleanLiteral : (T R U E | F A L S E) ;

// Keywords
K_MATCH : M A T C H ;
K_CREATE : C R E A T E ;
K_DELETE : D E L E T E ;
K_EXIT : E X I T ;
K_QUIT : Q U I T ;
K_SHOW : S H O W ;
K_DESC : D E S C ;
K_INSERT : I N S E R T ;

K_TYPE : T Y P E ;
K_RELATION : R E L A T I O N ;
K_NODE : N O D E ;
K_TYPES : T Y P E S ;
K_RELATIONS : R E L A T I O N S ;

K_WHERE : W H E R E ;
K_RETURN : R E T U R N;

K_AND : A N D ;
K_OR : O R ;

// Types
T_INT : I N T ;
T_LONG : L O N G ;
T_BOOL : B O O L ;
T_SHORT : S H O R T ;
T_CHAR : C H A R ;
T_FLOAT : F L O A T ;
T_DOUBLE : D O U B L E ;
T_STRING : S T R I N G ;

// Identifiers
I_NAME : LCASE (LCASE | DIGIT | OTHER_VALID)* ;
I_TYPE : UCASE LETTER*;
I_RELATION : UCASE (UCASE | OTHER_VALID)+ {self.text.isupper()}?;

// Other tokens
SPACES
  : [ \u000B\u000C\t\r\n] -> channel(HIDDEN)
  ;

BLOCK_COMMENT
  : '/*' .*? '*/' -> channel(HIDDEN)
  ;

LINE_COMMENT
  : '//' ~[\r\n]* -> channel(HIDDEN)
  ;

fragment OTHER_VALID : [_\-];
fragment DIGIT : [0-9];
fragment LETTER : [A-Za-z];
fragment UCASE : [A-Z];
fragment LCASE : [a-z];

fragment A : [aA];
fragment B : [bB];
fragment C : [cC];
fragment D : [dD];
fragment E : [eE];
fragment F : [fF];
fragment G : [gG];
fragment H : [hH];
fragment I : [iI];
fragment J : [jJ];
fragment K : [kK];
fragment L : [lL];
fragment M : [mM];
fragment N : [nN];
fragment O : [oO];
fragment P : [pP];
fragment Q : [qQ];
fragment R : [rR];
fragment S : [sS];
fragment T : [tT];
fragment U : [uU];
fragment V : [vV];
fragment W : [wW];
fragment X : [xX];
fragment Y : [yY];
fragment Z : [zZ];

fragment StringChars : StringChar+ ;
fragment StringChar : ~["\\] | EscapeSeq ;
fragment EscapeSeq : '\\' [btnfr"'\\] ;
