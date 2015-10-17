#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import json
from sys import argv
from functools import reduce, partial

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

DEFAULT_PORT = 8888

operations = {
    '+': sum,
    '-': lambda l: l[0] - sum(l[1:]),
    '*': partial(reduce, lambda x, y: x*y),
    '/': partial(reduce, lambda x, y: x/y),
}


def get_app():
    return Application([(r'/$', CalcHandler)])


class CalcHandler(RequestHandler):
    def write_result(self, result):
        self.write({'result': result})

    def post(self):
        try:
            query = json.loads(
                self.get_body_argument('query')
            )
            op = query['op']
            ops = query['ops']

            if len(ops) == 0:
                raise ValueError

            result = operations[op](ops)

        except:
            self.write_result(None)

        else:
            self.write_result(result)


if __name__ == '__main__':
    try:
        get_app().listen(
            int(argv[1]) if len(argv) == 2
            else DEFAULT_PORT)
        IOLoop.current().start()

    except KeyboardInterrupt:
        exit()
