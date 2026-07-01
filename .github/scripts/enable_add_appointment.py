from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

text = text.replace("          allowAdd: false,\n", "")

if "onAdd: (ctx, refresh) => editAppointment(ctx, null, refresh)," not in text:
    text = text.replace(
        "          onView: viewAppointment,\n          onEdit: editAppointment,",
        "          onAdd: (ctx, refresh) => editAppointment(ctx, null, refresh),\n          onView: viewAppointment,\n          onEdit: editAppointment,",
        1,
    )

old_function = r'''Future<void> editAppointment(BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final data = await showRecordDialog(
    context,
    'Edit Appointment',
    const [
      EditField('category', 'Type', kind: FieldKind.dropdown, required: true, options: [EditOption('Full-time', 'Full-time'), EditOption('Probationary', 'Probationary')]),
      EditField('appointment_title', 'Appointment', required: true),
    ],
    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  await saveRow(context, 'employee_appointments', row['id'], data, refresh);
}
'''

new_function = r'''Future<void> editAppointment(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Appointment' : 'Edit Appointment',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('category', 'Contract Type', kind: FieldKind.dropdown, required: true, options: [EditOption('Full-time', 'Full-time'), EditOption('Full-time-Probationary', 'Full-time-Probationary'), EditOption('Part-time', 'Part-time'), EditOption('Probationary', 'Probationary'), EditOption('Compliance', 'Compliance')]),
      const EditField('appointment_title', 'Appointment', required: true),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_appointments', data['employee_id'], 'appointment')) return;
  await saveRow(context, 'employee_appointments', row?['id'], data, refresh);
}
'''

if old_function in text:
    text = text.replace(old_function, new_function, 1)
elif "Future<void> editAppointment(BuildContext context, Map<String, dynamic>? row" in text:
    pass
else:
    # More flexible replacement for versions where Contract Type was already changed.
    start = text.find('Future<void> editAppointment(BuildContext context,')
    end = text.find('\n}\n\nclass RankingPage', start)
    if start == -1 or end == -1:
        raise SystemExit('editAppointment function was not found.')
    end += len('\n}\n')
    text = text[:start] + new_function + text[end:]

path.write_text(text, encoding='utf-8')
print('Add Appointment flow enabled in lib/main.dart')
