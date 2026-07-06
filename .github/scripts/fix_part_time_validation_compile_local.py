from pathlib import Path

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('Run this from the project root.')

s = p.read_text(encoding='utf-8-sig')
old = s

s = s.replace(
    "  bool get isPartTimeEmployee => employeeType == 'part_time';",
    "  bool isPartTimeEmployee() => employeeType == 'part_time';",
)

s = s.replace('!isPartTimeEmployee', '!isPartTimeEmployee()')
s = s.replace('isPartTimeEmployee ? null', 'isPartTimeEmployee() ? null')
s = s.replace('return isPartTimeEmployee ? null', 'return isPartTimeEmployee() ? null')

# Clean up if this script is run more than once.
while 'isPartTimeEmployee()()' in s:
    s = s.replace('isPartTimeEmployee()()', 'isPartTimeEmployee()')

p.write_text(s, encoding='utf-8')
print('Fixed Add Employee part-time validation compile issue.' if s != old else 'No changes needed.')
