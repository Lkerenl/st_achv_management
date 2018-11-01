import tornado.escape
import tornado.ioloop
import asyncio
import bcrypt
import json

async def encode(psd):
    hashed_psd = await tornado.ioloop.IOLoop.current().run_in_executor(
        None,bcrypt.hashpw,tornado.escape.utf8(psd),bcrypt.gensalt())
    print(tornado.escape.to_unicode(hashed_psd))
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(encode("123456"))
