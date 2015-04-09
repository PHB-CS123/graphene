class MatchCommand:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.data]
        return "[Match\n%s\n]" % "\n".join(lst)
