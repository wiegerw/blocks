# blocks

This page contains a python script `blocks.py` for solving 2D and 3D 
block puzzles. The solver can for example assemble a 4x4x4 cube from the
pieces below.

![](images/half_cube.png)

## Features

* Solve puzzles using the Z3 solver
* Draw pieces and solutions in VRML format
* Save the puzzles in SMT format

## Puzzle format

A puzzle is stored in a simple textual format. Each line contains a
piece of the puzzle. A line contains the 3D coordinates of the cubes of
a piece. Hence, a line consists of triples of integer values.

The `pieces` directory contains several examples of puzzles.
They can be visualized using the `draw_pieces` script. A puzzle
can be solved using a call like this:

```
python3 blocks.py --solve --pieces="pieces/offroad_cube.txt" --goal="goals/4x4x4.txt"
```

The goal is a file in the same format as the pieces. It should contain
one piece only, which is the desired configuration of the puzzle.
Note that some puzzles are too large to solve using Z3.

## links

https://diypuzzles.wordpress.com/tag/4x4x4-cube/

https://puzzlewillbeplayed.com/444/Gemini/

https://en.wikipedia.org/wiki/Tetromino

https://en.wikipedia.org/wiki/Pentomino

https://en.wikipedia.org/wiki/Hexomino

https://www.youtube.com/watch?v=Jr36wC9cbHI