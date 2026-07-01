from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

helper = r'''
Future<String> latestContractTypeForEmployee(String employeeId) async {
  if (employeeId.trim().isEmpty) return '';
  final rows = await db
      .from('employee_contracts')
      .select('contract_type, contract_end_date, contract_start_date, created_at')
      .eq('employee_id', employeeId)
      .order('contract_end_date', ascending: false)
      .limit(1);
  if (rows.isEmpty) return '';
  return formatValue((rows.first as Map)['contract_type']).trim();
}

Future<Map<String, dynamic>?> showAddAppointmentDialog(BuildContext context, List<EditOption> employees) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  String contractType = '';
  final appointment = TextEditingController();
  var loadingContractType = false;

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add Appointment'),
        content: SizedBox(
          width: 620,
          child: Form(
            key: formKey,
            child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
              DropdownButtonFormField<String>(
                value: employeeId,
                isExpanded: true,
                decoration: const InputDecoration(labelText: 'Employee Name'),
                items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                validator: (v) => v == null || v.isEmpty ? 'Please select employee' : null,
                onChanged: (value) async {
                  setDialogState(() {
                    employeeId = value;
                    contractType = '';
                    loadingContractType = true;
                  });
                  final latestType = value == null ? '' : await latestContractTypeForEmployee(value);
                  if (!context.mounted) return;
                  setDialogState(() {
                    contractType = latestType;
                    loadingContractType = false;
                  });
                },
              ),
              const SizedBox(height: 14),
              DropdownButtonFormField<String>(
                value: contractType.isEmpty ? null : contractType,
                isExpanded: true,
                decoration: InputDecoration(labelText: 'Contract Type', suffixIcon: loadingContractType ? const Padding(padding: EdgeInsets.all(12), child: SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))) : null),
                items: const [
                  DropdownMenuItem(value: 'Full-time', child: Text('Full-time')),
                  DropdownMenuItem(value: 'Full-time-Probationary', child: Text('Full-time-Probationary')),
                  DropdownMenuItem(value: 'Part-time', child: Text('Part-time')),
                  DropdownMenuItem(value: 'Probationary', child: Text('Probationary')),
                  DropdownMenuItem(value: 'Compliance', child: Text('Compliance')),
                ],
                validator: (v) => v == null || v.isEmpty ? 'Please select contract type' : null,
                onChanged: (value) => setDialogState(() => contractType = value ?? ''),
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: appointment,
                decoration: const InputDecoration(labelText: 'Appointment'),
                validator: (v) => v == null || v.trim().isEmpty ? 'Appointment is required' : null,
              ),
              const SizedBox(height: 8),
              const Text('Contract Type is automatically filled from the selected employee latest contract. You may still change it if needed.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600, fontSize: 12)),
            ]),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!(formKey.currentState?.validate() ?? false)) return;
              Navigator.pop(context, {
                'employee_id': employeeId,
                'category': contractType,
                'appointment_title': appointment.text.trim(),
              });
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  appointment.dispose();
  return result;
}

'''
if 'Future<String> latestContractTypeForEmployee' not in text:
    marker = 'Future<void> editAppointment(BuildContext context,'
    if marker not in text:
        raise SystemExit('editAppointment marker not found.')
    text = text.replace(marker, helper + marker, 1)

start = text.find('Future<void> editAppointment(BuildContext context,')
end = text.find('\n}\n\nclass RankingPage', start)
if start == -1 or end == -1:
    raise SystemExit('editAppointment function block not found.')
end += len('\n}\n')
new_function = r'''Future<void> editAppointment(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];

  final data = isAdd
      ? await showAddAppointmentDialog(context, employees)
      : await showRecordDialog(
          context,
          'Edit Appointment',
          const [
            EditField('category', 'Contract Type', kind: FieldKind.dropdown, required: true, options: [EditOption('Full-time', 'Full-time'), EditOption('Full-time-Probationary', 'Full-time-Probationary'), EditOption('Part-time', 'Part-time'), EditOption('Probationary', 'Probationary'), EditOption('Compliance', 'Compliance')]),
            EditField('appointment_title', 'Appointment', required: true),
          ],
          row,
          readOnlyEmployeeName: linkedEmployeeName(row),
        );

  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_appointments', data['employee_id'], 'appointment')) return;
  await saveRow(context, 'employee_appointments', row?['id'], data, refresh);
}
'''
text = text[:start] + new_function + text[end:]

path.write_text(text, encoding='utf-8')
print('Appointment contract type prefill patch applied to lib/main.dart')
