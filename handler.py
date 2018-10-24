#!/usr/bin/env python3
import tornado.web
import bcrypt
import json

import appbase
from appbase import NoResultError

class IndexHandler(appbase.BaseHandler):
    async def get(self):
        self.write("Index Page.")

class LoginHandler(appbase.BaseHandler):
    # async def get(self):
    #     self.write("Index Page.")
    async def post(self):
        username = self.get_argument("username",None)
        password = self.get_argument("password",None)
        identity = self.get_argument("identity",None)
        data = dict(
            name = username,
            user_id = None,
            access = [identity],
            avator = 'https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png',
            message = ""
        )
        if identity not in ["teacher","student","management"]:
            data['message'] = "identity wrong."
            self.write(json.dumps(data))
        try:
            status = await self.queryone("select * from " + identity + " where no=%s",(username,))

        except NoResultError:
            data['message'] = "not find user."
            self.write(json.dumps(data))
            return

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
                None,bcrypt.hashpw, tornado.escape.utf8(password),
                tornado.escape.utf8(status.password))
        hashed_password = tornado.escape.to_unicode(hashed_password)

        if hashed_password == status.password:
            data["token"] = username
            data['message']="success."
            data['user_id']=str(status.id)
            self.set_secure_cookie("user_id",str(status.id))
        else:
            data['message']="username or password wrong."

        self.write(json.dumps(data))

            # self.set_secure_cookie("access",identity)
