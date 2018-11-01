#!/usr/bin/env python3
import tornado.web
import bcrypt
import json

import appbase
from appbase import NoResultError

TEACHER = "teacher"
STUDENT = "student"
MANAGEMENT = "management"
IDENTITYS = [STUDENT, TEACHER, MANAGEMENT]


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
            token=None,
            message="success"
        )
        if identity not in IDENTITYS:
            self.write("identity wrong.")
            self.finish()
            return
        try:
            status = await self.queryone("select * from " + identity + " where no=%s", username)
        except NoResultError:
            self.write_error(401, "not user fond.")
            return

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None, bcrypt.hashpw, tornado.escape.utf8(password),
            tornado.escape.utf8(status.password))
        hashed_password = tornado.escape.to_unicode(hashed_password)

        if hashed_password == status.password:
            data["token"] = username

            session = dict(
                user_id=status.id,
                identity=identity
            )
            self.set_secure_cookie("session", json.dumps(session))

        else:
            self.write("username or password wrong.")
            self.finish()
        self.write(json.dumps(data))


class LogOutHandler(appbase.BaseHandler):
    async def post(self):
        self.set_allow_origin()
        self.clear_all_cookies()
        return


class UserInfoHandler(appbase.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()
        session = self.current_user
        identity = session.get('identity',None)
        user_id = session.get('user_id',None)
        try:
            result = await self.queryone("select * from " + identity + " where id=%s", str(user_id))
        except NoResultError:
            self.write_error(401, "no user fond.")
            return
        result.pop('password', None)
        if result.no == self.get_argument("token", None):
            data = dict(
                name=result.no,
                user_id=user_id,
                access=[identity],
                avator='https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png',
                message=result
            )
            data = tornado.util.ObjectDict(data)
            self.write(json.dumps(data))
            return
        self.set_status(404)


class QuerySCHandler(appbase.BaseHandler):
    """
    ex:
        /query_score?token=jwk&time=2018下&st=1600100101

    wrings:
        If your identity is a student, you must ensure that
    st is equal to token.
    """
    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()

        session = self.current_user
        token = self.get_argument("token", None)
        time = self.get_argument("time", None)
        st = self.get_argument("st", None)
        if session.get('identity',None) != MANAGEMENT and st != token:
            self.set_status(403)
            self.finish()
            return
        try:
            result = await self.query("select no,name,cno,cname,score from score_view where no=%s and ctime=%s", st, time)
        except NoResultError:
            self.write("no data fond.")
            return
        data = dict(
            no=st,
            name=list(map(lambda x: x.pop('name',None), result))[0],
            score=[]
        )
        for _ in result:
            if _.get('score') != None:
                data['score'].append(_)
        self.write(json.dumps(data))


class DumpSCHandler(appbase.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()

        session = self.current_user
        if session.get('identity',None) != MANAGEMENT:
            self.write_error(403, "Insufficient permissions.")
            return

        st = self.get_argument("st", None)
        if not st:
            self.write("no arg")
        try:
            result = await self.query("select name,cname,ctype,ccredits,score from score_view where no=%s", st)
        except:
            pass
        # self.write(json.dumps(result))

        data = dict(
            no=st,
            name=list(map(lambda x: x.pop('name',None), result))[0],
            score=[]
        )
        for _ in result:
            if _.get('score') != None:
                data['score'].append(_)

        self.write(json.dumps(data))


class ConfirmSCHandler(appbase.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()

        session = self.current_user
        if session.get('identity',None) != MANAGEMENT:
            self.write_error(403, "Insufficient permissions.")
            return
        cno = self.get_argument("cno", None)
        if cno:
            result = await self.query("select cno,cname,name from tmp_score_view group by cno")
        else:
            result = await self.query("select no,name,exam,regular,expr from tmp_score_view where cno=%s", cno)
        self.write(json.dumps(result))

    async def post(self):
        self.set_allow_origin()

        session = self.current_user
        if session.get('identity',None) != MANAGEMENT:
            self.write_error(403, "Insufficient permissions.")
            return

class CookieHandler(appbase.BaseHandler):
    async def get(self):
        session = self.current_user
        self.write(session)
