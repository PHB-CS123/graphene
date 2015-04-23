import sys

class PrettyPrinter:
    @staticmethod
    def print_list(lst, header=None, output=sys.stdout):
        max_len = max(map(len, lst))

        str_list = []

        if header is not None:
            str_list.append((max_len + 4) * "-")
            str_list.append("| " + header.upper() + (max_len - len(header)) * " " + " |")
        str_list.append((max_len + 4) * "-")
        for o in lst:
            str_list.append("| " + o + (max_len - len(o)) * " " + " |")
        str_list.append((max_len + 4) * "-")

        output.write("\n".join(str_list) + "\n")
