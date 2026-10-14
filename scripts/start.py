#!/usr/bin/env python3
"""Shared, dependency-free entry point for the desktop launchers."""
import os
from pathlib import Path
import sys


def main():
    if sys.version_info < (3, 10):
        print('PaperThread requires Python 3.10 or newer. Current: ' + sys.version.split()[0], file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    sys.path.insert(0, str(root))
    from paper import main as paper_main
    sys.argv = ['paper.py', 'serve', *sys.argv[1:]]
    return paper_main()


if __name__ == '__main__':
    sys.exit(main())
