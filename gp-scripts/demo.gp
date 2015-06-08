help
help insert
help create

SHOW TYPES;
SHOW RELATIONS;

MATCH (p:Person);
MATCH (p:Person) WHERE id < 15;
MATCH (p:Person) WHERE id < 15 RETURN name;
MATCH (p:Person) WHERE id < 15 OR id > 490;
MATCH (p:Person) WHERE id < 15 AND id > 490;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person);
MATCH (p1:Person)-[KNOWS]->(p1:Person); // error
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100 AND p1.age < p2.age;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100 AND p1.age < p2.age RETURN p1.name, p2.name;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100 AND p1.age < p2.age RETURN name; // error
MATCH (p1:Person)-[KNOWS]->(Person)-[KNOWS]->(p2:Person);

MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id = 11;
UPDATE RELATION Person(id = 11)-KNOWS SET num_years = 42;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id = 11;
DELETE RELATION Person(id = 11)-KNOWS;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id = 11;

MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id = 22;
DELETE NODE Person(id = 22);
MATCH (Person) WHERE id = 22;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id = 22;

CREATE TYPE T(a: int[]);
INSERT NODE T(3); // error
INSERT NODE T([true, false]); // error
INSERT NODE T([true, 5]); // error
INSERT NODE T([1,2]), T([]);
MATCH (T);
UPDATE NODE T(a=[1,2]) SET a = [1,2,3];
MATCH (T);
DELETE NODE T(a=[1,2,3]);
MATCH (T);
DROP TYPE T;
MATCH (T); // error
