from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

replacements = {
    "employeeImportDate(r['birthdate'])": "employeeImportDate(r['birthdate'] ?? '')",
    "employeeImportDate(r['employment_date'])": "employeeImportDate(r['employment_date'] ?? '')",
}

changed = False
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed = True

if not changed:
    print('Employee import nullable date fix is already applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Employee import nullable date fix applied to lib/main.dart')
