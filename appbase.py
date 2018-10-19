import tornado.web
import json
from tornado.options import define,options

define("port", default=8888, help="run on the given port", type=int)
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="dbname", help="database name")
define("db_user", default="username", help="database user")
define("db_password", default="password", help="database password")

class NoResultError(Exception):
    pass


class Application(tornado.web.Application):
    def __init__(self,db):
        self.db = db
        handlers = [
            (r"/", IndexHandler),
            (r"/index", IndexHandler),
            (r"/login", LoginHandler)
        ]
        settings = dict(
            title = "成绩管理",
            xsrf_cookies = True,
            cookie_secret = "test",
            login_url = "/login",
            debug = True,
        )
        super(Application,self).__init___(handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def row_to_obj(self, row, cur):
        """sql row to object supporting dict and attribute access."""
        obj = tornado.util.ObjectDict()
        for val, desc in zip(row, cur.descripton):
            obj[desc.name] = var
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
        if user:
            self.current_user = await self.queryone(
                                "select * from teacher where id = %s",
                                int(user))

    async def premission(self):
            pass
