from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

helper = r'''
String normalizeContractTypeOption(Object? value) {
  final raw = formatValue(value).trim();
  final key = raw.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), ' ').replaceAll(RegExp(r'\s+'), ' ').trim();
  if (key == 'full time' || key == 'fulltime') return 'Full-time';
  if (key == 'full time probationary' || key == 'fulltime probationary') return 'Full-time-Probationary';
  if (key == 'part time' || key == 'parttime') return 'Part-time';
  if (key == 'probationary') return 'Probationary';
  if (key == 'compliance') return 'Compliance';
  return raw == '-' ? '' : raw;
}

Future<String> latestContractTypeForEmployee(String employeeId) async {
  final id = employeeId.trim();
  if (id.isEmpty) return '';
  try {
    final rows = await db
        .from('employee_contracts')
        .select('contract_type, contract_end_date')
        .eq('employee_id', id)
        .order('contract_end_date', ascending: false)
        .limit(1);
    if (rows.isEmpty) return '';
    return normalizeContractTypeOption((rows.first as Map)['contract_type']);
  } catch (_) {
    return '';
  }
}

Future<Map<String, dynamic>?> showAddAppointmentDialog(BuildContext context, List<EditOption> employees) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  String selectedEmployeeName = '';
  String contractType = '';
  final appointment = TextEditingController();
  var loadingContractType = false;

  const contractTypes = <String>['Full-time', 'Full-time-Probationary', 'Part-time', 'Probationary', 'Compliance'];

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) {
        void loadContractTypeFor(String id) {
          setDialogState(() {
            contractType = '';
            loadingContractType = true;
          });
          latestContractTypeForEmployee(id).then((latest) {
            if (!context.mounted || employeeId != id) return;
            setDialogState(() {
              contractType = contractTypes.contains(latest) ? latest : '';
              loadingContractType = false;
            });
          });
        }

        void chooseEmployee(EditOption option) {
          setDialogState(() {
            employeeId = option.value;
            selectedEmployeeName = option.label;
          });
          loadContractTypeFor(option.value);
        }

        return AlertDialog(
          title: const Text('Add Appointment'),
          content: SizedBox(
            width: 760,
            child: Form(
              key: formKey,
              child: SingleChildScrollView(
                child: Wrap(spacing: 14, runSpacing: 14, children: [
                  SizedBox(
                    width: 354,
                    child: Autocomplete<EditOption>(
                      displayStringForOption: (option) => option.label,
                      optionsBuilder: (textEditingValue) {
                        final sortedEmployees = uniqueOptions(employees).toList()
                          ..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
                        final query = textEditingValue.text.trim().toLowerCase();
                        if (query.isEmpty) return sortedEmployees;
                        final normalizedQuery = normalizeName(query);
                        return sortedEmployees.where((option) {
                          final label = option.label.toLowerCase();
                          final normalizedLabel = normalizeName(option.label);
                          return label.contains(query) || normalizedLabel.contains(normalizedQuery);
                        });
                      },
                      onSelected: chooseEmployee,
                      fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: 'Employee Name',
                          hintText: 'Select or type employee name',
                          suffixIcon: Icon(Icons.search_rounded),
                        ),
                        validator: (_) => employeeId == null || employeeId!.isEmpty ? 'Please select employee from the list' : null,
                        onChanged: (value) {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees).where((option) => option.label.toLowerCase() == typed).toList();
                          if (exact.isNotEmpty) {
                            chooseEmployee(exact.first);
                          } else {
                            setDialogState(() {
                              employeeId = null;
                              selectedEmployeeName = '';
                              contractType = '';
                              loadingContractType = false;
                            });
                          }
                        },
                      ),
                      optionsViewBuilder: (context, onSelected, options) => Align(
                        alignment: Alignment.topLeft,
                        child: Material(
                          elevation: 6,
                          borderRadius: BorderRadius.circular(14),
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 520, maxHeight: 320),
                            child: ListView.separated(
                              padding: EdgeInsets.zero,
                              shrinkWrap: true,
                              itemCount: options.length,
                              separatorBuilder: (_, __) => const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final option = options.elementAt(index);
                                return ListTile(
                                  dense: true,
                                  title: Text(option.label, overflow: TextOverflow.ellipsis),
                                  onTap: () => onSelected(option),
                                );
                              },
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(
                    width: 354,
                    child: DropdownButtonFormField<String>(
                      value: contractTypes.contains(contractType) ? contractType : null,
                      isExpanded: true,
                      decoration: InputDecoration(
                        labelText: 'Contract Type',
                        suffixIcon: loadingContractType
                            ? const Padding(
                                padding: EdgeInsets.all(12),
                                child: SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
                              )
                            : null,
                      ),
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
                  ),
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: appointment,
                      decoration: const InputDecoration(labelText: 'Appointment'),
                      validator: (v) => v == null || v.trim().isEmpty ? 'Appointment is required' : null,
                    ),
                  ),
                  SizedBox(
                    width: 728,
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)),
                      child: Text(
                        selectedEmployeeName.isEmpty
                            ? 'Search and select an employee. Contract Type will auto-fill from the employee latest contract record.'
                            : 'Selected: $selectedEmployeeName. Contract Type is based on the latest contract record and can still be changed if needed.',
                        style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                ]),
              ),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                if (!(formKey.currentState?.validate() ?? false)) return;
                Navigator.pop(context, {
                  'employee_id': emptyToNull(employeeId),
                  'category': contractType,
                  'appointment_title': appointment.text.trim(),
                });
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    ),
  );
  appointment.dispose();
  return result;
}

'''

# Remove older helper/dialog versions if present, then insert the fixed version before editAppointment.
start = text.find('String normalizeContractTypeOption(Object? value)')
if start == -1:
    start = text.find('Future<String> latestContractTypeForEmployee')
if start != -1:
    end = text.find('Future<void> editAppointment(BuildContext context,', start)
    if end == -1:
        raise SystemExit('Could not find editAppointment after existing appointment helper.')
    text = text[:start] + text[end:]

marker = 'Future<void> editAppointment(BuildContext context,'
if marker not in text:
    raise SystemExit('editAppointment marker not found.')
text = text.replace(marker, helper + marker, 1)

# Replace editAppointment to call the custom autocomplete add dialog.
start = text.find('Future<void> editAppointment(BuildContext context,')
end = text.find('\n}\n\nclass RankingPage', start)
if start == -1 or end == -1:
    raise SystemExit('editAppointment block not found.')
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
print('Appointment employee autocomplete and contract type prefill fixed in lib/main.dart')
