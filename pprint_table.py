import locale, sys # for pretty printing table

# From http://ginstrom.com/scribbles/2007/09/04/pretty-printing-a-table-in-python/
def format_num(num):
    """Format a number according to given places.
    Adds commas, etc."""
    try:
        return locale.format("%.*f", num, True)
    except (ValueError, TypeError):
        return str(num)

def get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(format_num(row[index])) for row in table])

def pprint_table(out, table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """
    col_paddings = []
    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))
    for row in table:
        for i in range(len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
            print >> out, col,
        print >> out
