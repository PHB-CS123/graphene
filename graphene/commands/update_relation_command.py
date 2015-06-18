from relation_iterator import *
from graphene.errors import TypeMismatchException, NonexistentPropertyException
from graphene.storage import Property
from graphene.utils.conversion import TypeConversion

class UpdateRelationCommand(RelationIterator):
    """
    Used to update individual relations from the database.
    """
    def __init__(self, rel_type, query_chain, left_node, right_node, update):
        # Update dictionary
        self.update = update
        super(UpdateRelationCommand, self).__init__(rel_type, query_chain,
                                                    left_node, right_node)

    def execute(self, storage_manager, timer=None):
        """
        Update the relationship properties from the query

        :param storage_manager: Storage manager to obtain data from
        :type storage_manager: StorageManager
        :return:
        :rtype:
        """
        # Get relation iterator
        rel_iter = super(UpdateRelationCommand, self).execute(storage_manager)
        # Check Schema Types
        rel_type, schema = storage_manager.get_relationship_data(self.rel_type)
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
                err = "Property name `%s` does not exist." % u_name
                raise NonexistentPropertyException(err)
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
        # Update relation properties yielded by generator
        storage_manager.update_relations(rel_iter, update_dict)
