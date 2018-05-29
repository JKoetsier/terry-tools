from .functions import *

import sys


def transform_schema(filename):
    data = load_data_from_file(filename)
    data = remove_use_db(data)
    data = replace_sysname(data)
    data = remove_go_statements(data)
    data = remove_comments(data)
    data = remove_brackets(data)
    data = remove_set_lines(data)
    data = remove_create_properties(data)
    data = remove_clustered_keywords(data)
    data = remove_asc_primary_keys(data)
    data = remove_textimage_on(data)
    data = remove_index_include_columns(data)
    data = add_semicolons_remove_on_primary(data)

    data = replace_keywords(data)
    data = add_semicolons(data)

    data = remove_constraint_defs(data)

    return unduplicate_new_lines(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with filename parameter:")
        print("{} filename".format(sys.argv[0]))
        exit(1)

    print(transform_schema(sys.argv[1]))
