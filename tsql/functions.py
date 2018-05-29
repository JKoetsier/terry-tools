import re


def load_data_from_file(filename):
    with open(filename, "r") as file:
        return "".join(file.readlines())


def remove_use_db(data):
    return re.sub(r'^USE (.*)', "", data, flags=re.M)


def remove_comments(data):
    return re.sub(r'/\*\*(.*?)\*\*/', "", data, flags=re.M | re.S)


def remove_go_statements(data):
    return re.sub(r'^GO', "", data, flags=re.M)


def remove_brackets(data):
    return re.sub(r'\[(?P<inner>.*?)\]', "\g<inner>", data)


def remove_set_lines(data):
    return re.sub(r'^SET (.*)', "", data, flags=re.M)

def replace_sysname(data):
    return re.sub('\[sysname\]', "[nvarchar(128)]", data)

def unduplicate_new_lines(data):
    # Remove all new lines in beginning of file
    data = re.sub(r'^(\n)*', "", data)

    # Remove all unnecessary new lines further down in the file
    return re.sub(r'(\n){2,}', "\n\n", data, flags=re.M)


def add_semicolons_remove_on_primary(data):
    return re.sub(r'\)(.*?)ON(.*?)PRIMARY\s*?CREATE', ");\n\nCREATE", data, flags=re.M)


def remove_asc_primary_keys(data):
    (data, n) = re.subn(r'PRIMARY KEY(?P<before>(.*?)\(\s*\w*?\s*)ASC(?P<after>.*?\))',
                        "PRIMARY KEY\g<before>\g<after>", data, flags=re.M | re.S)

    # Do a couple of times, max 20
    for i in range(0, 20):
        (data, n) = re.subn(r'PRIMARY KEY(?P<before>(.*?)\(.*?,\s*?\w*?\s*)ASC(?P<after>.*?\))',
                            "PRIMARY KEY\g<before>\g<after>", data, flags=re.M | re.S)
        if n == 0:
            break

    # Same, but for Unique keyword. Combined regex is too slow
    (data, n) = re.subn(r'UNIQUE(?P<before>(.*?)\(\s*\w*?\s*)ASC(?P<after>.*?\))', "UNIQUE\g<before>\g<after>", data,
                        flags=re.M | re.S)

    for i in range(0, 20):
        (data, n) = re.subn(r'UNIQUE(?P<before>(.*?)\(.*?,\s*?\w*?\s*)ASC(?P<after>.*?\))', "UNIQUE\g<before>\g<after>",
                            data, flags=re.M | re.S)
        if n == 0:
            break

    # Nearly the same as above
    (data, n) = re.subn(r'(?P<before>CREATE\s+(UNIQUE\s+)?INDEX(.*?)\(\s*\w*?\s*)ASC(?P<after>.*?\))',
                        "\g<before>\g<after>", data, flags=re.M | re.S)
    for i in range(0, 20):
        (data, n) = re.subn(r'(?P<before>CREATE\s+(UNIQUE\s+)?INDEX(.*?)\(.*?,\s*\w*?\s*)ASC(?P<after>.*?\))',
                            "\g<before>\g<after>", data, flags=re.M | re.S)
        if n == 0:
            break
    return data


def remove_create_properties(data):
    return re.sub(r'WITH\s*?\((.*?)\)\s*?ON PRIMARY',
                  "", data, flags=re.M | re.S)


def remove_clustered_keywords(data):
    return re.sub(r'(NON)?CLUSTERED', "", data, flags=re.M)


def remove_textimage_on(data):
    return re.sub(r'TEXTIMAGE_ON', "", data, flags=re.M)


def add_semicolons(data):
    data = re.sub('(?P<before>[)|\w])\s*(?P<keyword>CREATE|ALTER)', '\g<before>;\n\n\g<keyword>', data, flags=re.M)
    data = re.sub('(?P<all>(.*))(?P<lastchar>\w)\s*', '\g<all>\g<lastchar>;', data, flags=re.M | re.S)

    return data


def replace_keywords(data):
    return re.sub(r'(?P<ws>\s)(?P<keyword>(Value|Date|Key))', '\g<ws>Mod\g<keyword>', data, flags=re.M)


def remove_index_include_columns(data):
    return re.sub('(?P<create_part>CREATE\s+(UNIQUE\s+)?INDEX(.*?)\))\s+INCLUDE(.*?)\)', '\g<create_part>', data,
                  flags=re.M | re.S)


def remove_constraint_defs(data):
    return re.sub(r'ALTER TABLE(.*?);', "", data, flags=re.M | re.S)
