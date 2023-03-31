#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Tuple

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


def bounding_box(pieces: List[Piece]) -> Tuple[int, int, int]:
    max_x = 0
    max_y = 0
    max_z = 0
    for piece in pieces:
        for (x, y, z) in piece:
            max_x = max(x, max_x)
            max_y = max(y, max_y)
            max_z = max(z, max_z)
    return max_x, max_y, max_z


def make_vrml(pieces: List[Piece], colors: List[RGB]) -> str:
    text = '''#VRML V2.0 utf8

PROTO KUBUS [field SFVec3f translation 0 0 0 field SFColor color 1 0 0] {
Transform {
   translation IS translation
   children [
      Shape{geometry Box { size 0.9 0.9 0.9 } appearance Appearance{ material Material { diffuseColor IS color               }}}
      Shape{geometry Box { size 1.0 1.0 1.0 } appearance Appearance{ material Material { diffuseColor 1 1 1 transparency 0.4 }}}
   ]
}}

'''

    size_x, size_y, size_z = bounding_box(pieces)
    size_x += 2
    size_y += 2

    def piece(i: int) -> str:
        name = f'BLOCK{i}'
        piece = pieces[i]
        color = colors[i % len(colors)]
        translation = (size_x * (i % 4), size_y * (i // 4), 0)
        return make_piece(name, piece, color, translation)

    return text + '\n\n'.join([piece(i) for i in range(len(pieces))])


def cube_positions(X: int, Y: int, Z: int) -> List[Position]:
    return [(x, y, z) for x in range(X) for y in range(Y) for z in range(Z)]


def main():
    cmdline_parser = argparse.ArgumentParser()
    cmdline_parser.add_argument('--pieces', type=str, help='A file containing pieces. Each line contains a piece')
    cmdline_parser.add_argument('--goal', type=str, help='A file containing the coordinates of a 3D object. It is the goal of a puzzle')
    cmdline_parser.add_argument('--make-cube', type=str, help="A string like '4x4x4'. Writes the positions of a cube to a file")
    cmdline_parser.add_argument('--output', type=str, help='A filename')
    cmdline_parser.add_argument('--draw', help='Draws the pieces to the given output file', action='store_true')
    cmdline_parser.add_argument('--solve', help='Solves a puzzle. The specified pieces are fitted into the goal', action='store_true')
    args = cmdline_parser.parse_args()

    if args.draw:
        pieces = load_pieces(args.pieces)
        colors = parse_colors(COLORS)
        text = make_vrml(pieces, colors)
        print(f"Saving pieces to file '{args.output}'")
        Path(args.output).write_text(text)

    if args.make_cube:
        X, Y, Z = map(int, args.make_cube.split('x'))
        positions = [f'{x} {y} {z}' for (x, y, z) in cube_positions(X, Y, Z)]
        text = '   '.join(positions)
        print(f"Saving {args.make_cube} cube to file '{args.output}'")
        Path(args.output).write_text(text)

    if args.solve:
        print('Solving is not implemented yet')


if __name__ == '__main__':
    main()
