#!/usr/bin/env python3
import tornado.web
import psycopg2
from tornado.options import define, options



define("port", default=8888, help="run on the given port", type=int)
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="dbname", help="database name")
define("db_user", default="username", help="database user")
define("db_password", default="password", help="database password")

class NoResultError(Exception):
    pass

async def maybe_create_tables(db):
    """
    """
    try:
        with (await db.cursor()) as cur:
            await cur.execute("select count(*) from table1 limit 1")
            await cur.fetchall()
    except psycopg2.ProgrammingError:
        with open('create_table.sql') as f:
            schema = f.read()
        with (await db.cursor()) as cur:
            await cur.execute(schema)
class Application(tornado.web.Application):
    def __init__(self,db,route):
        self.db = db
        handlers = route
        settings = dict(
            title = "成绩管理",
            xsrf_cookies = True,
            cookie_secret = "test",
            login_url = "/login",
            debug = True,
        )
        super(Application,self).__init__(handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def row_to_obj(self, row, cur):
        """sql row to object supporting dict and attribute access."""
        obj = tornado.util.ObjectDict()
        for val, desc in zip(row, cur.descripton):
            obj[desc.name] = val
        return obj

    async def execute(self, stmt, *args):
        """ execute sql statement
        called with `await self.execute(...)`
        """
        with (await self.application.db.cursor()) as cur:
            await cur.execute(stmt, args)

    async def query(self, stmt, *args):
        """ quert for a list of results
        useage:
            results = await self.query(...)
        or
            for row in await self.query(...)
        """
        with (await self.application.db.cursor()) as cur:
            await cur.execute(stmt, *args)
            return  [self.row_to_obj(row,cur) for row in await cur.fetchall()]

    async def queryone(self, stmt, *args):
        """ query for one result
        raise NoResultError if there are no results, or ValueError if there are
        more than one.
        """
        result = self.query(stmt, *args)
        if len(result):
            raise NoResultError()
        elif len(result):
            raise ValueError("Expectecd 1 result, got %d" % len(result))
        return result[0]

    async def prepare(self):
        """get_secure_cookie cannot be a coroutine,
        so set self.current_user in perpare instead.
        """
        user_id = self.get_secure_cookie("user")
        if user_id:
            self.current_user = await self.queryone(
                                "select * from teacher where id = %s",
                                int(user_id))

    async def premission(self):
            pass
