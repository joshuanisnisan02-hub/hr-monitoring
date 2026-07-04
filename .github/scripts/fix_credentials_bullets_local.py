from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8')
original = text

# Remove mojibake bullets from existing source text.
text = text.replace('â€¢', '\\u2022')

# Add shared credential bullet helpers before loadLicensesGrouped.
helper_marker = 'Future<List<dynamic>> loadLicensesGrouped({int limit = 5000}) async {'
if 'String credentialListValue(' not in text:
    helper = r'''
String credentialListValue(Object? value) {
  final text = formatValue(value)
      .replaceAll('â€¢', '')
      .replaceAll('\u2022', '')
      .replaceAll('•', '')
      .trim();
  return text.isEmpty || text == '-' ? '-' : text;
}

String credentialBulletList(List<Map<String, dynamic>> rows, String key) =>
    rows.map((row) => '\u2022 ${credentialListValue(row[key])}').join('\n');

'''
    if helper_marker not in text:
        raise SystemExit('Could not find loadLicensesGrouped marker.')
    text = text.replace(helper_marker, helper + helper_marker, 1)

# Fix the Licenses grouped bullet generator.
old_license_bullets = """    String bullets(String key) =>
        list.map((r) => '\\u2022 ${formatValue(r[key])}').join('\\n');"""
new_license_bullets = """    String bullets(String key) => credentialBulletList(list, key);"""
text = text.replace(old_license_bullets, new_license_bullets)
old_license_bullets_mojibake = """    String bullets(String key) =>
        list.map((r) => 'â€¢ ${formatValue(r[key])}').join('\\n');"""
text = text.replace(old_license_bullets_mojibake, new_license_bullets)

# Add grouped National Certificate loader.
cert_loader_marker = """Future<List<dynamic>> loadEvaluations({int limit = 1500}) => db"""
if 'Future<List<dynamic>> loadCertificatesGrouped' not in text:
    cert_grouped = r'''
Future<List<dynamic>> loadCertificatesGrouped({int limit = 5000}) async {
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
'''
    if cert_loader_marker not in text:
        raise SystemExit('Could not find loadEvaluations marker.')
    text = text.replace(cert_loader_marker, cert_grouped + cert_loader_marker, 1)

# Use grouped certificates in the tab and add View support.
text = text.replace("load: () => activeOnlyRows(loadCertificates()),", "load: () => activeOnlyRows(loadCertificatesGrouped()),", 1)
text = text.replace("""        onAdd: (ctx, refresh) => editCertificate(ctx, null, refresh),
        onEdit: editCertificate,""", """        onAdd: (ctx, refresh) => editCertificate(ctx, null, refresh),
        onView: viewCertificateGroup,
        onEdit: editCertificate,""", 1)

# Delete all grouped certificate IDs when deleting a grouped certificate row.
text = text.replace("""        onDelete: (row) =>
            db.from('employee_certificates').delete().eq('id', row['id']),""", """        onDelete: (row) async {
          final ids = row['certificate_ids'];
          if (ids is List && ids.isNotEmpty) {
            for (final id in ids) {
              await db.from('employee_certificates').delete().eq('id', id);
            }
          } else {
            await db.from('employee_certificates').delete().eq('id', row['id']);
          }
        },""", 1)

# Insert certificate group view and record picker before editCertificate.
cert_edit_marker = 'Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row,'
if 'Future<void> viewCertificateGroup(' not in text:
    cert_helpers = r'''
Future<void> viewCertificateGroup(
    BuildContext context, Map<String, dynamic> row) async {
  final records = (row['certificate_records'] is List)
      ? List<Map<String, dynamic>>.from(row['certificate_records'] as List)
      : <Map<String, dynamic>>[row];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Certificate Details - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 920,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            for (final rec in records)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 10),
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: _line)),
                child: Wrap(spacing: 10, runSpacing: 10, children: [
                  DetailTile('Certificate Type', formatValue(rec['certificate_type'])),
                  DetailTile('Certificate Name', formatValue(rec['certificate_name'])),
                  DetailTile('Certificate Number', formatValue(rec['certificate_number'])),
                  DetailTile('Expiry Date', formatValue(rec['expiry_date'])),
                  DetailTile('Status', formatValue(rec['status'])),
                  DetailTile('Attachment PDF', formatValue(rec['attachment_url'])),
                ]),
              ),
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

Future<Map<String, dynamic>?> pickCertificateRecordToEdit(
    BuildContext context, Map<String, dynamic> row) async {
  final records = (row['certificate_records'] is List)
      ? List<Map<String, dynamic>>.from(row['certificate_records'] as List)
      : <Map<String, dynamic>>[row];
  if (records.isEmpty) return null;
  if (records.length == 1) return records.first;
  return showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Choose Certificate to Edit'),
      content: SizedBox(
        width: 520,
        child: ListView.separated(
          shrinkWrap: true,
          itemCount: records.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (_, i) => ListTile(
            title: Text(formatValue(records[i]['certificate_name'])),
            subtitle: Text(
                'Certificate No.: ${formatValue(records[i]['certificate_number'])} \u2022 Expiry: ${formatValue(records[i]['expiry_date'])}'),
            onTap: () => Navigator.pop(context, records[i]),
          ),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'))
      ],
    ),
  );
}

'''
    if cert_edit_marker not in text:
        raise SystemExit('Could not find editCertificate marker.')
    text = text.replace(cert_edit_marker, cert_helpers + cert_edit_marker, 1)

# Make editCertificate work with grouped rows by selecting the actual certificate record first.
old_edit_start = r'''  final data = await showRecordDialog(
    context,
    'Edit Certificate','''
new_edit_start = r'''  final editRow = await pickCertificateRecordToEdit(context, row);
  if (editRow == null) return;
  final employeeName =
      formatValue(row['employee_name'] ?? editRow['employee_name']);

  final data = await showRecordDialog(
    context,
    'Edit Certificate','''
text = text.replace(old_edit_start, new_edit_start, 1)
text = text.replace("""    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row['id'], data, refresh);""", """    editRow,
    readOnlyEmployeeName:
        employeeName == '-' ? linkedEmployeeName(editRow) : employeeName,
  );
  if (data == null) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', editRow['id'], data, refresh);""", 1)

if text == original:
    print('No changes applied. Credentials bullets may already be fixed.')
else:
    path.write_text(text, encoding='utf-8')
    print('Fixed credential bullet formatting and applied grouped bullets to National Certificates.')
