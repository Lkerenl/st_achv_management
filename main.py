import tornado.ioloop
import tornado.web
import aiopg

from tornado.options import define,options

#configure
import route
import appbase

def main():
    tornado.options.parse_command_line()
    async with aiopg.create_pool(
            host=options.db_host,
            port=options.db_port,
            user=options.db_user,
            password=options.db_password,
            dbname=options.db_database) as db:
        await appbase.maybe_create_tables(db)
        app = appbase.Application(db, route.route_handler)
        app.listen(options.port)

        # In this demo the server will simply run until interrupted
        # with Ctrl-C, but if you want to shut down more gracefully,
        # call shutdown_event.set().

        shutdown_event = tornado.locks.Event()
        await shutdown_event.wait()

if __name__ == '__main__':
    tornado.ioloop.IOLoop.current().run_sync(main)
