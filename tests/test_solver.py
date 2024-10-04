# Copyright 2024 Wieger Wesselink + Huub van de Wetering.
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)

from unittest import TestCase
from more_itertools import flatten

from blocks import solve_puzzle, parse_pieces

# This test solves a very simple puzzle with 3 pieces.
#
# 0 0 2
# 0 1 2
# 1 1 2

PIECES = '''
0 0 0   0 1 0   1 1 0
0 0 0   1 0 0   1 1 0
0 0 0   0 1 0   0 2 0
'''

GOAL = '0 0 0   1 0 0   2 0 0   0 1 0   1 1 0   2 1 0   0 2 0   1 2 0   2 2 0'


class Test(TestCase):
    def test_puzzle(self):
        pieces = parse_pieces(PIECES)
        goal = parse_pieces(GOAL)[0]
        solution = solve_puzzle(pieces, goal)
        self.assertEqual(set(goal), set(flatten(solution)))