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
        # username = self.get_argument("username",None)
        # password = self.get_argument("password",None)
        identity = self.get_argument("identity",None)
        try:
            status = await self.queryone(
                    "select * from %s where "
                    "username=%s",
                    self.get_argument("identity",None),
                    self.get_argument("username",None))
        except NoResultError:
            self.write(json.dumps({"login":False,"message":"user not find."}))
            return
        if identity == "management":
            hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(status.mpwd))
            hashed_password = tornado.escape.to_unicode(hashed_password)
            if hashed_password == status.mpwd:
                self.write(json.dumps({"login":True,"message":""}))
                self.set_secure_cookie("user_id",str(status.mno))
                self.set_secure_cookie("access",identity)
            else:
                self.write(json.dumps({"login":False,"message":"incorrect password"}))
        elif identity == "teacher":
            hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(status.tpwd))
            hashed_password = tornado.escape.to_unicode(hashed_password)
            if hashed_password == status.tpwd:
                self.write(json.dumps({"login":True,"message":""}))
                self.set_secure_cookie("user_id",str(status.tno))
                self.set_secure_cookie("access",identity)
            else:
                self.write(json.dumps({"login":False,"message":"incorrect password"}))
        else:
            hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(status.spwd))
            hashed_password = tornado.escape.to_unicode(hashed_password)
            if hashed_password == status.spwd:
                self.write(json.dumps({"login":True,"message":""}))
                self.set_secure_cookie("user_id",str(status.sno))
                self.set_secure_cookie("access",identity)
            else:
                self.write(json.dumps({"login":False,"message":"incorrect password"}))
