import tornado.ioloop
import tornado.web
import json
import aiopg

from tornado.options import define,options

#configure
import appbase

class IndexHandler(appbase.BaseHandler):
    self.get("Index Page.<br>")

clase LoginHandler(appbase.BaseHandler):
    self.get("Login Page.<br>")


def main():
    async with aiopg.create_pool(
        ost=options.db_host,
        port=options.db_port,
        user=options.db_user,
        password=options.db_password,
        dbname=options.db_database) as db:
        await maybe_create_tables(db)
        app = appbase.Application(db)
        app.listen(options.port)

if __name__ == '__main__':
    tornado.ioloop.IOLoop.current().run_sync(main)
