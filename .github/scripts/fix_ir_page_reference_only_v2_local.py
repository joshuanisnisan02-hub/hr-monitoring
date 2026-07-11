from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root.')

text = path.read_text(encoding='utf-8-sig')
original = text

text = text.replace('const IncidentReportPage()', 'IncidentReportPage()')
text = text.replace('const [\n            NavItem(\'Incident Report\'', '[\n            const NavItem(\'Incident Report\'')

path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. IR page reference may already be fixed.')
else:
    print('Removed const from IncidentReportPage references.')
