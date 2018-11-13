#!/bin/usr/env python3
"""
This module is routing for app
"""
import handler

route_handler = [
    (r"/", handler.IndexHandler),
    (r"/index", handler.IndexHandler),
    (r"/login", handler.LoginHandler),
    (r"/logout", handler.LogOutHandler),
    (r"/get_info", handler.UserInfoHandler),

    (r"/query_score", handler.QuerySCHandler),
    (r"/dump_score", handler.DumpSCHandler),
    (r"/confirm_score", handler.ConfirmSCHandler),
    (r"/cookie", handler.CookieHandler),
    (r"/test", handler.TestqueryHandler),
<<<<<<< HEAD
    (r"/updatePassword",handler.ModifyPasswordHandler),
=======
    (r"/modify_password",handler.ModifyPasswordHandler),
>>>>>>> b83a714d993dcc29ba092ab774144004fe93935b

    (r"/get_insert_data", handler.InsertDataHandler),
    (r"/get_table_data",handler.TableDataHandle),
    (r"/commitTableData",handler.CommitTableData),
    (r"/getScoreCnoData",handler.GetScoreCnoDataHandler),
    (r"/getScoreData",handler.GetScoreDataHandler),
    (r"/getAllScore",handler.getAllScoreHandler),

<<<<<<< HEAD
	(r"/get_GPA",handler.GetUserGPAHandler),
    (r"/get_Course",handler.GetUserCourseHandler),
    (r"/get_GPATime",handler.GetUserGPATimeHandler),
    (r"/get_ChosenGPA",handler.GetUserChosenGPAHandler),
    (r"/get_Score",handler.GetUserCourseScoreHandler)

=======
>>>>>>> b83a714d993dcc29ba092ab774144004fe93935b

]

# class Route(tornado.routing.Router):
#     def __init__(self):
#         pass
