from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Make page creation non-const-safe even while the class is being inserted.
text = text.replace('const IncidentReportPage()', 'IncidentReportPage()')

# Add the Incident Report loader if the first