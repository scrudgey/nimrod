#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_nimrod
----------------------------------

Tests for `nimrod` module.
"""

import unittest
import nimrod


class TestImports(unittest.TestCase):
    """Test the behavior of loading"""

    def test_load(self):
        pass


class TestSyntax(unittest.TestCase):
    """Test the main syntax features of nimrod."""

    def setUp(self):
        self.g = nimrod.Grammar()
        self.g.load('tests/def')

    def test_interpret(self):
        self.assertEqual(self.g.interpret('symbol'), 'fresh')
        self.assertEqual(self.g.interpret('nested-symbol'), 'fresh')
        self.assertEqual(self.g.interpret(
            'nested-symbol', parse=False), '{symbol}')
        # test depth catching
        # self.assertEqual(self.g.interpret('nested-symbol', depth=100), '{symbol}')
        # symbol doesn't exist
        self.assertEqual(self.g.interpret('not-symbol'), '{not-symbol}')

    def test_parse(self):
        # variables parse to pure strings
        self.assertEqual(self.g.parse('{symbol}'), 'fresh')
        self.assertEqual(self.g.parse('{nested-symbol}'), 'fresh')
        # test depth catching
        # self.assertEqual(self.g.parse('{loop-symbol-1}'), '{loop-symbol-1}')
        # test symbol doesn't exist
        self.assertEqual(self.g.parse('{not-symbol}'), '{not-symbol}')
        # parse multiple symbols in one string
        self.assertEqual(self.g.parse('{who} {do-what}'), 'we want the funk')

    def test_var(self):
        # test setting a variable
        self.g.parse('{set-var}')
        self.assertEqual(self.g.ref('var'), 'crescent')
        # unset variables parse to ''
        self.assertEqual(self.g.ref('not-a-var'), '')
        # test resetting variables
        self.g.reset()
        self.assertEqual(self.g.ref('var'), '')
        # test lazy assign
        self.g.parse('{lazy-def}')
        self.assertEqual(self.g.ref('var'), 'crescent fresh')
        # variables can be symbols
        self.g.parse('{set-var-2}')
        self.assertEqual(self.g.ref('var2'), '{symbol}')

    def test_p(self):
        # probability 1
        self.assertEqual(self.g.parse('<1|fresh>'), 'fresh')
        # probability 0
        self.assertEqual(self.g.parse('<0|fresh>'), '')

    def test_either(self):
        # probability 1
        self.assertEqual(self.g.parse('<1|A|B>'), 'A')
        # probability 0
        self.assertEqual(self.g.parse('<0|A|B>'), 'B')


if __name__ == '__main__':
    unittest.main()


# interpret
# interpret parse=False
# parse
# nested parse
