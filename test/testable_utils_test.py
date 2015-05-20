#!/usr/bin/env python3

import multiprocessing as MP
import unittest as UT
import random as R
import testable_utils as TU


TESTS = 500


def trunc_string(item):
    s = str(item)
    return s[0:12]

class testable_utils_test(UT.TestCase):
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
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_b))
                self.assertTrue(a < b)

    def test_large_float_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_a))
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)

    def test_large_float_less_than_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_b))
                self.assertTrue(a <= b)

    def test_large_float_greater_than(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a < _b):
                    _b = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_b))
                self.assertTrue(a > b)

    def test_large_float_less_than_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a <= _b):
                    _b = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_b))
                self.assertTrue(a >= b)

    def test_large_float_not_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a == _b):
                    _b = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_b))
                self.assertNotEqual(str(a), str(b))
                self.assertNotEqual(a, b)

    def test_large_float_negate(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = -_a
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_b))
                self.assertEqual(str(-a), str(b))
                self.assertEqual(-a, b)

    def test_large_float_assignment(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = a
                self.assertEqual(a, b)
                self.assertEqual(str(a), str(b))

                a = ""
                self.assertEqual(str(b), str(TU.large_float(str(_a))))
                self.assertEqual(b, TU.large_float(str(_a)))

    def test_large_float_string(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                b = TU.large_float(str(_a))
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)

    def test_large_float_pickle(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                q = MP.JoinableQueue()
                q.put(a)
                b = q.get()
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)


    #+-------------------------------------------------------------------------+
    #| Test for included interval                                              |
    #+-------------------------------------------------------------------------+
    def test_interval_width(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                width = abs(_a-_b)
                c = TU.interval(str(_a), str(_b))
                trunc_c = trunc_string(c.width())
                trunc_width = trunc_string(TU.large_float(str(width)))
                self.assertEqual(trunc_c, trunc_width)

    def test_interval_lower(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                a = TU.large_float(str(_a))
                c = TU.interval(str(_a), str(_b))
                self.assertEqual(str(c.lower()), str(a))
                self.assertEqual(c.lower(), a)

    def test_interval_upper(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                b = TU.large_float(str(_b))
                c = TU.interval(str(_a), str(_b))
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
                d = TU.interval(str(_a), str(_b))
                e = TU.interval(str(_b), str(_c))
                self.assertEqual(str(d.upper()), str(e.lower()))
                self.assertEqual(d.upper(), e.lower())

    def test_interval_string_same(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                b = TU.interval(str(_a), str(_a))
                c = TU.interval(str(_a), str(_a))
                self.assertEqual(str(b), str(c))
                self.assertEqual(b, c)

    def test_interval_pickle(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                c = TU.interval(str(_a), str(_b))
                q = MP.JoinableQueue()
                q.put(c)
                d = q.get()
                self.assertEqual(str(c), str(d))
                self.assertEqual(c, d)




    #+-------------------------------------------------------------------------+
    #| Test for box                                                            |
    #+-------------------------------------------------------------------------+
    def test_box_string_same(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = TU.interval(str(_a), str(_a))
                _c = TU.interval(str(_a), str(_a))
                d = TU.box()
                d.append(_b)
                d.append(_c)
                e = TU.box()
                e.append(_b)
                e.append(_c)
                self.assertEqual(str(d), str(e))
                self.assertEqual(d, e)

    def test_box_append_0(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                _c = R.uniform(-100, 100)
                _d = R.uniform(-100, 100)
                while (_c > _d):
                    _d = R.uniform(-100, 100)

                e = TU.box()
                e.append(str(_a), str(_b))
                e.append(str(_c), str(_d))

                f = TU.box()
                f.append(TU.interval(str(_a), str(_b)))
                f.append(TU.interval(str(_c), str(_d)))

                self.assertEqual(str(e), str(f))
                self.assertEqual(e, f)

    def test_box_append_1(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                _c = R.uniform(-100, 100)
                _d = R.uniform(-100, 100)
                while (_c > _d):
                    _d = R.uniform(-100, 100)

                e = TU.box()
                e.append(str(_a), str(_b))
                e.append(TU.interval(str(_c), str(_d)))

                f = TU.box()
                f.append(TU.interval(str(_a), str(_b)))
                f.append(str(_c), str(_d))

                self.assertEqual(str(e), str(f))
                self.assertEqual(e, f)

    def test_box_width_0(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                width = abs(_a-_b)
                c = TU.box()
                c.append(TU.interval(str(_a), str(_b)))
                trunc_c = trunc_string(c.width())
                trunc_width = trunc_string(TU.large_float(str(width)))
                self.assertEqual(trunc_c, trunc_width) 

    def test_box_width_1(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)

                _c = R.uniform(-100, 100)
                _d = R.uniform(-100, 100)
                while (_c > _d):
                    _d = R.uniform(-100, 100)
                while (abs(_a-_b) <= abs(_c-_d)):
                    _c = R.uniform(-100, 100)
                    _d = R.uniform(-100, 100)
                    while (_c > _d):
                        _d = R.uniform(-100, 100)
                width = abs(_a-_b)
                e = TU.box()
                e.append(TU.interval(str(_a), str(_b)))
                e.append(TU.interval(str(_c), str(_d)))
                trunc_e = trunc_string(e.width())
                trunc_width = trunc_string(TU.large_float(str(width)))
                self.assertEqual(trunc_e, trunc_width) 

    def test_box_width_2(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)

                _c = R.uniform(-100, 100)
                _d = R.uniform(-100, 100)
                while (_c > _d):
                    _d = R.uniform(-100, 100)
                while (abs(_a-_b) >= abs(_c-_d)):
                    _c = R.uniform(-100, 100)
                    _d = R.uniform(-100, 100)
                    while (_c > _d):
                        _d = R.uniform(-100, 100)
                width = abs(_c-_d)
                e = TU.box()
                e.append(TU.interval(str(_a), str(_b)))
                e.append(TU.interval(str(_c), str(_d)))
                trunc_e = trunc_string(e.width())
                trunc_width = trunc_string(TU.large_float(str(width)))
                self.assertEqual(trunc_e, trunc_width) 

    def test_box_split(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(0, 100)
                b = TU.box()
                b.append(str(-_a), str(_a))
                c = TU.box()
                c.append(str(-_a), "0")
                d = TU.box()
                d.append("0", str(_a))
                box_list = b.split()
                self.assertEqual(str(box_list[0]), str(c))
                self.assertEqual(box_list[0], c)

                self.assertEqual(str(box_list[1]), str(d))
                self.assertEqual(box_list[1], d)




if __name__ == "__main__":
    R.seed(42)
    UT.main()
