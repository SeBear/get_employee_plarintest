import re
import json
from typing import Optional
import pymongo
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse

#To start rolling (uvicorn server): in venv
# uvicorn get_employee:employees_getter --reload

"""
----------------------------------------------------------------------------------------
CONNECT
----------------------------------------------------------------------------------------
"""

def connect_to_database(DEBUG = False):
    if DEBUG:
        conn = pymongo.MongoClient(
            "mongodb+srv://morisalle:c8W-ztX-uxD-Jb4@cluster0.khavi.mongodb.net/Cluster0?retryWrites=true&w=majority")
        with open("./employees.json", "r") as example:
            table = conn.db.workers
            table.drop()
            table.insert_many(json.load(example))
    else:
        conn = pymongo.MongoClient()
        pass
    # TODO: Conn to prod MongoDB
    return conn

"""
----------------------------------------------------------------------------------------
API
----------------------------------------------------------------------------------------
"""

class SQL_shield():
    """
    Class-helper to ensure string does not contain SQL-rq
    Класс проверяющий что строка не SQL-запрос
    """
    quotate_sql = re.compile(r"(?P<sql_special_symb>(;)|(WHERE)|(FROM)|(INSERT)|(INTO)|(BY)|(ORDER))", re.IGNORECASE)
    # List of special symbols and words to shield
    #TODO: Move to SQL_safe_str method.
    # Это должен быть метод класса SQL_safe_str
    def ensure_no_SQL_injection(self, string_to_check = None):
        if string_to_check is not None:
            #FIXME: Shielding with \ . Change if u need.
            # Экранируем \ .
            return  self.quotate_sql.sub("\\\g<sql_special_symb>\\", f"{string_to_check}")
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
API
----------------------------------------------------------------------------------------
"""


employees_getter = FastAPI()

@employees_getter.get("/")
async def root():
    #TODO: Ensure we have INDEX page => delete following redirect;
    # Убедись, что есть главная странмца => Убери редирект.
    return RedirectResponse("/employees")


@employees_getter.get("/employees")
async def get_empolyees_by(name: Optional[str] = None,
                           email: Optional[str] = None,
                           age: Optional[int] = None,
                           company: Optional[str] = None,
                           join_date: Optional[str] = None,
                           job_title: Optional[str] = None,
                           gender: Optional[str] = None,
                           salary: Optional[int] = None):
    q = {'name': name, 'email': email,'age':age,'company':company,'join_date':join_date,'job_title':job_title,'gender':gender,'salary':salary}
    query = {}
    for field in q:
        if q[field] is not None:
            query.update({f"{field}": f"{q[field]}"})

    conn = connect_to_database(DEBUG = True)
    result = []
    try:
        for person_fits_query in conn.db.workers.find(query):
            print(person_fits_query)
            result.append(person_fits_query)

    except ValueError:   #TODO: Откуда?
        pass
    return result




