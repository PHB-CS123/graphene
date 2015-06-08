import random
import names
import itertools

# Global ids/names corresponding to the ids/names we create.
all_people = []
all_rels = []
# all_ids = []
# all_names = []

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

        # all_ids.append(i)
        # all_names.append(name)
        all_people.append({"name": name, "id": i, "age": age})
        # Print the node insert statement with the generated data
        yield "Person(%d, \"%s\", %d)" % (i, name, age)


def rel_data_generator(nodes, amount=50):
    """
    Relation generating function, generates relations with random data for
    the type:       RELATION KNOWS (num_years: int);
    """
    combos = tuple(itertools.permutations(nodes, 2))
    for left, right in random.sample(combos, amount):
        left_id = left.split('(')[1].split(',')[0]
        right_id = right.split('(')[1].split(',')[0]
        years_known = random.randrange(1, 10, 1)
        all_rels.append({"a": left_id, "b": right_id, "years_known": years_known})

        yield "Person(id=%s)-[KNOWS(%d)]->Person(id=%s)" % (
        left_id, years_known, right_id)


def update_age_generator(nodes, amount=50):
    """
    Generates update statements on ages.

    :param amount: number of update statements to generate
    """
    for id in random.sample(range(1, len(nodes) + 1), amount):
        new_age = random.randint(1, 71)
        yield 'UPDATE NODE Person(id=%d) SET age=%d;' % (
            id, new_age
        )

def update_name_generator(nodes, amount=50):
    """
    Generates update statements on names.

    :param amount: number of names to change.
    """
    for id in random.sample(range(1, len(nodes) + 1), amount):
        new_name = names.get_full_name()
        yield 'UPDATE NODE Person(id=%d) SET name="%s";' % (
            id, new_name
        )

def update_rel_generator(nodes, amount=50):
    combos = tuple(itertools.permutations(nodes, 2))
    for left, right in random.sample(combos, amount):
        left_id = left.split('(')[1].split(',')[0]
        right_id = right.split('(')[1].split(',')[0]
        years_known = random.randrange(1, 10, 1)
        yield "UPDATE RELATION Person(id=%s)-[KNOWS(%d)]->Person(id=%s)" % (
            left_id, years_known, right_id)

def sql_person_generator():
    for person in all_people:
        yield "(%s, %s, %s)" % (
            person["id"], person["name"], person["age"]
        )


if __name__ == '__main__':
    nodes = tuple(node_data_generator(500))
    print "CREATE TYPE Person (id: int, name: string, age: int);"
    print "INSERT NODE " + ", ".join(nodes) + ";"
    # print "CREATE RELATION KNOWS (num_years: int);"
    # print "INSERT RELATION " + ", ".join(rel_data_generator(nodes, 1750)) + ";"
    # print "\n".join(update_age_generator(nodes, 100))
    # print "\n".join(update_name_generator(nodes, 100))

    # print("DROP TABLE IF EXISTS person;")
    # print("DROP TABLE IF EXISTS knows;")
    #
    # print("CREATE TABLE person (id INTEGER AUTO_INCREMENT NOT NULL,"
    #       " name VARCHAR(50), age INTEGER);")
    # print("CREATE TABLE knows (a INTEGER, b INTEGER, years_known INTEGER);")
    # print("INSERT INTO person VALUES")
    # print(",".join(sql_person_generator()))
    # print(";")
    #
    # print("INSERT INTO knows VALUES")
