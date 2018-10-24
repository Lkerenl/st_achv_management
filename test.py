import asyncio
import aiopg
import tornado.util
dsn = 'dbname=tornado user=tornado password=qwe789456 host=127.0.0.1'


async def test_select():
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * from management where no=%s",('jwk',))
                ret = []
                async for row in cur:
                    ret.append(row)
                    print(row)
    print("ALL DONE")

def row_to_obj(row, cur):
    """sql row to object supporting dict and attribute access."""
    obj = tornado.util.ObjectDict()
    print(cur.description)
    # print(next(cur.fetchall()))
    for val, desc in zip(row, cur.description):
        obj[desc.name] = val
    return obj

async def execute(db, stmt, *args):
    """ execute sql statement
    called with `await self.execute(...)`
    """
    with (await db.cursor()) as cur:
        await cur.execute(stmt, args)

async def query(db, stmt, *args):
    """ quert for a list of results
    useage:
        results = await self.query(...)
    or
        for row in await self.query(...)
    """
    with (await db.cursor()) as cur:
        await cur.execute(stmt, args)
        # print("@@@@@@@@@@")
        return [row_to_obj(row, cur) for row in await cur.fetchall()]

async def queryone(stmt, *args):
    """ query for one result
    raise NoResultError if there are no results, or ValueError if there are
    more than one.
    """
    async with aiopg.create_pool(dsn) as db:
        result = await query(db, stmt, *args)
        # print(result)
        # import pdb;pdb.set_trace()
        if len(result) == 0:
            raise EOFError()
        elif len(result) > 1:
            raise ValueError("Expectecd 1 result, got %d" % len(result))
    return result[0]

loop = asyncio.get_event_loop()
loop.run_until_complete(queryone("select * from management where no=%s",("jwk",)))
