grammar GQL;

parse : stmt_list EOF;

stmt_list returns [stmts]
  : s1=stmt {$stmts = [$s1.ctx]}
    (';' (si=stmt {$stmts.append($si.ctx)})? )*
  ;

stmt
  : (K_EXPLAIN)? ( c=match_stmt
                 | c=create_stmt
                 )
  ;

match_stmt
  : K_MATCH node_chain
  ;

node returns [node_data]
  : '('
    (nn=I_NAME)?
    ':'
    (nt=I_TYPE)
    ')'
  {
$node_data = { "name": $nn.text, "type": $nt.text }
  }
  ;

relation returns [relation_data]
  : '-' ((rn=I_NAME ':')? rel=I_RELATION) '->'
  {
$relation_data = { "name": $rn.text, "type": $rel.text[1:-1] }
  }
  ;

node_chain
  : node (relation node)*
  ;

create_stmt returns [c]
  : K_CREATE ( create_type
             | create_relation
             )
  ;

create_type
  : K_TYPE (I_TYPE) '(' type_list ')'
  ;

type_list
  : type_decl (',' type_decl)*
  ;

type_decl
  : I_NAME ':' ( T_INT | T_STR )
  ;

create_relation
  : K_RELATION I_RELATION I_TYPE I_TYPE;

K_EXPLAIN : E X P L A I N ;
K_MATCH : M A T C H ;
K_CREATE : C R E A T E ;
K_TYPE : T Y P E ;
K_RELATION : R E L A T I O N ;

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
