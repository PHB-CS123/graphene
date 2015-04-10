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
    | c=create_stmt
    | c=exit_stmt
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
  : K_MATCH (nc=node_chain)
  {$cmd = MatchCommand($nc.ctx)}
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

type_decl
  : (n=I_NAME) ':' (t=( T_INT | T_STR ))
  {return ($n.text, $t.text)}
  ;

create_relation
  : K_RELATION
    (r=(I_RELATION|I_TYPE) {$r.text.isupper()}? {$r=$r.text})
    (t1=I_TYPE {$t1=$t1.text})
    (t2=I_TYPE {$t2=$t2.text});

// Keywords
K_MATCH : M A T C H ;
K_CREATE : C R E A T E ;
K_TYPE : T Y P E ;
K_RELATION : R E L A T I O N ;
K_EXIT : E X I T ;
K_QUIT : Q U I T ;

// Types
T_INT : I N T ;
T_STR : S T R ;

// Identifiers
I_NAME : LCASE (LCASE | DIGIT | OTHER_VALID)* ;
I_TYPE : UCASE LETTER*;
I_RELATION : UCASE+ {self.text.isupper()}?;

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
