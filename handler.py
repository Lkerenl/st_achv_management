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
        login_info = json.loads(self.request.body.decode('utf-8'))
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
        session = json.loads(session.decode('utf-8'))
        session = tornado.util.ObjectDict(session)
        identity = session.identity
        user_id = session.user_id
        try:
            result = await self.queryone("select * from " + identity + " where id=%s", str(user_id))
        except NoResultError:
            self.write("no user font.")
            return
        if result.no == self.get_argument("token", None):
            data = dict(
                name = result.no,
                user_id = user_id,
                access = [identity],
                avator = 'https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png',
                message = result
            )
            data = tornado.util.ObjectDict(data)
            self.write(json.dumps(data))
            return
        self.set_status(404)

        # self.write(json.dumps(result))

        # result =

class InsertDataHandler(appbase.BaseHandler):
    async def get(self):
        self.set_allow_origin()
        session = self.current_user
        if not session:
            self.write("no login")
            return
        session = json.loads(session.decode('utf-8'))
        session = tornado.util.ObjectDict(session)
        id = session.user_id
        result = await self.query("select cno from tea_cour_view where id=%s",str(id))
        data = dict(
            message = result
        )
        data = tornado.util.ObjectDict(data)
        self.write(json.dumps(data))
        return

class TableDataHandle(appbase.BaseHandler):
    async def post(self):
        self.set_allow_origin()
        key = str(self.request.body.decode('utf-8'))
        result = await self.query("select no,name from score_view where cno=%s",key)
        list(map(lambda x:x.update(regular=0,exam=0,expr=0),result))
        data = dict(
            message = result
        )
        data = tornado.util.ObjectDict(data)
        self.write(json.dumps(data))
        return

class CommitTableData(appbase.BaseHandler):
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()
    async def post(self):
        self.set_allow_origin()
        data = json.loads(self.request.body.decode('utf-8'))
        data = tornado.util.ObjectDict(data)
        cno = data.key
        print(cno)
        score_info = data.tableData
        course_result = await self.query("select id from course where cno=%s",cno)
        student_result = await self.query("select id from student where no=%s",score_info[0]['no'])
        tmp_score_result = await self.query("select id from tmp_scores where course=%s",course_result[0]['id'])
        score_result = await self.query("select score from score_view where cno=%s limit 1",cno)
        print(len(tmp_score_result))
        print(len(score_result))
        if len(tmp_score_result) == 0 and score_result[0]["score"] == None:
            for info in score_info:
                await self.execute("insert into tmp_scores(regular,exam,student,course,expr) values(%s,%s,%s,%s,%s)",str(info['regular']),str(info['exam']),str(student_result[0]['id']),str(course_result[0]['id']),str(info['expr']))
            self.write("写入成功")
        else:
            self.write("请不要重复提交")
            return

class GetScoreDataHandler(appbase.BaseHandler):
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()
    async def post(self):
        self.set_allow_origin()
        key = str(self.request.body.decode('utf-8'))
        result = await self.queryone("select max(score),min(score),avg(score) from score_view where cno=%s",key)
        die = result['die']
        all = result['all']
        result.update(sodie=((die*1.0)/all)*100,nodie=100-((die*1.0)/all)*100,good=all-die)
        data = dict(
            message = result
        )
        data = tornado.util.ObjectDict(data)
        self.write(json.dumps(data))

class GetScoreCnoDataHandler(appbase.BaseHandler):
    async def get(self):
        self.set_allow_origin()
        session = self.current_user
        if not session:
            self.write("no login")
            return
        session = json.loads(session.decode('utf-8'))
        session = tornado.util.ObjectDict(session)
        id = session.user_id
        result = await self.query("(select cno from score_view where score is not null) union (select cno from tea_cour_view where id=%s)",str(id))
        data = dict(
            message = result
        )
        data = tornado.util.ObjectDict(data)
        self.write(json.dumps(data))
        return

class ModifyPasswordHandler(appbase.BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        session = self.current_user
        data = json.loads(self.request.body)
        if not data.get('old_password',None) and not data.get('new_password',None):
            self.write("no angr")
            return

        try:
            old_hashed_password = await self.queryone("select password from " + session.get('identity', None) + ' where id=%s',str(session.get('user_id',None)))
        except NoResultError:
            self.write('user error')
            return

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.hashpw,
            tornado.escape.utf8(data.get('old_password',None)),
            tornado.escape.utf8(old_hashed_password.get('password',None)))
        hashed_password = tornado.escape.to_unicode(hashed_password)

        if hashed_password == old_hashed_password.get('password',None):
            new_hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
                None,
                bcrypt.hashpw,
                tornado.escape.utf8(data.get('new_password',None)),
                bcrypt.gensalt())
            new_hashed_password = tornado.escape.to_unicode(new_hashed_password)
            await self.execute('update ' + session.get('identity', None) + ' set password=%s where id=%s',new_hashed_password,str(session.get('user_id',None)))
            return
        self.set_status(403)

class getAllScoreHandler(appbase.BaseHandler):
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()

    #@tornado.web.authenticated
    async def post(self):
        self.set_allow_origin()
        session = self.current_user
        if not session:
            self.write("no login")
            return
        session = json.loads(session.decode('utf-8'))
        session = tornado.util.ObjectDict(session)
        identity = session.identity
        cno = str(self.request.body.decode('utf-8'))
        if identity == 'teacher':
            try:
                cno = dict(
                    cno=cno
                )
                user_id = session.user_id
                all_cno = await self.query("select cno from tea_cour_view where id=%s",user_id)
                if cno in all_cno:
                    result = await self.query("select no,name,score from score_view where cno=%s", cno['cno'])
                else:
                    self.write("你输入的课号有误")
                    self.set_status(403)
                    return
            except NoResultError:
                self.write("no data fond.")
                self.set_status(403)
                return
        elif identity == 'management':
            try:
                result = await self.query("select no,name,score from score_view where cno=%s", cno)
            except NoResultError:
                self.write("no data fond.")
                self.set_status(403)
                return
        else:
            self.write("身份无法验证")
            self.set_status(403)
            return
        data = dict(
            message=result
        )
        self.write(json.dumps(data))