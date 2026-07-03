from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8')
original = text

text = text.replace("""          addLabel: 'Add Appointment',
          allowAdd: false,
          reportTitle: 'Appointment Reference Report',""", """          addLabel: 'Add Appointment',
          reportTitle: 'Appointment Reference Report',""", 1)

text = text.replace("""          onView: viewAppointment,
          onEdit: editAppointment,""", """          onAdd: (ctx, refresh) => editAppointment(ctx, null, refresh),
          onView: viewAppointment,
          onEdit: editAppointment,""", 1)

old = r'''Future<void> editAppointment(BuildContext context, Map<String, dynamic> row,
    VoidCallback refresh) async {
  final data = await showRecordDialog(
    context,
    'Edit Appointment',
    const [
      EditField('category', 'Type',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Full-time', 'Full-time'),
          EditOption('Full-time-Probationary', 'Full-time-Probationary'),
          EditOption('Part-time', 'Part-time'),
          EditOption('Probationary', 'Probationary'),
          EditOption('Compliance', 'Compliance')
          ]),
      EditField('appointment_title', 'Appointment', required: true),
    ],
    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  await saveRow(context, 'employee_appointments', row['id'], data, refresh);
}
'''

new = r'''Future<void> editAppointment(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final fields = <EditField>[
    if (isAdd)
      EditField('employee_id', 'Employee Name',
          kind: FieldKind.dropdown,
          required: true,
          options: await employeeOptions()),
    const EditField('category', 'Type',
        kind: FieldKind.dropdown,
        required: true,
        options: [
          EditOption('Full-time', 'Full-time'),
          EditOption('Full-time-Probationary', 'Full-time-Probationary'),
          EditOption('Part-time', 'Part-time'),
          EditOption('Probationary', 'Probationary'),
          EditOption('Compliance', 'Compliance')
        ]),
    const EditField('appointment_title', 'Appointment', required: true),
  ];

  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Appointment' : 'Edit Appointment',
    fields,
    normalizeRow(row ?? {}),
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd &&
      !await ensureNoEmployeeDuplicate(
          context, 'employee_appointments', data['employee_id'], 'appointment')) {
    return;
  }
  await saveRow(context, 'employee_appointments', row?['id'], data, refresh);
}
'''

if old not in text:
    raise SystemExit('Could not find the current editAppointment block. The file may already be updated or has changed.')
text = text.replace(old, new, 1)

if text == original:
    print('No changes applied. Add Appointment may already be enabled.')
else:
    path.write_text(text, encoding='utf-8')
    print('Enabled Add Appointment button and ranking-style employee selection.')

