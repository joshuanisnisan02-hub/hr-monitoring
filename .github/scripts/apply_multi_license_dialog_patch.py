from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Add dynamic license option loader after employeeOptions.
if 'Future<List<String>> licenseNameOptions() async' not in s:
    s = s.replace(
        """Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
}
""",
        """Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
}

Future<List<String>> licenseNameOptions() async {
  const defaults = <String>[
    'Licensed Professional Teacher (LPT)',
    'Registered Criminologist (RCRIM)',
    'Registered Nurse (RN)',
    'Registered Social Worker (RSW)',
    'Registered Librarian (RL)',
    'Real Estate Broker (REB)',
    'Professional Regulation Commission (PRC) License',
  ];
  final seen = <String>{};
  final out = <String>[];
  void addName(String name) {
    final clean = name.trim();
    if (clean.isEmpty) return;
    final key = clean.toLowerCase();
    if (seen.add(key)) out.add(clean);
  }
  for (final item in defaults) {
    addName(item);
  }
  try {
    final rows = await db.from('employee_licenses').select('license_name').order('license_name').limit(3000);
    for (final r in rows) {
      addName('${r['license_name'] ?? ''}');
    }
  } catch (_) {}
  return out;
}
""",
        1,
    )

old_edit_license = """Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add License' : 'Edit License',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('license_name', 'License Name', required: true),
      const EditField('license_number', 'License Number'),
      const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      const EditField('attachment_url', 'Attachment URL'),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_licenses', data['employee_id'], 'license')) return;
  await saveRow(context, 'employee_licenses', row?['id'], data, refresh);
}
"""

new_edit_license = """Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddLicenseDialog(context, await employeeOptions(), await licenseNameOptions());
    if (records == null || records.isEmpty) return;
    try {
      await db.from('employee_licenses').insert(records);
      showSnack(context, records.length == 1 ? 'License record added.' : '${records.length} license records added.');
      refresh();
    } catch (e) {
      showSnack(context, 'Add License Failed: $e');
    }
    return;
  }

  final data = await showRecordDialog(
    context,
    'Edit License',
    const [
      EditField('license_name', 'License Name', required: true),
      EditField('license_number', 'License Number'),
      EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      EditField('attachment_url', 'Attachment URL'),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  await saveRow(context, 'employee_licenses', row['id'], data, refresh);
}
"""

if old_edit_license not in s:
    raise SystemExit('Old editLicense block not found')
s = s.replace(old_edit_license, new_edit_license, 1)

# Add selected license model and custom add dialog before editLicense.
if 'class SelectedLicenseInput' not in s:
    custom_dialog = r'''
class SelectedLicenseInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  String status = '';

  SelectedLicenseInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
  }
}

String licenseStatusFromExpiry(String text) {
  final value = text.trim();
  if (value.isEmpty) return '';
  final parsed = DateTime.tryParse(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final expiry = DateTime(parsed.year, parsed.month, parsed.day);
  if (expiry.isBefore(today)) return 'Expired';
  if (expiry.difference(today).inDays <= 90) return 'For Renewal';
  return 'Active';
}

Future<List<Map<String, dynamic>>?> showAddLicenseDialog(BuildContext context, List<EditOption> employees, List<String> licenses) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  final selected = <String, SelectedLicenseInput>{};

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add License'),
        content: SizedBox(
          width: 900,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                SizedBox(
                  width: 430,
                  child: DropdownButtonFormField<String>(
                    value: employeeId,
                    isExpanded: true,
                    hint: const Text('Select Employee'),
                    decoration: const InputDecoration(labelText: 'Employee Name'),
                    items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                    validator: (v) => v == null || v.isEmpty ? 'Please select employee' : null,
                    onChanged: (v) => setDialogState(() => employeeId = v),
                  ),
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('License Checklist'),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    for (final license in licenses)
                      SizedBox(
                        width: 278,
                        child: CheckboxListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          controlAffinity: ListTileControlAffinity.leading,
                          title: Text(license, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
                          value: selected.containsKey(license),
                          onChanged: (checked) => setDialogState(() {
                            if (checked == true) {
                              selected.putIfAbsent(license, () => SelectedLicenseInput(license));
                            } else {
                              selected.remove(license)?.dispose();
                            }
                          }),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('Selected Licenses'),
                if (selected.isEmpty)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                    child: const Text('Select one or more licenses above. The selected licenses will appear here as a table.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
                  )
                else
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
                    child: Column(children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        decoration: const BoxDecoration(color: Color(0xFFF8FAFC), borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
                        child: const Row(children: [
                          Expanded(flex: 3, child: Text('License Name', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('License Number', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Expiry Date', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          SizedBox(width: 130, child: Text('Status', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                        ]),
                      ),
                      for (final entry in selected.values)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Expanded(flex: 3, child: Padding(padding: const EdgeInsets.only(top: 14), child: Text(entry.name, style: const TextStyle(fontWeight: FontWeight.w800, color: _ink)))),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.number,
                                decoration: const InputDecoration(labelText: 'License Number'),
                                validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.expiry,
                                decoration: const InputDecoration(labelText: 'Expiry Date', hintText: 'YYYY-MM-DD'),
                                validator: (v) {
                                  if (v == null || v.trim().isEmpty) return 'Required';
                                  if (DateTime.tryParse(v.trim()) == null) return 'Use YYYY-MM-DD';
                                  return null;
                                },
                                onChanged: (v) => setDialogState(() => entry.status = licenseStatusFromExpiry(v)),
                              ),
                            ),
                            const SizedBox(width: 10),
                            SizedBox(width: 130, child: Padding(padding: const EdgeInsets.only(top: 10), child: StatusChip(entry.status.isEmpty ? '-' : entry.status))),
                          ]),
                        ),
                    ]),
                  ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one license.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {
                final status = licenseStatusFromExpiry(entry.expiry.text);
                return <String, dynamic>{
                  'employee_id': employeeId,
                  'license_name': entry.name,
                  'license_number': entry.number.text.trim(),
                  'expiry_date': entry.expiry.text.trim(),
                  'status': status.isEmpty ? null : status,
                  'updated_at': now,
                };
              }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final item in selected.values) {
    item.dispose();
  }
  return result;
}

'''
    s = s.replace('Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', custom_dialog + 'Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', 1)

p.write_text(s)
