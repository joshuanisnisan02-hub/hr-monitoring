from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

needle = 'showDatePicker(\n'
insert = 'showDatePicker(\n    initialEntryMode: DatePickerEntryMode.calendarOnly,\n'

parts = []
pos = 0
changed = 0
while True:
    idx = text.find(needle, pos)
    if idx < 0:
        parts.append(text[pos:])
        break
    parts.append(text[pos:idx])
    preview = text[idx:idx + 320]
    if 'initialEntryMode:' in preview:
        parts.append(needle)
    else:
        parts.append(insert)
        changed += 1
    pos = idx + len(needle)

text = ''.join(parts)
path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. Date pickers may already be calendar-only.')
else:
    print(f'Set {changed} date picker call(s) to calendar-only mode.')
