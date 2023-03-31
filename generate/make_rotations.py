#!/usr/bin/env python3

import argparse
import itertools
from pathlib import Path
from typing import List, Tuple

ROTATI0NS = '''-x, -y, z
-x, y, -z
x, -y, -z
x, y, z
-x, -z, -y
-x, z, y
x, -z, y
x, z, -y
-y, -x, z
-y, x, -z
y, -x, -z
y, x, z
-y, -z, -x
-y, z, x
y, -z, x
y, z, -x
-z, -x, -y
-z, x, y
z, -x, y
z, x, -y
-z, -y, x
-z, y, -x
z, -y, -x
z, y, x'''


if __name__ == '__main__':
    rotations = []
    for i, rotation in enumerate(ROTATI0NS.split('\n')):
        text = '''class NAME(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return ROTATION

'''
        name = f'Rotation{i + 1}'
        text = text.replace('NAME', name)
        text = text.replace('ROTATION', rotation)
        print(text)
        rotations.append(name)

    print(',\n            '.join(f'{name}()' for name in rotations))
