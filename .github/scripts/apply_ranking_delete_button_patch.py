from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = """              showDelete: false,
              onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
"""
new = """              showDelete: true,
              onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
"""

if old not in text:
    if "showDelete: true," in text and "ranking_applications" in text:
        print('Ranking delete button is already enabled.')
        raise SystemExit(0)
    raise SystemExit('Ranking delete button block was not found.')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Ranking delete button patch applied to lib/main.dart')
