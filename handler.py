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
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()

    async def get(self):
        self.write("Index Page.")
    async def post(self):
        self.set_allow_origin()
        login_info = json.loads(self.request.body)
        login_info = tornado.util.ObjectDict(login_info)

        username = login_info.userName
        password = login_info.password
        identity = login_info.identity

        data = dict(
            token = None,
            message = "success"
        )
        if identity not in ["teacher", "student", "management"]:
            self.write("identity wrong.")
            self.finish()
            return
        try:
            status = await self.queryone("select * from " + identity + " where no=%s", username)
        except NoResultError:
            self.write("not user fond.")
            return

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
                None,bcrypt.hashpw, tornado.escape.utf8(password),
                tornado.escape.utf8(status.password))
        hashed_password = tornado.escape.to_unicode(hashed_password)

        if hashed_password == status.password:
            data["token"] = username

            session = dict(
                user_id = status.id,
                identity = identity
            )
            self.set_secure_cookie("session", json.dumps(session))

        else:
            self.write("username or password wrong.")
            self.finish()
        self.write(json.dumps(data))


class LogOutHandler(appbase.BaseHandler):
    async def post(self):
        self.clear_all_cookies()
        return


class UserInfoHandler(appbase.BaseHandler):
    # @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()
        session = self.current_user
        if not session:
            self.write("no login")
            return
        session = tornado.util.ObjectDict(session)
        identity = session.identity
        user_id = session.user_id
        try:
            result = self.queryone("select * from " + identity + " where id=%d", user_id)
        except NoResultError:
            self.write("no user font.")
            return
        if result.no == self.get_argument("token", None):
            data = dict(
                name = result.no,
                user_id = user_id,
                id = result.name,
                access = [identity],
                avator = 'https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png',
                message = ""
            )
            data = tornado.util.ObjectDict(data)
        self.write(json.dumps(result))

        # result =
