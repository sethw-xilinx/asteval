#!/usr/bin/env python
""" Base Test Case """
import unittest
from unittest_utils import TestCase
import numpy as np
from asteval import NameFinder

class TestEval(TestCase):
    '''testing of asteval'''

    def test_dict_index(self):
        '''dictionary indexing'''
        self.interp("a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}")
        self.istrue("a_dict['a'] == 1")
        self.istrue("a_dict['d'] == 4")

    def test_list_index(self):
        '''list indexing'''
        self.interp("a_list = ['a', 'b', 'c', 'd', 'o']")
        self.istrue("a_list[0] == 'a'")
        self.istrue("a_list[1] == 'b'")
        self.istrue("a_list[2] == 'c'")

    def test_tuple_index(self):
        '''tuple indexing'''
        self.interp("a_tuple = (5, 'a', 'x')")
        self.istrue("a_tuple[0] == 5")
        self.istrue("a_tuple[2] == 'x'")

    def test_string_index(self):
        '''string indexing'''
        self.interp("a_string = 'hello world'")
        self.istrue("a_string[0] == 'h'")
        self.istrue("a_string[6] == 'w'")
        self.istrue("a_string[-1] == 'd'")
        self.istrue("a_string[-2] == 'l'")

    def test_ndarray_index(self):
        '''nd array indexing'''
        self.interp("a_ndarray = 5*arange(20)")
        self.istrue("a_ndarray[2] == 10")
        self.istrue("a_ndarray[4] == 20")

    def test_ndarrayslice(self):
        '''array slicing'''
        self.interp("a_ndarray = arange(200).reshape(10, 20)")
        self.istrue("a_ndarray[1:3,5:7] == array([[25,26], [45,46]])")

    def test_while(self):
        '''while loops'''
        self.interp("""
n=0
while n < 8:
    n += 1
""")
        self.isvalue('n',  8)

    def test_for(self):
        '''for loops'''
        self.interp('''
n=0
for i in arange(10):
    n += i
''')
        self.isvalue('n', 45)

    def test_if(self):
        '''runtime errors test'''
        self.interp("""zero = 0
if zero == 0:
    x = 1
if zero != 100:
    x = x+1
if zero > 2:
    x = x + 1
else:
    y = 33
""")
        self.isvalue('x',  2)
        self.isvalue('y', 33)


    def test_print(self):
        '''print a string'''

        self.interp("print 1")
        out = self.read_stdout()
        self.assert_(out== '1\n')

    def test_cmp(self):
        '''numeric comparisons'''

        self.istrue("3 == 3")
        self.istrue("3.0 == 3")
        self.istrue("3.0 == 3.0")
        self.istrue("3 != 4")
        self.istrue("3.0 != 4")
        self.istrue("3 >= 1")
        self.istrue("3 >= 3")
        self.istrue("3 <= 3")
        self.istrue("3 <= 5")
        self.istrue("3 < 5")
        self.istrue("5 > 3")

        self.isfalse("3 == 4")
        self.isfalse("3 > 5")
        self.isfalse("5 < 3")

    def test_bool(self):
        '''boolean logic'''

        self.interp('''
yes = True
no = False
nottrue = False
a = arange(7)''')

        self.istrue("yes")
        self.isfalse("no")
        self.isfalse("nottrue")
        self.isfalse("yes and no or nottrue")
        self.isfalse("yes and (no or nottrue)")
        self.isfalse("(yes and no) or nottrue")
        self.istrue("yes or no and nottrue")
        self.istrue("yes or (no and nottrue)")
        self.isfalse("(yes or no) and nottrue")
        self.istrue("yes or not no")
        self.istrue("(yes or no)")
        self.isfalse("not (yes or yes)")
        self.isfalse("not (yes or no)")
        self.isfalse("not (no or yes)")
        self.istrue("not no or yes")
        self.isfalse("not yes")
        self.istrue("not no")

    def test_bool_coerce(self):
        '''coercion to boolean'''

        self.istrue("1")
        self.isfalse("0")

        self.istrue("'1'")
        self.isfalse("''")

        self.istrue("[1]")
        self.isfalse("[]")

        self.istrue("(1)")
        self.istrue("(0,)")
        self.isfalse("()")

        self.istrue("dict(y=1)")
        self.isfalse("{}")

    def test_assignment(self):
        '''variables assignment'''
        self.interp('n = 5')
        self.isvalue("n",  5)
        self.interp('s1 = "a string"')
        self.isvalue("s1",  "a string")
        self.interp('b = (1,2,3)')
        self.isvalue("b",  (1,2,3))
        self.interp('a = 1.*arange(10)')
        self.isvalue("a", np.arange(10) )
        self.interp('a[1:5] = 1 + 0.5 * arange(4)')
        self.isnear("a", np.array([ 0. ,  1. ,  1.5,  2. ,  2.5,  5. ,  6. ,  7. ,  8. ,  9. ]))

    def test_names(self):
        '''names test'''
        self.interp('nx = 1')
        self.interp('nx1 = 1')

    def test_syntaxerrors_1(self):
        '''assignment syntax errors test'''
        for expr in ('class = 1', 'for = 1', 'if = 1', 'raise = 1',
                     '1x = 1', '1.x = 1', '1_x = 1'):
            failed, errtype, errmsg = False, None, None
            try:
                self.interp(expr, show_errors=False)
            except RuntimeError:
                failed = True
                errtype, errmsg = self.interp.error[0].get_error()

            self.assertTrue(failed)
            self.assertTrue(errtype == 'SyntaxError')
            #self.assertTrue(errmsg.startswith('invalid syntax'))

    def test_syntaxerrors_2(self):
        '''syntax errors test'''
        for expr in ('x = (1/*)', 'x = 1.A', 'x = A.2'):

            failed, errtype, errmsg = False, None, None
            try:
                self.interp(expr, show_errors=False)
            except RuntimeError:
                failed = True
                errtype, errmsg = self.interp.error[0].get_error()
            self.assertTrue(failed)
            self.assertTrue(errtype == 'SyntaxError')
            #self.assertTrue(errmsg.startswith('invalid syntax'))

    def test_runtimeerrors_1(self):
        '''runtime errors test'''
        self.interp("zero = 0")
        self.interp("astr ='a string'")
        self.interp("atup = ('a', 'b', 11021)")
        self.interp("arr  = arange(20)")
        for expr, errname in (('x = 1/zero', 'ZeroDivisionError'),
                              ('x = zero + nonexistent', 'NameError'),
                              ('x = zero + astr', 'TypeError'),
                              ('x = astr * atup', 'TypeError'),
                              ('arr.shapx = 4', 'AttributeError')):
            failed, errtype, errmsg = False, None, None
            try:
                self.interp(expr, show_errors=False)
            except:
                failed = True
                errtype, errmsg = self.interp.error[0].get_error()
            self.assertTrue(failed)
            self.assertTrue(errtype == errname)
            #self.assertTrue(errmsg.startswith('invalid syntax'))

    def test_ndarrays(self):
        '''simple ndarrays'''
        self.interp('n = array([11, 10, 9])')
        self.istrue("isinstance(n, ndarray)")
        self.istrue("len(n) == 3")
        self.isvalue("n", np.array([11, 10, 9]))
        self.interp('n = arange(20).reshape(5, 4)')
        self.istrue("isinstance(n, ndarray)")
        self.istrue("n.shape == (5, 4)")

        self.interp("n.shape = (4, 5)")
        self.istrue("n.shape == (4, 5)")

    def test_binop(self):
        '''test binary ops'''
        self.interp('a = 10.0')
        self.interp('b = 6.0')

        self.istrue("a+b == 16.0")
        self.isnear("a-b", 4.0)
        self.istrue("a/(b-1) == 2.0")
        self.istrue("a*b     == 60.0")

    def test_unaryop(self):
        '''test binary ops'''
        self.interp('a = -10.0')
        self.interp('b = -6.0')

        self.isnear("a", -10.0)
        self.isnear("b", -6.0)

    def test_del(self):
        '''test del function'''
        self.interp('a = -10.0')
        self.interp('b = -6.0')

        self.assertTrue('a' in self.symtable)
        self.assertTrue('b' in self.symtable)

        self.interp("del a")
        self.interp("del b")

        self.assertFalse('a' in self.symtable)
        self.assertFalse('b' in self.symtable)

    def test_math1(self):
        '''builtin math functions'''
        self.interp('n = sqrt(4)')
        self.istrue('n == 2')
        self.isnear('sin(pi/2)', 1)
        self.isnear('cos(pi/2)', 0)
        self.istrue('exp(0) == 1')
        self.isnear('exp(1)', np.e)

    def test_namefinder(self):
        'test namefinder'
        ast = self.interp.parse('x+y+cos(z)')
        nf = NameFinder()
        nf.generic_visit(ast)
        self.assertTrue('x' in nf.names)
        self.assertTrue('y' in nf.names)
        self.assertTrue('z' in nf.names)
        self.assertTrue('cos' in nf.names)

    def test_index_assignment(self):
        "test indexing / subscripting on assignment"
        self.interp('x = arange(10)')
        self.interp('l = [1,2,3,4,5]')
        self.interp('l[0] = 0')
        self.interp('l[3] = -1')
        self.isvalue('l', [0,2,3,-1,5])
        self.interp('l[0:2] = [-1, -2]')
        self.isvalue('l', [-1,-2,3,-1,5])

        self.interp('x[1] = 99')
        self.isvalue('x', np.array([0,99,2,3,4,5,6,7,8,9]))
        self.interp('x[0:2] = [9,-9]')
        self.isvalue('x', np.array([9,-9,2,3,4,5,6,7,8,9]))

    def test_simple_function(self):
        "test function definition and running"
        self.interp("""
def fcn(x, scale=2, **kws):
    'test function'
    out = sqrt(x)
    if scale > 1:
        out = out * scale
    return out
""")
        self.interp("a = fcn(4, scale=9)")
        self.isvalue("a", 18)
        self.interp("a = fcn(9, scale=0)")
        self.isvalue("a", 3)

        self.interp("print fcn")
        out = self.read_stdout()
        out = out.split('\n')
        self.assert_(out[0].startswith('<Procedure fcn(x, scale='))
        self.assert_('test func' in out[1])

        self.interp("a = fcn()")

        errtype, errmsg = self.interp.error[0].get_error()
        self.assertTrue(errtype == 'TypeError')

if __name__ == '__main__':  # pragma: no cover
    for suite in (TestEval,):
        suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)
