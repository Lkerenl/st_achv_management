#!/usr/bin/env python3
import tornado.web
import json

import appbase

class IndexHandler(appbase.BaseHandler):
    def get(self):
        self.write("Index Page.")

class LoginHandler(appbase.BaseHandler):
    def get(self):
        self.write("Index Page.")
