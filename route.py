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
]

# class Route(tornado.routing.Router):
#     def __init__(self):
#         pass
