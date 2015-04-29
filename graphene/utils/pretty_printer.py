import sys

class PrettyPrinter:
    @staticmethod
    def print_list(lst, header=None, output=sys.stdout):
        max_len = max(map(len, lst))

        str_list = []

        if header is not None:
            max_len = max(max_len, len(header))
            str_list.append((max_len + 4) * "-")
            str_list.append("| " + header.upper() + (max_len - len(header)) * " " + " |")
        str_list.append((max_len + 4) * "-")
        for o in lst:
            str_list.append("| " + o + (max_len - len(o)) * " " + " |")
        str_list.append((max_len + 4) * "-")

        output.write("\n".join(str_list) + "\n")

    @staticmethod
    def print_table(table, header=None, output=sys.stdout):
        data = zip(*table)
        maxes = map(lambda l: max(map(lambda v: len(str(v)), l)), data)
        width = sum(m + 2 for m in maxes) + 2 + (len(maxes) - 1)
        if header is not None:
            maxes = [max(m, len(str(header[i] or ""))) for i, m in enumerate(maxes)]
            width = sum(m + 2 for m in maxes) + 2 + (len(maxes) - 1)
            output.write(width * "-" + "\n")
            output.write("|%s|" % "|".join(" %s%s " % (v.upper(), (maxes[i] - len(str(v))) * " ") \
                   for i, v in enumerate(header)) + "\n")
        output.write(width * "-" + "\n")
        for row in table:
            output.write("|%s|" % "|".join(" %s%s " % (v, (maxes[i] - len(str(v))) * " ") \
                   for i, v in enumerate(row)) + "\n")
        output.write(width * "-" + "\n")
