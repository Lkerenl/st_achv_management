import tornado.ioloop
import tornado.locks
import tornado.web
import asyncio
import aiopg

from tornado.options import define, options

# configure
import route
import appbase


async def main():
    tornado.options.parse_command_line()
    # dsn = "dbname={db_name}  user={db_user}  password={db_password} host={db_host} port={db_port}".format(
    #     db_name=options.db_database,
    #     db_user=options.db_user,
    #     db_password=options.db_password,
    #     db_host=options.db_host,
    #     db_port=options.db_port)
    # import pdb;pdb.set_trace()
    # async with aiopg.create_pool(dsn) as db:
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
