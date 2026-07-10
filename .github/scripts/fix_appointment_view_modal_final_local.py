from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Keep Appointment Type choices same as before only.
start = text.find('const appointmentCategoryOptions = <EditOption>[')
if start >= 0:
    end = text.find('];', start)
    if end >= 0:
        end += 2
        text = (text[:start] + """const appointmentCategoryOptions = <EditOption>[
  EditOption('FULL-TIME', 'FULL-TIME'),
  EditOption('PART-TIME', 'PART-TIME'),
  EditOption('PROBATIONARY', 'PROBATIONARY'),
  EditOption('COMPLIANCE', 'COMPLIANCE'),
];""" + text[end:])
text = text.replace("  EditOption('ADMINISTRATIVE', 'ADMINISTRATIVE'),\n", '')
text = text.replace("  EditOption('ACADEMIC', 'ACADEMIC'),\n", '')

# Replace the whole viewAppointment function so it follows the Add/Edit Appointment fields.
def matching_brace(src: str, brace_index: int) -> int:
    depth = 0
    in_single = False
    in_double = False
    escaped = False
    for i in range(brace_index, len(src)):
        ch = src[i]
        if in_single:
            if ch == '\\' and not escaped:
                escaped = True
                continue
            if ch == "'" and not escaped:
                in_single = False
            escaped = False
            continue
        if in_double:
            if ch == '\\' and not escaped:
                escaped = True
                continue
            if ch == '"' and not escaped:
                in_double = False
            escaped = False
            continue
        if ch == "'":
            in_single = True
            continue
        if ch == '"':
            in_double = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1

fn_start = text.find('Future<void> viewAppointment(')
if fn_start < 0:
    raise SystemExit('Could not find viewAppointment function.')
brace = text.find('{', fn_start)
fn_end = matching_brace(text, brace)
if fn_end < 0:
    raise SystemExit('Could not find the end of viewAppointment function.')
line_end = text.find('\n', fn_end)
if line_end < 0:
    line_end = fn_end + 1

replacement = r'''Future<void> viewAppointment(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final titleName = formatValue(normalized['employee_name']).trim().isEmpty ||
          formatValue(normalized['employee_name']) == '-'
      ? linkedEmployeeName(normalized)
      : formatValue(normalized['employee_name']);

  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(titleName),
      content: SizedBox(
        width: 850,
        child: SingleChildScrollView(
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const DialogSectionTitle('Appointment Information'),
                Wrap(spacing: 10, runSpacing: 10, children: [
                  DetailTile('Employee Name', titleName),
                  DetailTile('Appointment Type',
                      formatDetailValue(normalized['category'], 'category')),
                  DetailTile('Appointment', formatDetailValue(
                      normalized['appointment_title'], 'appointment_title')),
                  DetailTile('Other Duties', formatDetailValue(
                      normalized['other_duties'], 'other_duties')),
                  DetailTile('Type', formatDetailValue(
                      normalized['appointment_type'], 'appointment_type')),
                  AttachmentPdfTile(
                      'Appointment PDF', normalized['attachment_url']),
                ]),
              ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close')),
      ],
    ),
  );
}

'''
text = text[:fn_start] + replacement + text[line_end + 1:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Appointment view modal may already be fixed.')
else:
    print('Fixed Appointment view modal to match Add/Edit Appointment fields.')
