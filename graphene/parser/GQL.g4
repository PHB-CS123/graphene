grammar GQL;

@header {
from graphene.commands import *
}

parse : stmt_list EOF;

stmt_list returns [stmts]
  : s1=stmt {$stmts = [$s1.ctx]}
    (';' (si=stmt {$stmts.append($si.ctx)})? )*
  ;

stmt
  : (K_EXPLAIN)? ( c=match_stmt
                 | c=create_stmt
                 | c=exit_stmt
                 )
  ;

exit_stmt returns [cmd]
  : (K_EXIT | K_QUIT)
  {$cmd = ExitCommand()}
  ;

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

node returns [node_data]
  : '('
    (nn=I_NAME)?
    ':'
    (nt=I_TYPE)
    ')'
  {
return { "chain_type": "node", "name": $nn.text, "type": $nt.text }
  }
  ;

relation returns [relation_data]
  : '-' ((rn=I_NAME ':')? rel=I_RELATION) '->'
  {
return { "chain_type": "rel", "name": $rn.text, "type": $rel.text[1:-1] }
  }
  ;

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
    (r=I_RELATION {$r=$r.text[1:-1]})
    (t1=I_TYPE {$t1=$t1.text})
    (t2=I_TYPE {$t2=$t2.text});

K_EXPLAIN : E X P L A I N ;
K_MATCH : M A T C H ;
K_CREATE : C R E A T E ;
K_TYPE : T Y P E ;
K_RELATION : R E L A T I O N ;
K_EXIT : E X I T ;
K_QUIT : Q U I T ;

T_INT : I N T ;
T_STR : S T R ;

I_NAME : LCASE (LCASE | DIGIT)* ;
I_TYPE : UCASE LCASE* ;
I_RELATION : '(' UCASE+ ')' ;

SPACES
  : [ \u000B\u000C\t\r\n] -> skip
  ;

BLOCK_COMMENT
  : '/*' .*? '*/' -> skip
  ;

LINE_COMMENT
  : '//' ~[\r\n]* -> skip
  ;

UNEXPECTED_CHAR
  : .
  ;

fragment DIGIT : [0-9];
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
