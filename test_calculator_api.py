#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import json
from unittest import TestCase, main

from tornado.gen import coroutine
from tornado.escape import url_escape
from tornado.testing import AsyncHTTPTestCase, gen_test

import calculator_api as ca


class TestOperations(TestCase):
    def assertNumReduceOperation(
            self, operation, *data):
        msg = \
            "Reduce operation {op} over " \
            "{ops} isn't equal to {r}!"

        for r, ops in data:
            with self.subTest(result=r, operands=ops):
                fmsg = msg.format(
                    op=operation, ops=ops, r=r)

                self.assertAlmostEqual(
                    operation(ops), r, msg=fmsg)

    def test_sum(self):
        self.assertNumReduceOperation(
            ca.operations['+'],
            (6, (1, 2, 3)),
            (3, (1, 2)),
            (-6, (-1, -2, -3)),
            (12, (1, 2, 3, 1, 2, 3)),
            (-2, (-1, 2, -3)),
            (2, (1, -2, 3)),
            (1, (0.333333333333, 0.666666666666)),
            (13/17, (4/17, 3/17, 7/17, -1/17)),
        )

    def test_sub(self):
        self.assertNumReduceOperation(
            ca.operations['-'],
            (-4, (1, 2, 3)),
            (-1, (1, 2)),
            (4, (-1, -2, -3)),
            (-10, (1, 2, 3, 1, 2, 3)),
            (0, (-1, 2, -3)),
            (0, (1, -2, 3)),
            (-0.33333333, (0.333333333333, 0.666666666666)),
            (-5/17, (4/17, 3/17, 7/17, -1/17)),
        )

    def test_mul(self):
        self.assertNumReduceOperation(
            ca.operations['*'],
            (6, (1, 2, 3)),
            (2, (1, 2)),
            (-6, (-1, -2, -3)),
            (36, (1, 2, 3, 1, 2, 3)),
            (6, (-1, 2, -3)),
            (-6, (1, -2, 3)),
            (0.222222222, (0.333333333333, 0.666666666666)),
            (-84/83521, (4/17, 3/17, 7/17, -1/17)),
        )

    def test_div(self):
        self.assertNumReduceOperation(
            ca.operations['/'],
            (1/6, (1, 2, 3)),
            (0.5, (1, 2)),
            (-1/6, (-1, -2, -3)),
            (1/36, (1, 2, 3, 1, 2, 3)),
            (1/6, (-1, 2, -3)),
            (-1/6, (1, -2, 3)),
            (0.5, (0.333333333333, 0.666666666666)),
            (-4*17*17/(3*7), (4/17, 3/17, 7/17, -1/17)),
        )


class TestApp(AsyncHTTPTestCase):
    @property
    def url(self):
        if not hasattr(self, '_url'):
            self._url = self.get_url('/')
        return self._url

    def get_app(self):
        return ca.get_app()

    def get_body(self, op, *ops):
        json_ops = json.dumps(ops)
        json_query = '{{"op": "{}", "ops": {}}}'.format(
            op, json_ops)
        return 'query=' + url_escape(json_query)

    @coroutine
    def send_query(self, http_body):
        response = yield self.http_client.fetch(
            self.url, method='POST', body=http_body)
        response = json.loads(
            response.body.decode()
        )
        self.assertIsInstance(response, dict)
        self.assertIn('result', response)
        return response

    @coroutine
    def send_f_query(self, op, *ops):
        response = yield self.send_query(
            self.get_body(op, *ops)
        )
        return response

    @gen_test
    def test_query_parsing(self):
        querys = [
            '',
            'query=',
            'query=hola',
            'query=' + url_escape('{}'),
            self.get_body('^', 1, 1),
            self.get_body('*'),
            '&%$(&%(&%$   +++////))',
        ]

        for query in querys:
            with self.subTest(query=query):
                response = yield self.send_query(query)
                self.assertIsNone(response['result'])

        response = yield self.send_f_query('+', 1, 1)
        self.assertIsNotNone(response['result'])

    @gen_test
    def test_single_number_ops(self):
        ops = ['+', '-', '*', '/']

        for op in ops:
            with self.subTest(operation=op):
                response = yield self.send_f_query(op, 6)
                self.assertEqual(response['result'], 6)

    @gen_test
    def test_sum(self):
        op = '+'

        response = yield self.send_f_query(op, 1, 2, 3)
        self.assertEqual(response['result'], 6)

        response = yield self.send_f_query(
            op, 0.333333333, 0.6666666666)
        self.assertAlmostEqual(response['result'], 1)

    @gen_test
    def test_sub(self):
        op = '-'

        response = yield self.send_f_query(op, 1, 2, 3)
        self.assertEqual(response['result'], -4)

        response = yield self.send_f_query(
            op, 0.333333333, 0.6666666666)
        self.assertAlmostEqual(
            response['result'], -0.3333333333)

    @gen_test
    def test_mul(self):
        op = '*'

        response = yield self.send_f_query(op, 1, 2, 3)
        self.assertEqual(response['result'], 6)

        response = yield self.send_f_query(
            op, 0.333333333, 0.6666666666)
        self.assertAlmostEqual(
            response['result'], 0.2222222222222)

    @gen_test
    def test_div(self):
        op = '/'

        response = yield self.send_f_query(op, 1, 2, 3)
        self.assertAlmostEqual(
            response['result'], 0.166666666667)

        response = yield self.send_f_query(
            op, 0.333333333, 0.6666666666)
        self.assertAlmostEqual(response['result'], 0.5)

if __name__ == '__main__':
    main()
