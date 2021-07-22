from django.db import connection


def get_row(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        if not len(cursor.description) == 1:
            raise Exception("The result column must be named 'value'")
        value = cursor.description[0].name
        if value != 'value':
            raise Exception(f"The result column must be named 'value' instead of '{value}'.")
        row = cursor.fetchone()

    return row[0]


def check_query(description, column_1, column_2):
    if not len(description) == 2:
        raise Exception(f"The result columns must be named '{column_1}' and '{column_2}'.")
    first = description[0].name
    second = description[1].name
    if first != column_1 or second != column_2:
        err_msg = f"The result columns must be named '{column_1}', '{column_2}' instead of '{first}', '{second}'."
        raise Exception(err_msg)


def execute_query(query, column_1, column_2, one=False):
    with connection.cursor() as cursor:
        cursor.execute(query)
        check_query(cursor.description, column_1, column_2)
        if one:
            res = cursor.fetchone()
        else:
            res = cursor.fetchall()

    return res
