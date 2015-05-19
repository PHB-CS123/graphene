import random
import names

def node_data_generator(amount=100):
  """
  Node generating function, generates nodes with random data for
  the type:        TYPE Person (name: string, age: int);
  Has the format:  INSERT NODE Person ("cody", 21);
  """
  for i in range(0, amount):
    # Get a random age between 1 and 70 years
    age = random.randrange(1, 71, 1)
    # Get a random name
    name = names.get_full_name()
    # Print the node insert statement with the generated data
    print("INSERT NODE Person (\"%s\", %d);" %(name, age))


