from pathlib import Path

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('Run from project root')
s = p.read_text(encoding='utf-8-sig')
o = s

# The current error is only from using const before IncidentReportPage when the
# class is not compile-time const in the user's local file. Remove const in the
# page list and conditional page list.
s = s.replace('const IncidentReportPage()', 'IncidentReportPage()')
s = s.replace('const IncidentReport