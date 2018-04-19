from functions import *


def extract_vars(query):
    vardecls = re.findall(r'(?P<varname>@(\w*?)\d+)=(?P<value>.*?)(,|$)', query)
    vars = {}

    for vardecl in vardecls:
        vars[vardecl[0]] = re.sub(r"^N'", "'", vardecl[2])  # Remove N prefix if present
    return vars


def replace_vars(query):
    vars = extract_vars(query)
    query = re.sub(r"exec sp_executesql N'(?P<query>.*?)',N'(.*)", '\g<query>', query, flags=re.M | re.S)

    for varname, value in vars.items():
        query = re.sub(r'' + varname + '', value, query, flags=re.M | re.I)
    return query


def remove_parentheses(query):
    return re.sub(r'WHERE\s+\(\((?P<inner>.*?)\)\)\)\s+AND', 'WHERE (\g<inner>)) AND', query)


def replace_double_single_quotes(query):
    return re.sub(r"''(?P<inner>[^']*?)''", "'\g<inner>'", query, flags=re.M)


def transform_query(query):
    query = remove_brackets(query)
    query = replace_vars(query)
    query = remove_parentheses(query)
    query = replace_double_single_quotes(query)
    query = query.strip() + ";"

    return query


def is_valid_query(query):
    query = query.lower()

    return not query.startswith("declare") and \
           not query.startswith(";with") and \
           not query.startswith("create") and \
           not query.startswith("if exists (select") and \
           not query.startswith("insert") and \
           not query.startswith("select convert(") and \
           not query.startswith("select @@") and \
           "create table" not in query


def transform_workload(filename):
    data = load_data_from_file(filename)

    queries = re.split(r'^go$', data, flags=re.M)

    # First do global filtering
    queries = [q for q in queries if "select" in q.lower()]

    # Transform and do final filtering
    return [query for query in (transform_query(q) for q in queries) if is_valid_query(query)]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call program with filename parameter:")
        print("{} filename".format(sys.argv[0]))
        exit(1)

    workload = transform_workload(sys.argv[1])

    for query in workload:
        print(query)
