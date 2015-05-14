#!/usr/bin/env python3

import unittest as UT
import random as R
import interval as I


TESTS = 1000


def trunc_string(item):
    s = str(item)
    return s[0:12]


class large_float_test(UT.TestCase):
    #+-------------------------------------------------------------------------+
    #| Test for included large_float                                           |
    #+-------------------------------------------------------------------------+
    def test_large_float_less_than(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a >= _b):
                    _b = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_b))
                self.assertTrue(a < b)

    def test_large_float_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_a))
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)

    def test_large_float_less_than_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_b))
                self.assertTrue(a <= b)

    def test_large_float_greater_than(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a < _b):
                    _b = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_b))
                self.assertTrue(a > b)

    def test_large_float_less_than_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a <= _b):
                    _b = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_b))
                self.assertTrue(a >= b)

    def test_large_float_not_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a == _b):
                    _b = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_b))
                self.assertNotEqual(str(a), str(b))
                self.assertNotEqual(a, b)


    def test_large_float_negate(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = -_a
                a = I.large_float(str(_a))
                b = I.large_float(str(_b))
                self.assertEqual(str(a.neg()), str(b))
                self.assertEqual(a.neg(), b)

    def test_large_float_assignment(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = a
                self.assertEqual(str(a) , str(b))
                self.assertEqual(a , b)

                a = ""
                self.assertEqual(b, I.large_float(str(_a)))

    def test_large_float_string(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                b = I.large_float(str(_a))
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)




    #+-------------------------------------------------------------------------+
    #| Test for interval                                                       |
    #+-------------------------------------------------------------------------+
    def test_interval_width(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                width = abs(_a-_b)
                c = I.interval(str(_a), str(_b))
                trunc_c = trunc_string(c.width())
                trunc_width = trunc_string(I.large_float(str(width)))
                self.assertEqual(trunc_c, trunc_width)

    def test_interval_lower(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                a = I.large_float(str(_a))
                c = I.interval(str(_a), str(_b))
                self.assertEqual(str(c.lower()), str(a))
                self.assertEqual(c.lower(), a)

    def test_interval_upper(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                b = I.large_float(str(_b))
                c = I.interval(str(_a), str(_b))
                self.assertEqual(str(c.upper()), str(b))
                self.assertEqual(c.upper(), b)

    def test_interval_upper_and_lower(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                _c = R.uniform(-100, 100)
                while (_b > _c):
                    _c = R.uniform(-100, 100)
                d = I.interval(str(_a), str(_b))
                e = I.interval(str(_b), str(_c))
                self.assertEqual(str(d.upper()), str(e.lower()))
                self.assertEqual(d.upper(), e.lower())

    def test_interval_string_same(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                b = I.interval(str(_a), str(_a))
                c = I.interval(str(_a), str(_a))
                self.assertEqual(str(b), str(c))
                self.assertEqual(b, c)




if __name__ == "__main__":
    R.seed(42)
    UT.main()
