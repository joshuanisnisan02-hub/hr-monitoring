from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text
has_archive_props = 'final String? archiveTableName;' in text

# Add Safety Officer loader/grouping beside license/certificate loaders.
if 'Future<List<dynamic>> loadSafetyOfficers' not in text:
    insert_after = """Future<List<dynamic>> loadCertificatesGrouped({int limit = 5000}) async {
  final rows = await loadCertificates(limit: limit);
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}';
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }
  final out = <Map<String, dynamic>>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.isEmpty) continue;
    final first = list.first;
    String bullets(String key) => credentialBulletList(list, key);
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'certificate_ids': list.map((r) => r['id']).toList(),
      'certificate_records': list,
      'certificate_name': bullets('certificate_name'),
      'certificate_type': bullets('certificate_type'),
      'certificate_number': bullets('certificate_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name'])
      .compareTo(formatValue(b['employee_name'])));
  return out;
}
"""
    new_loader = insert_after + """
Future<List<dynamic>> loadSafetyOfficers({int limit = 1500}) => db
    .from('employee_safety_officers')
    .select(
        'id, employee_id, safety_officer_name, certificate_number, issued_date, expiry_date, status, attachment_url, employees(full_name)')
    .order('expiry_date')
    .limit(limit);

Future<List<dynamic>> loadSafetyOfficersGrouped({int limit = 5000}) async {
  final rows = await loadSafetyOfficers(limit: limit);
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}';
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }
  final out = <Map<String, dynamic>>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.isEmpty) continue;
    final first = list.first;
    String bullets(String key) => credentialBulletList(list, key);
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'safety_officer_ids': list.map((r) => r['id']).toList(),
      'safety_officer_records': list,
      'safety_officer_name': bullets('safety_officer_name'),
      'certificate_number': bullets('certificate_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name'])
      .compareTo(formatValue(b['employee_name'])));
  return out;
}
"""
    if insert_after not in text:
        raise SystemExit('Could not find certificate grouped loader block.')
    text = text.replace(insert_after, new_loader, 1)

# Update Credentials page tabs.
text = text.replace(
    "subtitle:\n            'Manage licenses and national certificates linked to employees.',",
    "subtitle:\n            'Manage licenses, national certificates, and safety officer credentials linked to employees.',",
    1,
)
text = text.replace('length: 2,', 'length: 3,', 1)
text = text.replace('width: 430,', 'width: 680,', 1)
text = text.replace(
    """                      Tab(text: 'Licenses'),
                      Tab(text: 'National Certificates')""",
    """                      Tab(text: 'Licenses'),
                      Tab(text: 'National Certificates'),
                      Tab(text: 'Safety Officer')""",
    1,
)
text = text.replace(
    "TabBarView(children: [LicensesTab(), CertificatesTab()])",
    "TabBarView(children: [LicensesTab(), CertificatesTab(), SafetyOfficersTab()])",
    1,
)

# Add Safety Officer tab widget after CertificatesTab.
if 'class SafetyOfficersTab extends StatelessWidget' not in text:
    marker = 'class EvaluationsPage extends StatefulWidget {'
    archive_lines = ""
    if has_archive_props:
        archive_lines = """        archiveTableName: 'employee_safety_officers',
        archiveModuleName: 'Credentials - Safety Officer',
"""
    safety_tab = f'''class SafetyOfficersTab extends StatelessWidget {{
  const SafetyOfficersTab({{super.key}});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => activeOnlyRows(loadSafetyOfficersGrouped()),
        searchHint: 'Search employee, safety officer, certificate number, or status',
        addLabel: 'Add Safety Officer',
{archive_lines}        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('safety_officer_name', 'Safety Officer', flex: 3),
          GridCol('certificate_number', 'Certificate No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editSafetyOfficer(ctx, null, refresh),
        onView: viewSafetyOfficerGroup,
        onEdit: editSafetyOfficer,
        onDelete: (row) async {{
          final ids = row['safety_officer_ids'];
          if (ids is List && ids.isNotEmpty) {{
            for (final id in ids) {{
              await db.from('employee_safety_officers').delete().eq('id', id);
            }}
          }} else {{
            await db.from('employee_safety_officers').delete().eq('id', row['id']);
          }}
        }},
      );
}}

'''
    if marker not in text:
        raise SystemExit('Could not find insertion point for SafetyOfficersTab.')
    text = text.replace(marker, safety_tab + marker, 1)

