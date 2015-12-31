MATCH (Person) WHERE id = 22;
MATCH (p:Person) WHERE id < 15;
MATCH (p:Person) WHERE id < 15 RETURN name;
MATCH (p:Person) WHERE id < 15 OR id > 990;
MATCH (p:Person) WHERE id < 15 AND id > 990;
MATCH (Person);
MATCH (Human);

MATCH (p1:Person)-[k:KNOWS]->(p2:Person);
MATCH (p1:Person)-[r:REMEMBERS]->(p2:Person);
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id = 22;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100 AND p1.age < p2.age;
MATCH (p1:Person)-[k:KNOWS]->(p2:Person) WHERE p1.id < 100 AND p1.age < p2.age RETURN p1.name, p2.name;
MATCH (p1:Person)-[KNOWS]->(Person)-[KNOWS]->(p2:Person);
MATCH (p1:Human)-[k:KNOWS]->(p2:Human);
MATCH (p1:Human)-[r:REMEMBERS]->(p2:Human);