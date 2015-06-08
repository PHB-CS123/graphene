import random
import names
import itertools

def node_data_generator(amount=100):
  """
  Node generating function, generates nodes with random data for
  the type:        TYPE Person (id: int, name: string, age: int);
  Has the format:  INSERT NODE Person (1, "cody", 21);
  """
  for i in range(1, amount + 1):
    # Get a random age between 1 and 70 years
    age = random.randrange(1, 71, 1)
    # Get a random name
    name = names.get_full_name()
    # Print the node insert statement with the generated data
    yield "Person(%d, \"%s\", %d)" % (i, name, age)

def rel_data_generator(nodes, amount=50):
  """
  Relation generating function, generates relations with random data for
  the type:       RELATION KNOWS (num_years: int);
  """
  combos = tuple(itertools.permutations(nodes, 2))
  for left, right in random.sample(combos, len(nodes) / 2):
    left_id = left.split('(')[1].split(',')[0]
    right_id = right.split('(')[1].split(',')[0]
    years_known = random.randrange(1, 10, 1)
    yield "Person(id=%s)-[KNOWS(%d)]->Person(id=%s)" % (left_id, years_known, right_id)

if __name__ == '__main__':
  nodes = tuple(node_data_generator(100))
  print "CREATE TYPE Person (id: int, name: string, age: int);"
  print "INSERT NODE " + ", ".join(nodes) + ";"
  print "CREATE RELATION KNOWS (num_years: int);"
  print "INSERT RELATION " + ", ".join(rel_data_generator(nodes)) + ";"
