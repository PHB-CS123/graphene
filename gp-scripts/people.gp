CREATE TYPE Person (name : string, age : int);
INSERT NODE Person ("cody", 21);
INSERT NODE Person ("david", 22);
CREATE RELATION R (a : int);
INSERT RELATION Person(name="cody")-[R(a=5)]->Person(name="david");
MATCH (p1:Person)-[R]->(p2:Person)
