class ProjectStream:
    def __init__(self, return_chain, schema, results):
        self.rc = return_chain
        self.schema = schema
        self.results = results

        self.schema_names = []

        self.indexes = self.gen_indexes()

    def gen_indexes(self):
        if len(self.rc) == 0:
            return None
        indexes = []
        schema_names = [name for name, ttype in self.schema]
        schema_base_names = [name.split(".")[-1] for name, ttype in self.schema]
        for r in self.rc:
            ident, name = r
            # If there is an identifier given (e.g. `MATCH (a:A)`), then we
            # check that if one was given with the return query that it
            # matches the one we are looking at with the current schema.
            # That is, if our selection is `MATCH (a:A)`, where A has fields
            # b or c, then `RETURN b, c` and `RETURN a.b, a.c` both work and
            # do the same thing, but `RETURN a` and `RETURN t.b` do not.
            # if (ident == alias or ident is None) and name in schema_names:
            #     indexes.append(schema_names.index(name))
            if ident is None:
                if schema_base_names.count(name) > 1:
                    raise Exception("Property name `%s` is ambiguous." % name)
                elif name not in schema_base_names:
                    raise Exception("Property name `%s` does not exist." % name)
                else:
                    indexes.append(schema_base_names.index(name))
                    self.schema_names.append(name)
            else:
                key = "%s.%s" % r
                if key not in schema_names:
                    raise Exception("Property name `%s` does not exist." % key)
                else:
                    indexes.append(schema_names.index(key))
                    self.schema_names.append(key)
        return indexes

    def __iter__(self):
        for result in self.results:
            if self.indexes is not None:
                yield map(lambda i: result[i], self.indexes)
            else:
                yield result
