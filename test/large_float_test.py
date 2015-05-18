#!/usr/bin/env python3

import unittest as UT
import random as R
import large_float as LF
import multiprocessing as MP

TESTS = 1


class large_float_test(UT.TestCase):
    #+-------------------------------------------------------------------------+
    #| Test for large_float                                                    |
    #+-------------------------------------------------------------------------+
    def test_large_float_less_than(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a >= _b):
                    _b = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_b))
                self.assertTrue(a < b)

    def test_large_float_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_a))
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)

    def test_large_float_less_than_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a > _b):
                    _b = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_b))
                self.assertTrue(a <= b)

    def test_large_float_greater_than(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a < _b):
                    _b = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_b))
                self.assertTrue(a > b)

    def test_large_float_less_than_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a <= _b):
                    _b = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_b))
                self.assertTrue(a >= b)

    def test_large_float_not_equal(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = R.uniform(-100, 100)
                while (_a == _b):
                    _b = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_b))
                self.assertNotEqual(str(a), str(b))
                self.assertNotEqual(a, b)


    def test_large_float_negate(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                _b = -_a
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_b))
                self.assertEqual(str(a.neg()), str(b))
                self.assertEqual(a.neg(), b)

    def test_large_float_assignment(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = a
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)

                a = ""
                self.assertEqual(str(b), str(LF.large_float(str(_a))))
                self.assertEqual(b, LF.large_float(str(_a)))

    def test_large_float_string(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                b = LF.large_float(str(_a))
                self.assertEqual(a, b)
                self.assertEqual(str(a), str(b))
                
    def test_large_float_pickle(self):
        for i in range(TESTS):
            with self.subTest(i=i):
                _a = R.uniform(-100, 100)
                a = LF.large_float(str(_a))
                q = MP.Queue()
                q.put(a)
                b = q.get()
                self.assertEqual(str(a), str(b))
                self.assertEqual(a, b)

if __name__ == "__main__":
    R.seed(42)
    UT.main()
