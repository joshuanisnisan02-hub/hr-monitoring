from pathlib import Path
import re

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('Run from project root')
s = p.read_text(encoding='utf-8-sig')
o = s

# Appointment Type should be same as the previous/core list only.
# Remove ACADEMIC and ADMINISTRATIVE from the searchable Appointment Type choices.
start = s.find('const appointmentCategoryOptions = <EditOption>[')
if start >= 0:
    end = s.find('];', start)
    if end >= 0:
        end += 2
        replacement = """const appointmentCategoryOptions = <EditOption>[
  EditOption('FULL-TIME', 'FULL-TIME'),
  EditOption('PART-TIME', 'PART-TIME'),
  EditOption('PROBATIONARY', 'PROBATIONARY'),
  EditOption('COMPLIANCE', 'COMPLIANCE'),
];"""
        s = s[:start] + replacement + s[end:]

# Also remove any stray old dropdown items if they were inserted inline elsewhere.
s = s.replace("  EditOption('ADMINISTRATIVE', 'ADMINISTRATIVE'),\n", '')
s = s.replace("  EditOption('ACADEMIC', 'ACADEMIC'),\n", '')

# Revise the Appointment view modal to match Add Appointment fields.
# Fields should be: Employee, Appointment Type, Appointment, Other Duties, Type, PDF.
view_start = s.find('Future<void> viewAppointment(')
if view_start >= 0:
    next_start = s.find('Future<void>', view_start + 10)
    if next_start < 0:
        next_start = s.find('class ', view_start + 10)
    block = s[view_start:next_start]
    if 'Appointment PDF' not in block or "'Appointment Type': 'category'" not in block:
        # Replace detailSection field map variants.
        block = re.sub(
            r"detailSection\('Appointment Information',\s*normalized,\s*const\s*\{[\s\S]*?\}\),",
            """detailSection('Appointment Information', normalized, const {
      'Employee Name': 'employee_name',
      'Appointment Type': 'category',
      'Appointment': 'appointment_title',
      'Other Duties': 'other_duties',
      'Type': 'appointment_type',
    }),
    const SizedBox(height: 10),
    AttachmentPdfTile('Appointment PDF', normalized['attachment_url']),""",
            block,
            count=1,
        )
        s = s[:view_start] + block + s[next_start:]

# If viewAppointment function was not found or regex failed, add a targeted fallback.
s = s.replace(
    """'Type': 'category',
      'Appointment': 'appointment_title',""",
    """'Appointment Type': 'category',
      'Appointment': 'appointment_title',
      'Other Duties': 'other_duties',
      'Type': 'appointment_type',""",
    1,
)

p.write_text(s, encoding='utf-8')
if s == o:
    print('No changes applied. Appointment type list and view modal may already be revised.')
else:
    print('Revised Appointment Type list and updated Appointment view modal.')
