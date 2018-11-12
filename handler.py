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
            self.wirte("not user fond.")
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

        if not session:
            self.write("no login")
            return
            
        try:
            result = await self.queryone("select * from " + identity + " where id=%s", str(user_id))
        except NoResultError:
            self.wirte("no user fond.")
            self.set_status(404)
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
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()

    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()

        session = self.current_user
        token = self.get_argument("token", None)
        time = self.get_argument("time", None)
        st = self.get_argument("st", None)
        if session.get_argument('identity',None) != MANAGEMENT and st != token:
            self.set_status(403)
            self.finish()
            return
        try:
            result = await self.query("select no,name,cno,cname,score from score_view where no=%s and ctime=%s", st, time)
        except NoResultError:
            self.write("no data fond.")
            self.set_status(404)
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
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()

    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()

        session = self.current_user
        if session.get('identity',None) != MANAGEMENT:
            self.wirte("Insufficient permissions.")
            self.set_status(403)
            return

        st = self.get_argument("st", None)
        try:
            result = await self.query("select name,cno,cname,ctype,ccredits,score from score_view where no=%s", st)
        except:
            pass
        # self.write(json.dumps(result))

        data = dict(
            no=st,
            name=list(map(lambda x: x.pop('name',None), result))[0],
            score=[]
        )
        sum_score = 0
        sum_credits = 0
        for _ in result:
            if _.get('score') != None:
                data['score'].append(_)
                sum_score += _.get('score',None) * _.get('ccredits',None)
                sum_credits += _.get('ccredits',None)
        gpa = sum_score/sum_credits
        data['gpa'] = '%.2f' % gpa

        self.write(json.dumps(data))


class ConfirmSCHandler(appbase.BaseHandler):
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()

    @tornado.web.authenticated
    async def get(self):
        self.set_allow_origin()

        session = self.current_user
        if session.get('identity',None) != MANAGEMENT:
            self.wirte( "Insufficient permissions.")
            self.set_status(403)
            return
        cno = self.get_argument("cno", None)
        if not cno:
            result = await self.query("select cno,cname from tmp_score_view group by cno,cname")
        else:
            result = await self.query("select no,name,exam,regular,expr from tmp_score_view where cno=%s", cno)
        self.write(json.dumps(result))

    @tornado.web.authenticated
    async def post(self):
        self.set_allow_origin()

        session = self.current_user
        if session.get('identity',None) != MANAGEMENT:
            self.wirte("Insufficient permissions.")
            self.set_status(403)
            return
        req = json.loads(self.request.body)
        confirm = req.get('confirm',None)
        cno = req.get("cno",None)
        if confirm == None:
            self.write("no angr")
            return

        if confirm:
            try:
                await self.commit_score(cno)
            except:
                self.write("write score error")
                return
        try:
            await self.delete_score(cno)
        except:
            self.write("delete score error")
            return

        self.write("confirm success.")

    async def commit_score(self, cno):
        tmp = await self.query("select no,cno,"
        "case when regular_grade + exam_grade=1 "
        "then  regular * regular_grade + exam * exam_grade "
        "else regular * regular_grade + exam * exam_grade + (1 - regular_grade - exam_grade) * expr "
        "end "
        "from tmp_score_view where cno=%s",cno)
        tmp = list(map( lambda x:(x['no'],x['cno'],x['case']),tmp))

        for _ in tmp:
            id = await self.queryone("select id from score_view where no=%s and cno=%s",_[0],_[1])
            await self.execute("update score set score=%s where id=%s",_[2], id['id'])

    async def delete_score(self, cno):
        c_id = await self.query("select id from tmp_score_view where cno=%s",cno)
        assert c_id[0].id == c_id[-1].id
        await self.execute("delete from tmp_scores where course=%s",str(c_id[0].id))


class InsertDataHandler(appbase.BaseHandler):
    async def get(self):
        self.set_allow_origin()
        session = self.current_user
        if not session:
            self.write("no login")
            return
        session = json.loads(session)
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
        key = str(self.request.body)
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
        data = json.loads(self.request.body)
        data = tornado.util.ObjectDict(data)
        cno = data.key

        score_info = data.tableData
        course_result = await self.query("select id from course where cno=%s",cno)
        student_result = await self.query("select id from student where no=%s",score_info[0]['no'])
        tmp_score_result = await self.query("select id from tmp_scores where course=%s",course_result[0]['id'])
        score_result = await self.query("select score from score_view where cno=%s limit 1",cno)

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
        session = self.current_user
        user_id = session.get('user_id',None)
        key = str(self.request.body)
        try:
            flag = self.queryone("select cno from tea_cour_view where id=%s and cno=%s",str(user_id),key)
        except:
            self.set_status(404)
            return
        result = await self.queryone("select max(score),min(score),avg(score),count(*) as all from score_view where cno=%s",key)
        tmp = await self.query("select t.con,count(*) from (select (score_view.score/10)con from score_view where cno=%s)t group by t.con",key)
        nodie = 0
        for _ in tmp:
            if _.get('con',None)>6:
                nodie += _.get('')
        all = result.get('all',None)
        die = all - nodie
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
        session = json.loads(session)
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

class TestqueryHandler(appbase.BaseHandler):
    async def get(self):
        pass
    async def post(self):
        self.set_allow_origin()
        key = str(self.request.body)
        result = await self.queryone("select max(score),min(score),avg(score) from score_view where cno=%s",key)
        die = result['die']
        all = result['all']
        result.update(sodie=((die*1.0)/all)*100,nodie=100-((die*1.0)/all)*100,good=all-die)
        data = dict(
            message = result
        )
        data = tornado.util.ObjectDict(data)
        self.write(json.dumps(data))
        # time = self.get_argument("time", None)
        # st = self.get_argument("st", None)
        #
        # try:
        #     result = await self.query("select no,name,cno,cname,score from score_view where no=%s and ctime=%s", st, time)
        # except NoResultError:
        #     self.write("no data fond.")
        #     self.set_status(404)
        #     return
        # # print(st)
        # # print(time)
        # # self.write(json.dumps(result))
        # data = dict(
        #     no=st,
        #     name=list(map(lambda x: x.pop('name',None), result))[0],
        #     score=[]
        # )
        # for _ in result:
        #     if _.get('score') != None:
        #         data['score'].append(_)
        # self.write(json.dumps(data))

class CookieHandler(appbase.BaseHandler):
    async def get(self):
        session = self.current_user
        self.write(session)

class getAllScoreHandler(appbase.BaseHandler):
    async def options(self):
        self.set_status(204)
        self.set_allow_origin()

    @tornado.web.authenticated
    async def post(self):
        self.set_allow_origin()
        session = self.current_user
        if not session:
            self.write("no login")
            return
        session = json.loads(session)
        session = tornado.util.ObjectDict(session)
        identity = session.identity
        cno = str(self.request.body)
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
