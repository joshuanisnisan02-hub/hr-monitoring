from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

replacements = {
"""    final inserts = <Map<String, dynamic>>[];
    final ambiguous = <String>[];
""": """    var notFound = 0;
    final ambiguous = <String>[];
""",
"""      } else {
        data['employment_status'] ??= 'active';
        data['employee_type'] ??= 'full_time';
        data['is_faculty'] = true;
        inserts.add(data);
      }
""": """      } else {
        notFound++;
      }
""",
"""Matched updates: ${updates.length}\\nNew employees to insert: ${inserts.length}\\nNo changes needed: $noChanges\\nSkipped invalid: $invalid\\nSkipped ambiguous: ${ambiguous.length}\\n\\nOnly blank/missing fields will be filled. Existing non-empty values will not be overwritten. Government IDs and photos are not imported.""": """Matched updates: ${updates.length}\\nEmployees not found in system: $notFound\\nNo changes needed: $noChanges\\nSkipped invalid: $invalid\\nSkipped ambiguous: ${ambiguous.length}\\n\\nOnly blank/missing fields will be filled. Existing non-empty values will not be overwritten. No new employee records will be added.""",
"""    for (final row in inserts) {
      await db.from('employees').insert(row);
    }
""": """""",
"""Employee import completed. Updated ${updates.length}, inserted ${inserts.length}, skipped ${ambiguous.length + invalid}.""": """Employee import completed. Updated ${updates.length}, not found $notFound, skipped ${ambiguous.length + invalid}.""",
"""Import tbl_employee CSV to fill missing employee profile fields. Existing non-empty values are not overwritten.""": """Import tbl_employee CSV to fill missing profile fields for existing employees only. No new records are added.""",
}

changed = False
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed = True

if "final inserts = <Map<String, dynamic>>[]" in text or "insert(row)" in text:
    raise SystemExit('No-insert patch could not remove all insert logic. Please inspect lib/main.dart.')

if changed:
    path.write_text(text, encoding='utf-8')
    print('Employee import no-insert fix applied to lib/main.dart')
else:
    print('Employee import no-insert fix is already applied.')
