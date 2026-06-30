from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()
old = "title: 'Ranking',"
new = "title: '2026 Faculty Ranking',"
if new not in s:
    if old not in s:
        raise SystemExit('Ranking title line not found')
    s = s.replace(old, new, 1)
p.write_text(s)
