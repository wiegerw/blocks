#!/usr/bin/env python3

from typing import List, Tuple
from pathlib import Path

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
'''


BLOCKS = '''
  0 0 0   0 1 0   1 0 0   1 1 0   2 0 0   2 1 0
  0 0 0   0 1 0   1 0 0   1 0 1   2 0 0   2 1 0
  0 0 0   0 1 0   1 0 0   1 1 0   2 1 0   2 1 1
  0 0 0   0 1 0   1 2 0   1 1 0   2 0 0   2 1 0
  0 1 1   0 1 0   1 0 0   1 1 0   2 0 0   2 1 0
  0 0 0   0 1 0   1 0 0   1 1 0   2 2 0   2 1 0
  0 2 0   0 1 0   1 1 0   1 1 1   2 0 0   2 1 0
  0 0 0   0 1 0   1 1 1   1 1 0   2 2 0   2 1 0
  0 2 0   0 1 0   1 1 0   1 0 0   2 1 1   2 1 0
  0 0 0   0 1 0   1 2 0   1 1 0   2 1 1   2 1 0
  0 0 0   0 1 0   1 1 1   1 1 0
'''


def parse_colors(text: str) -> List[Tuple[int, int, int]]:
    """
    Parses a string of comma-separated RGB color values into a list of color triples.

    Args:
        text (str): A string of comma-separated RGB color values.

    Returns:
        List[Tuple[int, int, int]]: A list of color triples, where each triple is a tuple of
        three integers representing the red, green, and blue values of a color.
    """
    # Split the text into a list of lines
    lines = text.strip().split('\n')

    # Split each line into a list of color values and convert them to integers
    colors = [tuple(map(int, line.split(','))) for line in lines]

    return colors


from typing import List, Tuple


def parse_blocks(text: str) -> List[List[Tuple[int, int, int]]]:
    """
    Parses a string of space-separated RGB color values into a list of color block lists.

    Args:
        text (str): A string of space-separated RGB color values.

    Returns:
        List[List[Tuple[int, int, int]]]: A list of color block lists, where each block list is a list of
        color triples, and each color triple is a tuple of three integers representing the red, green, and blue
        values of a color.
    """
    # Split the text into a list of lines
    lines = text.strip().split('\n')

    # Split each line into a list of color values, convert them to integers, and group them into blocks
    blocks = [[tuple(map(int, lines[i].split()[j:j + 3])) for j in range(0, len(lines[i].split()), 3)] for i in range(len(lines))]

    return blocks


def make_vrml(blocks: List[List[Tuple[int, int, int]]], colors: List[Tuple[int, int, int]]) -> str:
    vrml_text = '''#VRML V2.0 utf8

PROTO KUBUS [field SFVec3f translation 0 0 0 field SFColor color 1 0 0] {
Transform {
   translation IS translation
   children [
      Shape{geometry Box { size 0.9 0.9 0.9 } appearance Appearance{ material Material { diffuseColor IS color               }}}
      Shape{geometry Box { size 1.0 1.0 1.0 } appearance Appearance{ material Material { diffuseColor 1 1 1 transparency 0.4 }}}
   ]
}}

'''
    block_text = '''DEF BLOCK Transform {
   translation X 0 0
   children [
CUBES
   ]}
    '''

    def make_cube(point, color):
        x, y, z = point
        r, g, b = color
        return f'      KUBUS {{ translation {x} {y} {z} color {r / 255} {g / 255} {b / 255} }}'

    def make_block(i: int) -> str:
        points = blocks[i]
        color = colors[i]
        cubes = '\n'.join([make_cube(point, color) for point in points])
        return block_text.replace('CUBES', cubes).replace('X', str(i * 4)).replace('BLOCK', f'BLOCK{i}')

    return vrml_text + '\n\n'.join([make_block(i) for i in range(len(blocks))])


def main():
    colors = parse_colors(COLORS)
    blocks = parse_blocks(BLOCKS)
    vrml = make_vrml(blocks, colors)
    print(vrml)


if __name__ == '__main__':
    main()
