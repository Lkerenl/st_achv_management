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
    (r"/get_insert_data", handler.InsertDataHandler),
    (r"/get_table_data",handler.TableDataHandle),
    (r"/commitTableData",handler.CommitTableData),
    (r"/getScoreCnoData",handler.GetScoreCnoDataHandler),
    (r"/getScoreData",handler.GetScoreDataHandler),
    (r"/getAllScore",handler.getAllScoreHandler),

]

# class Route(tornado.routing.Router):
#     def __init__(self):
#         pass
