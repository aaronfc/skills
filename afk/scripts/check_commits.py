import argparse
import subprocess


parser = argparse.ArgumentParser(description='List branch commits and reject missing bodies.')
parser.add_argument('base', help='PR base ref; checks base..HEAD')
args = parser.parse_args()
commits = subprocess.check_output(
    ['git', 'rev-list', '--reverse', f'{args.base}..HEAD'], text=True
).splitlines()
missing = False
for commit in commits:
    subject, body = subprocess.check_output(
        ['git', 'show', '-s', '--format=%s%x00%b', commit], text=True
    ).split('\0', 1)
    suffix = '' if body.strip() else ' (missing body)'
    print(f'{commit[:12]} {subject}{suffix}')
    missing |= not body.strip()
raise SystemExit(1 if missing else 0)
