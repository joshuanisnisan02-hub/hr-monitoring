from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

if 'Future<Map<String, dynamic>?> pickLicenseRecordToEdit(' not in s:
    helper = r'''
Future<Map<String, dynamic>?> pickLicenseRecordToEdit(BuildContext context, Map<String, dynamic> row) async {
  final records = (row['license_records'] is List) ? List<Map<String, dynamic>>.from(row['license_records'] as List) : <Map<String, dynamic>>[row];
  if (records.isEmpty) return null;
  if (records.length == 1) return records.first;
  return showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Choose License to Edit'),
      content: SizedBox(
        width: 520,
        child: ListView.separated(
          shrinkWrap: true,
          itemCount: records.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (_, i) => ListTile(
            title: Text(formatValue(records[i]['license_name'])),
            subtitle: Text('License No.: ${formatValue(records[i]['license_number'])} • Expiry: ${formatValue(records[i]['expiry_date'])}'),
            onTap: () => Navigator.pop(context, records[i]),
          ),
        ),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel'))],
    ),
  );
}

'''
    s = s.replace('Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', helper + 'Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', 1)

old = r'''  final data = await showRecordDialog(
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
  await saveRow(context, 'employee_licenses', row['id'], data, refresh);'''
new = r'''  final editRow = await pickLicenseRecordToEdit(context, row);
  if (editRow == null) return;
  final employeeName = formatValue(row['employee_name'] ?? editRow['employee_name']);
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
    editRow,
    readOnlyEmployeeName: employeeName == '-' ? linkedEmployeeName(editRow) : employeeName,
  );
  if (data == null) return;
  await saveRow(context, 'employee_licenses', editRow['id'], data, refresh);'''

if old not in s:
    raise SystemExit('Edit license dialog block not found')
s = s.replace(old, new, 1)

p.write_text(s)
