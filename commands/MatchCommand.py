class MatchCommand:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        lst = []
        for chain in self.data:
            ct = chain["chain_type"]
            t = chain["type"]
            n = chain["name"]
            if ct == "rel":
                lst.append("\tVIA: %s%s" % (t, ("" if n is None else " as %s" % n)))
            else:
                lst.append("\tNODE: %s%s" % (t, ("" if n is None else " as %s" % n)))
        return "[Match\n%s\n]" % "\n".join(lst)
