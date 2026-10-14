#!/usr/bin/env python3
"""Install both PaperThread skills as portable directories, without symlinks."""
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('paper-reader', 'knowledge-curator')


def files(directory):
    return {p.relative_to(directory): p.read_bytes() for p in directory.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'}


def install(root, destination, update=False):
    """Check every collision before changing either skill; keep replaced copies."""
    root, destination = Path(root), Path(destination)
    pending = []
    for name in NAMES:
        source, target = root / 'skills' / name, destination / name
        if not (source / 'SKILL.md').is_file():
            raise ValueError('Missing skill source: ' + str(source))
        if target.is_symlink() and target.resolve() == source.resolve():
            continue  # Existing project installations remain usable.
        exists = target.exists() or target.is_symlink()
        if exists:
            if not target.is_symlink() and target.is_dir() and files(source) == files(target):
                continue
            if not update:
                raise ValueError('Already exists with different content: ' + str(target)
                                 + '\nUse --update to back up and replace these two named skills.')
        pending.append((source, target, exists))
    destination.mkdir(parents=True, exist_ok=True)
    backup = None
    for source, target, exists in pending:
        if exists:
            if backup is None:
                stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
                backup = destination.parent / 'paperthread-skill-backups' / stamp
                backup.mkdir(parents=True)
            target.rename(backup / target.name)
        try:
            shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
        except Exception:
            if target.exists():
                shutil.rmtree(target)
            if exists:
                (backup / target.name).rename(target)
            raise
    return backup


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', action='store_true', help='Install into ~/.agents/skills instead of this project')
    parser.add_argument('--update', action='store_true', help='Back up and replace existing copies when they differ')
    args = parser.parse_args()
    destination = (Path.home() if args.user else ROOT) / '.agents' / 'skills'
    try:
        backup = install(ROOT, destination, args.update)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print('PaperThread skills ready: ' + str(destination))
    for name in NAMES:
        print('  ' + name)
    if backup:
        print('Previous copies saved to: ' + str(backup))
    print('Open the PaperThread project in your agent. Restart its session if skills are not listed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
