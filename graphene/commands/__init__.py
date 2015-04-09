## This comes from http://stackoverflow.com/a/6074997/28429
# The purpose is to load all the commands into this one module so that we don't
# have to manually add them.

# NOTE: The function name starts with an underscore so it doesn't get deleted by
# itself
def _load_modules(attr_filter=None):
    import os

    curdir = os.path.dirname(__file__)
    imports = [os.path.splitext(fname)[0] for fname in os.listdir(curdir) if fname.endswith(".py")]

    pubattrs = {}
    for mod_name in imports:
        mod = __import__(mod_name, globals(), locals(), ['*'], -1)

        for attr in mod.__dict__:
            if not attr.startswith('_') and (not attr_filter or attr_filter(mod_name, attr)):
                pubattrs[attr] = getattr(mod, attr)

    # Restore the global namespace to it's initial state
    for var in globals().copy():
        if not var.startswith('_'):
            del globals()[var]

    # Update the global namespace with the specific items we want
    globals().update(pubattrs)

_load_modules(attr_filter=lambda mod, attr: True if attr.endswith("Command") else False)
del _load_modules # Keep the namespace clean
