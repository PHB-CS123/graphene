import logging

from graphene.commands.command import Command
from graphene.expressions.match_node import MatchNode
from graphene.query.planner import QueryPlanner
from graphene.utils.conversion import TypeConversion
from graphene.errors import TypeMismatchException, NonexistentPropertyException
from graphene.storage import Property


class UpdateNodeCommand(Command):
    """
    Used to update nodes from the database
    """
    def __init__(self, data):
        self.node_type = data.t
        self.qc = data.q
        self.update = data.u

        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self, storage_manager, timer=None):
        """
        Checks that the given update values are valid, and converts the given
        values into properties that can be stored. Then performs update.

        :param storage_manager: Manager to perform update from
        :type storage_manager: StorageManager
        :return: Nothing
        :rtype: None
        """
        # Check Schema Types
        node_type, schema = storage_manager.get_node_data(self.node_type)
        # The first part of a tuple in the schema list is the type-type itself
        # which we don't have to worry about; the second is the name of the
        # property, and the third is the type, so just taking the last two
        # and converting to a dict gives us a dict {name: type}.
        schema_dict = dict(s[1:] for s in schema)
        # Get the indices of each property
        index_dict = dict((s[1], i) for i, s in enumerate(schema))
        # This list will contain all the new values for properties with the
        # given indices.
        update_dict = {}
        for u_name, u_value in self.update.items():
            if u_name not in schema_dict:
                msg = "Property name `%s` does not exist." % u_name
                raise NonexistentPropertyException(msg)
            prop_type = schema_dict[u_name]
            if u_value == "[]":
                # Empty array, so we just have to check that the expected
                # type is some time of array
                if prop_type.value < Property.PropertyType.intArray.value:
                    err = "Got empty array, but expected value of type %s " \
                          "for property '%s'." % (prop_type, u_name)
                    raise TypeMismatchException(err)
                conv_value = []
            else:
                u_type = TypeConversion.get_type_type_of_string(u_value)
                if u_type != prop_type:
                    err = "Got value of type %s, but expected value of type " \
                          "%s for property '%s'." % (u_type, prop_type, u_name)
                    raise TypeMismatchException(err)
                # Convert value and add to list
                conv_value = TypeConversion.convert_to_value(u_value, prop_type)
            # Create a key with the index and converted value
            update_dict[index_dict[u_name]] = conv_value

        planner = QueryPlanner(storage_manager)
        # Iterate over nodes using the planner's helper method for convenience
        iter_tree = planner.get_iter_tree([MatchNode(None, self.node_type)],
                                          self.qc)

        storage_manager.update_nodes(iter_tree, update_dict)
