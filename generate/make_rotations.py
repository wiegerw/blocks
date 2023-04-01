#!/usr/bin/env python3

#!/usr/bin/env python3

from typing import Tuple
from sympy import Symbol

Point = Tuple[Symbol, Symbol, Symbol]


def rotate_x_axis(p: Point) -> Point:
    x, y, z = p
    return x, -z,  y


def rotate_y_axis(p: Point) -> Point:
    x, y, z = p
    return  -z, y, x


def rotate_z_axis(p: Point) -> Point:
    x, y, z = p
    return  y, -x,  z


def compute_rotations(p: Point):
    points = {p}
    while True:
        points1 = points.copy()
        for p in points:
            points1.add(rotate_x_axis(p))
            points1.add(rotate_y_axis(p))
            points1.add(rotate_z_axis(p))
        if len(points) == len(points1):
            return points
        else:
            points = points1


if __name__ == '__main__':
    p = (Symbol('x'), Symbol('y'), Symbol('z'))
    points = compute_rotations(p)
    rotations = []

    for i, rotation in enumerate(points):
        text = '''class NAME(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return ROTATION

'''
        name = f'Rotation{i + 1}'
        text = text.replace('NAME', name)
        text = text.replace('ROTATION', str(rotation))
        print(text)
        rotations.append(name)

    print(',\n            '.join(f'{name}()' for name in rotations))
