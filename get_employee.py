import json
import re
from pymongo import MongoClient
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

"""
----------------------------------------------------------------------------------------
DATATYPES
----------------------------------------------------------------------------------------
"""


class SQL_shield():
    """
    Class-helper to ensure string does not contain SQL-rq
    Класс проверяющий что строка не SQL-запрос
    """
    sql_signif_pattern = re.compile(r"(?P<sql_significant>(;)|(WHERE)|(FROM)|(INSERT)|(INTO)|(BY)|(ORDER))",
                                    re.IGNORECASE)

    # List of special symbols and words to shield
    # TODO: Move to SQL_safe_str method.
    # Это должен быть метод класса SQL_safe_str
    def ensure_no_SQL_injection(self, string_to_check = None):
        if string_to_check is not None:
            # Shielding with \ . Change if u need.
            # Экранируем \ .
            shield = "\\"
            return self.sql_signif_pattern.sub(rf"{shield}\g<sql_significant>", f"{string_to_check}")
        else:
            return ''


class SQL_safe_str(str, SQL_shield):
    """
    Redef str init to fix if SQL
    """

    def __init__(self, string):
        string = super(SQL_shield).ensure_no_SQL_injection(string)
        super(str).__init__(string)


"""
----------------------------------------------------------------------------------------
CONNECT
----------------------------------------------------------------------------------------
"""


# To start rolling (uvicorn server): in venv
# uvicorn get_employee:employees_getter --reload
def connect_to_database(DEBUG = False):
    if DEBUG:
        conn = MongoClient(
            "mongodb+srv://morisalle:c8W-ztX-uxD-Jb4@cluster0.khavi.mongodb.net/Cluster0?retryWrites=true&w=majority")
        with open("./employees.json", "r") as example:
            table = conn.db.workers
            table.drop()
            table.insert_many(json.load(example))
    else:
        # TODO: CHANGE_ON_PROD
        # Ensure to connect prod db
        # Подключиться к рабочей базе

        conn = MongoClient()
        pass
    return conn


"""
----------------------------------------------------------------------------------------
API
----------------------------------------------------------------------------------------
"""

employees_getter = FastAPI()


@employees_getter.get("/")
async def root():
    # TODO: CHANGE_ON_PROD
    # Ensure we have INDEX page => delete following redirect;
    # Убедись, что есть главная странмца => Убери редирект.
    return RedirectResponse("/employees")


@employees_getter.get("/employees")
# TODO: Add format checks
# Добавить проверку формата
async def get_empolyees_by(name: Optional[SQL_safe_str] = None,
                           email: Optional[SQL_safe_str] = None,
                           age: Optional[int] = None,
                           company: Optional[SQL_safe_str] = None,
                           join_date: Optional[SQL_safe_str] = None,
                           job_title: Optional[SQL_safe_str] = None,
                           gender: Optional[SQL_safe_str] = None,
                           salary: Optional[int] = None):
    """
    Turn to json
    Delete meaningless def_values
    Start connection
    Find what fits request
    :return: JSON
    """
    json_query_template = {'name': name,
                           'email': email,
                           'age': age,
                           'company': company,
                           'join_date': join_date,
                           'job_title': job_title,
                           'gender': gender,
                           'salary': salary
                           }

    current_query = {}
    for key, value in json_query_template.items():
        if json_query_template[key] is not None:
            current_query.update({f"{key}": value})  # Exclude NONEs

    conn = connect_to_database(DEBUG = True)

    data_response = []
    for person_fits_query in conn.db.workers.find(current_query, {'_id': 0}):
        data_response.append(person_fits_query)

    return data_response
