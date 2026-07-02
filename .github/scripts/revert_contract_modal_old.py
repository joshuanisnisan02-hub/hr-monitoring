from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

new_edit = '''Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showContractDialog(
    context,
    isAdd ? await activeEmployeeOptions() : const <EditOption>[],
    await contractTypeOptions(),
    row,
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}
'''
old_edit = '''Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await activeEmployeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Contract' : 'Edit Contract',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('contract_type', 'Contract Type'),
      const EditField('contract_start_date', 'Start Date', kind: FieldKind.date),
      const EditField('duration_months', 'Duration In Months', kind: FieldKind.integer),
      const EditField('contract_end_date', 'End Date', kind: FieldKind.date),
      const EditField('attachment_url', 'Attachment URL'),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived'), EditOption('Resigned', 'Resigned')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}
'''
if new_edit in s:
    s = s.replace(new_edit, old_edit, 1)
elif old_edit not in s:
    raise SystemExit('editContract block not found')

start = s.find('String contractStatusFromEndDate(')
end = s.find('class SelectedLicenseInput {', start)
if start != -1 and end != -1:
    s = s[:start] + s[end:]

p.write_text(s)
