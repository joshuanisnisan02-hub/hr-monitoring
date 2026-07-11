from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# The previous role patch referenced IncidentReportPage, but the IR module script
# did not insert the class on this local copy. This script adds the module and
# also removes invalid const usage when the class was not yet known during parse