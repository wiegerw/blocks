#!/usr/bin/env python3

# Copyright 2023 Wieger Wesselink.
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)

import argparse
import itertools
from pathlib import Path
from typing import List, Optional, Tuple
from z3 import *


# type definitions
Position = Tuple[int, int, int]
Piece = List[Position]
RGB = Tuple[float, float, float]


COLORS = '''
166,206,227
31,120,180
178,223,138
51,160,44
251,154,153
227,26,28
253,191,111
255,127,0
202,178,214
106,61,154
255,255,153
177,89,40
'''


def parse_colors(text: str) -> List[RGB]:
    """
    Parses a string of comma-separated RGB color values into a list of color triples.

    Args:
        text (str): A string of comma-separated RGB color values.

    Returns:
        List[Position]: A list of color triples, where each triple is a tuple of
        three integers representing the red, green, and blue values of a color.
    """
    # Split the text into a list of lines
    lines = text.strip().split('\n')

    # Split each line into a list of color values and convert them to integers
    colors = [tuple(map(int, line.split(','))) for line in lines]

    # Divide by 255
    colors = [(r / 255, g / 255, b / 255) for (r, g, b) in colors]

    return colors


def parse_pieces(text: str) -> List[Piece]:
    """
    Parses a string with pieces. Each line contains the coordinates of one piece.

    Args:
        text (str): A string of pieces.

    Returns:
        List[Piece]: A list of pieces.
    """

    # Split the text into a list of lines
    lines = text.strip().split('\n')

    # Remove comments
    lines = [line for line in lines if not line.startswith('#')]

    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    # Split each line into a list of color values, convert them to integers, and group them into blocks
    pieces = [[tuple(map(int, lines[i].split()[j:j + 3])) for j in range(0, len(lines[i].split()), 3)] for i in range(len(lines))]

    return pieces


def load_pieces(filename: str) -> List[Piece]:
    text = Path(filename).read_text()
    return parse_pieces(text)


def make_cube(point: Position, color: RGB) -> str:
    """
    Returns a cube in VRML format
    """
    x, y, z = point
    r, g, b = color
    return f'      KUBUS {{ translation {x} {y} {z} color {r} {g} {b} }}'


def make_piece(name: str, piece: Piece, color: RGB, translation: Position) -> str:
    """
    Returns a piece in VRML format
    """
    text = '''DEF <NAME> Transform {
       translation <TRANSLATION>
       children [
    <CUBES>
       ]}
        '''
    x, y, z = translation
    cubes = '\n'.join([make_cube(point, color) for point in piece])
    text = text.replace('<NAME>', name)
    text = text.replace('<TRANSLATION>', f'{x} {y} {z}')
    text = text.replace('<CUBES>', cubes)
    return text


def bounding_box(pieces: List[Piece]) -> Tuple[Position, Position]:
    min_x = 0
    min_y = 0
    min_z = 0
    max_x = 0
    max_y = 0
    max_z = 0
    for piece in pieces:
        for (x, y, z) in piece:
            min_x = min(x, min_x)
            min_y = min(y, min_y)
            min_z = min(z, min_z)
            max_x = max(x, max_x)
            max_y = max(y, max_y)
            max_z = max(z, max_z)
    return (min_x, min_y, min_z), (max_x, max_y, max_z)


