from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

old = "textBox('Appointment', appointment),"
new = "textBox('Appointment', appointment, readOnly: true),"
if old not in s and new not in s:
    raise SystemExit('Appointment field line not found')
s = s.replace(old, new, 1)

p.write_text(s)
