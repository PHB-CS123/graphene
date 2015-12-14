MATCH (Person);
MATCH (Human);
MATCH (p1:Person)-[k:KNOWS]->(p2:Person);
MATCH (p1:Person)-[r:REMEMBERS]->(p2:Person);
MATCH (p1:Human)-[k:KNOWS]->(p2:Human);
MATCH (p1:Human)-[r:REMEMBERS]->(p2:Human);