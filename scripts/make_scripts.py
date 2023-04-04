#!/usr/bin/env python3

import io
import os
from pathlib import Path


def make_script(folder, options=''):
    out = io.StringIO()
    for path in sorted(Path(folder).glob('*.txt')):
        out.write(f'python3 blocks.py --draw --pieces="{path}" {options}\n')
    filename = f'draw_{folder}'
    print(f'Saving {filename}')
    Path(filename).write_text(out.getvalue())


if __name__ == '__main__':
    os.chdir('..')

    make_script('goals')
    make_script('puzzles', '--grid')
    make_script('solutions')