def make_vrml(pieces: List[Piece], colors: List[RGB], translate: bool = True) -> str:
    text = '''#VRML V2.0 utf8

PROTO KUBUS [field SFVec3f translation 0 0 0 field SFColor color 1 0 0] {
Transform {
   translation IS translation
   children [
      Shape{geometry Box { size 0.9 0.9 0.9 } appearance Appearance{ material Material { diffuseColor IS color               }}}
      Shape{geometry Box { size 1.0 1.0 1.0 } appearance Appearance{ material Material { diffuseColor 1 1 1 transparency 0.9 }}}
   ]
}}

'''

    (min_x, min_y, min_z), (max_x, max_y, max_z) = bounding_box(pieces)
    size_x = max_x - min_x + 2
    size_y = max_y - min_y + 2
    N = round(math.sqrt(len(pieces)))

    def piece(i: int) -> str:
        name = f'BLOCK{i}'
        piece = pieces[i]
        color = colors[i % len(colors)]
        translation = (size_x * (i % N), size_y * (i // N), 0) if translate else (0, 0, 0)
        return make_piece(name, piece, color, translation)

    return text + '\n\n'.join([piece(i) for i in range(len(pieces))])


def cube_positions(X: int, Y: int, Z: int) -> List[Position]:
    return [(x, y, z) for x in range(X) for y in range(Y) for z in range(Z)]


def translate_object(obj: List[Position], translation: Position) -> List[Position]:
    """
    Translates the given object by the given amount in each dimension.

    Args:
        obj: The object to be translated, given as a list of 3D points with integer coordinates.
        translation: The translation vector.

    Returns:
        A new list of 3D points representing the translated object.
    """
    dx, dy, dz = translation
    return [(x+dx, y+dy, z+dz) for (x, y, z) in obj]


def is_inside_bbox(point: Position, bboxmin: Position, bboxmax: Position) -> bool:
    """
    Determines whether the given point is inside the given bounding box.

    Args:
        point: The point to check, given as a 3D point with integer coordinates.
        bboxmin: The minimum corner of the bounding box, given as a 3D point with integer coordinates.
        bboxmax: The maximum corner of the bounding box, given as a 3D point with integer coordinates.

    Returns:
        True if the point is inside the bounding box, False otherwise.
    """
    return (bboxmin[0] <= point[0] <= bboxmax[0] and
            bboxmin[1] <= point[1] <= bboxmax[1] and
            bboxmin[2] <= point[2] <= bboxmax[2])


def unique_orientations(pieces: List[Piece]) -> List[Piece]:
    piece_tuples = set([tuple(sorted(piece)) for piece in pieces])
    return [list(piece) for piece in piece_tuples]


class Transformation(object):
    def __call__(self, p: Position) -> Position:
        raise NotImplementedError


class Translation(object):
    def __init__(self, translation: Position):
        self.translation = translation

    def __call__(self, p: Position) -> Position:
        x, y, z = self.translation
        return p[0] + x, p[1] + y, p[2] + z


class Rotation1(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (z, -y, x)


class Rotation2(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (x, z, -y)


class Rotation3(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-x, -y, z)


class Rotation4(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-z, x, -y)


class Rotation5(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-z, -x, y)


class Rotation6(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (y, -z, -x)


class Rotation7(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (x, -z, y)


class Rotation8(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-y, -x, -z)


class Rotation9(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-x, y, -z)


class Rotation10(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (y, z, x)


class Rotation11(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (x, y, z)


class Rotation12(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-y, z, -x)


class Rotation13(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-y, x, z)


class Rotation14(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (z, y, -x)


class Rotation15(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (y, -x, z)


class Rotation16(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-z, -y, -x)


class Rotation17(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (y, x, -z)


class Rotation18(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (x, -y, -z)


class Rotation19(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-x, z, y)


class Rotation20(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-z, y, x)


class Rotation21(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-y, -z, x)


class Rotation22(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (z, x, y)


class Rotation23(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (z, -x, -y)


class Rotation24(Transformation):
    def __call__(self, p: Position) -> Position:
        x, y, z = p
        return (-x, -z, -y)


def rotation_group() -> List[Transformation]:
    return [Rotation1(),
            Rotation2(),
            Rotation3(),
            Rotation4(),
            Rotation5(),
            Rotation6(),
            Rotation7(),
            Rotation8(),
            Rotation9(),
            Rotation10(),
            Rotation11(),
            Rotation12(),
            Rotation13(),
            Rotation14(),
            Rotation15(),
            Rotation16(),
            Rotation17(),
            Rotation18(),
            Rotation19(),
            Rotation20(),
            Rotation21(),
            Rotation22(),
            Rotation23(),
            Rotation24()]


def move_to_origin(piece: Piece) -> Piece:
    bmin, bmax = bounding_box([piece])
    x, y, z = bmin
    translate = Translation((-x, -y, -z))
    return list(sorted([translate(pos) for pos in piece]))


def rotated_pieces(piece: Piece) -> List[Piece]:
    pieces = [[rotate(pos) for pos in piece] for rotate in rotation_group()]
    pieces = [move_to_origin(piece) for piece in pieces]
    piece_tuples = set(tuple(piece) for piece in pieces)
    pieces = [list(piece) for piece in piece_tuples]
    return pieces


def is_sub_piece(piece: Piece, goal: Piece):
    """
    Returns true if piece is contained in goal
    """
    return all(p in goal for p in piece)


def find_translations(piece: Piece, goal: Piece) -> List[Translation]:
    pmin, pmax = bounding_box([piece])
    gmin, gmax = bounding_box([goal])

    tx = list(range(gmin[0] - pmin[0], gmax[0] - pmax[0] + 1))
    ty = list(range(gmin[1] - pmin[1], gmax[1] - pmax[1] + 1))
    tz = list(range(gmin[2] - pmin[2], gmax[2] - pmax[2] + 1))

    return [Translation(pos) for pos in itertools.product(tx, ty, tz)]


def find_orientations(piece: Piece, target: Piece) -> List[Piece]:
    """
    Generates all possible orientations of a piece such that it is contained in a given target.

    Args:
        piece (Piece): A piece.
        target (Piece): A target piece.

    Returns:
        List[Piece]: A list of all possible orientations of the piece inside the target piece.
    """

    # Apply all possible combinations of translations and rotations to the object
    orientations = []
    for rotated_piece in rotated_pieces(piece):
        for translate in find_translations(rotated_piece, target):
            translated_piece = [translate(pos) for pos in rotated_piece]
            if is_sub_piece(translated_piece, target):
                orientations.append(translated_piece)

    assert len(unique_orientations(orientations)) == len(orientations)
    return orientations


def make_puzzle(pieces: List[Piece], goal: Piece):
    pieces_size = sum(len(piece) for piece in pieces)
    goal_size = len(goal)
    if pieces_size != goal_size:
        print('The size of the goal does not match with the pieces')
        return None

    def var(pos: Position):
        x, y, z = pos
        return Int(f'x_{x}_{y}_{z}')

    variables = [var(pos) for pos in goal]

    constraints = [And(0 <= x, x < len(pieces)) for x in variables]
    for i, piece in enumerate(pieces):
        orientations = find_orientations(piece, goal)
        constraints.append(Or([And([var(pos) == i for pos in orientation]) for orientation in orientations]))

    return variables, constraints


def solve_puzzle(pieces: List[Piece], goal: Piece) -> Optional[List[Piece]]:
    variables, constraints = make_puzzle(pieces, goal)
    solver = Solver()
    solver.add(constraints)
    if solver.check() == sat:
        print('--- solution ---')
        model = solver.model()
        solution = [list() for piece in pieces]
        for pos, x in zip(goal, variables):
            i = int(str(model.evaluate(x)))
            print(f'{x} = {i}')
            solution[i].append(pos)
        return solution
    else:
        print('No solution possible')
    return None


def save_puzzle(pieces: List[Piece], filename: str) -> None:
    def print_position(pos: Position) -> str:
        x, y, z = pos
        return f'{x} {y} {z}'

    def print_piece(piece: Piece) -> str:
        return '   '.join(print_position(pos) for pos in piece)

    text = '\n'.join(print_piece(piece) for piece in pieces)
    Path(filename).write_text(text)


def main():
    cmdline_parser = argparse.ArgumentParser()
    cmdline_parser.add_argument('--pieces', type=str, help='A file containing pieces. Each line contains a piece')
    cmdline_parser.add_argument('--goal', type=str, help='A file containing the coordinates of a 3D object. It is the goal of a puzzle')
    cmdline_parser.add_argument('--make-cube', type=str, help="A string like '4x4x4'. Writes the positions of a cube to a file")
    cmdline_parser.add_argument('--output', type=str, help='A filename')
    cmdline_parser.add_argument('--draw', help='Draws the pieces to the given output file', action='store_true')
    cmdline_parser.add_argument('--solve', help='Solves a puzzle. The specified pieces are fitted into the goal', action='store_true')
    cmdline_parser.add_argument('--smt', help='Save the problem in .smt format', action='store_true')
    cmdline_parser.add_argument('--transform', help='Draws the transformed pieces to the given output file', action='store_true')
    args = cmdline_parser.parse_args()

    if args.draw:
        pieces = load_pieces(args.pieces)
        colors = parse_colors(COLORS)
        text = make_vrml(pieces, colors)
        if not args.output:
            args.output = f'{Path(args.pieces).stem}-pieces.wrl'
        print(f"Saving pieces to file '{args.output}'")
        Path(args.output).write_text(text)

    if args.make_cube:
        X, Y, Z = map(int, args.make_cube.split('x'))
        positions = [f'{x} {y} {z}' for (x, y, z) in cube_positions(X, Y, Z)]
        text = '   '.join(positions)
        if not args.output:
            args.output = f'goals/{args.make_cube}.txt'
        print(f"Saving {args.make_cube} cube to file '{args.output}'")
        Path(args.output).write_text(text)

    if args.smt:
        pieces = load_pieces(args.pieces)
        goal = load_pieces(args.goal)[0]
        variables, constraints = make_puzzle(pieces, goal)
        solver = Solver()
        solver.add(constraints)
        text = solver.to_smt2()
        filename = f'{Path(args.pieces).stem}-{Path(args.goal).stem}.smt'
        Path(filename).write_text(text)

    if args.solve:
        pieces = load_pieces(args.pieces)
        goal = load_pieces(args.goal)[0]
        solution = solve_puzzle(pieces, goal)
        if solution:
            colors = parse_colors(COLORS)
            text = make_vrml(solution, colors, False)
            if not args.output:
                args.output = f'{Path(args.pieces).stem}-{Path(args.goal).stem}.wrl'
            print(f"Saving solution to file '{args.output}'")
            Path(args.output).write_text(text)

            filename = f'{Path(args.pieces).stem}-{Path(args.goal).stem}.txt'
            print(f"Saving solution coordinates to file '{filename}'")
            save_puzzle(solution, filename)

    if args.transform:
        colors = parse_colors(COLORS)
        pieces = load_pieces(args.pieces)
        goal = load_pieces(args.goal)[0]
        for i, piece in enumerate(pieces):
            transformed_pieces = find_orientations(piece, goal)
            text = make_vrml(transformed_pieces, colors)
            filename = f'{Path(args.pieces).stem}-{i}.wrl'
            print(f"Saving {len(transformed_pieces)} piece orientations to file '{filename}'")
            Path(filename).write_text(text)


if __name__ == '__main__':
    main()