# Add edit/view functions before Appointment section if missing.
if 'Future<void> viewSafetyOfficerGroup' not in text:
    marker = 'class AppointmentPage extends StatelessWidget {'
    safety_functions = r'''Future<void> viewSafetyOfficerGroup(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final records = normalized['safety_officer_records'] is List
      ? normalized['safety_officer_records'] as List<dynamic>
      : <dynamic>[normalized];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Safety Officer - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            relatedSection('Safety Officer Records', records, const [
              'safety_officer_name',
              'certificate_number',
              'issued_date',
              'expiry_date',
              'status',
              'attachment_url'
            ]),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

Map<String, dynamic> firstSafetyOfficerRecord(Map<String, dynamic>? row) {
  final normalized = normalizeRow(row ?? {});
  final records = normalized['safety_officer_records'];
  if (records is List && records.isNotEmpty && records.first is Map) {
    return normalizeRow(Map<String, dynamic>.from(records.first as Map));
  }
  return normalized;
}

Future<void> editSafetyOfficer(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final source = firstSafetyOfficerRecord(row);
  final fields = <EditField>[
    if (isAdd)
      EditField('employee_id', 'Employee Name',
          kind: FieldKind.dropdown,
          required: true,
          options: await employeeOptions()),
    const EditField('safety_officer_name', 'Safety Officer',
        kind: FieldKind.dropdown,
        required: true,
        options: [
          EditOption('Safety Officer 1', 'Safety Officer 1'),
          EditOption('Safety Officer 2', 'Safety Officer 2'),
          EditOption('Safety Officer 3', 'Safety Officer 3'),
          EditOption('Safety Officer 4', 'Safety Officer 4'),
        ]),
    const EditField('certificate_number', 'Certificate Number', required: true),
    const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
    const EditField('expiry_date', 'Expiry Date',
        kind: FieldKind.date, required: true),
    const EditField('attachment_url', 'Attachment URL'),
    const EditField('status', 'Status',
        kind: FieldKind.dropdown,
        options: [
          EditOption('Active', 'Active'),
          EditOption('For Renewal', 'For Renewal'),
          EditOption('Expired', 'Expired'),
        ]),
  ];

  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Safety Officer' : 'Edit Safety Officer',
    fields,
    source,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(source),
  );
  if (data == null) return;
  final computedStatus = certificateStatusFromExpiry(data['expiry_date'] ?? '');
  if ((data['status'] == null || '${data['status']}'.trim().isEmpty) &&
      computedStatus.isNotEmpty) {
    data['status'] = computedStatus;
  }
  await saveRow(
      context, 'employee_safety_officers', isAdd ? null : source['id'], data, refresh);
}

'''
    if marker not in text:
        raise SystemExit('Could not find insertion point for Safety Officer functions.')
    text = text.replace(marker, safety_functions + marker, 1)

# Include safety officer records in archive restore cleanup if archive helper exists.
if "out.remove('safety_officer_ids');" not in text and "archiveRestoreData" in text:
    text = text.replace(
        "  out.remove('certificate_records');",
        "  out.remove('certificate_records');\n  out.remove('safety_officer_ids');\n  out.remove('safety_officer_records');",
        1,
    )

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Safety Officer tab may already be present.')
else:
    print('Added Safety Officer tab inside Credentials module with add/view/edit/delete behavior.')
