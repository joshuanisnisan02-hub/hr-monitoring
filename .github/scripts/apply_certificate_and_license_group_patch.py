from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Add grouped license loader and certificate option loader after loadLicenses/loadCertificates.
old_loads = """Future<List<dynamic>> loadLicenses({int limit = 1500}) => db.from('employee_licenses').select('id, employee_id, license_name, license_number, issued_date, expiry_date, status, attachment_url, employees(full_name)').order('expiry_date').limit(limit);
Future<List<dynamic>> loadCertificates({int limit = 1500}) => db.from('employee_certificates').select('id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, attachment_url, employees(full_name)').order('expiry_date').limit(limit);"""
new_loads = """Future<List<dynamic>> loadLicenses({int limit = 1500}) => db.from('employee_licenses').select('id, employee_id, license_name, license_number, issued_date, expiry_date, status, attachment_url, employees(full_name)').order('expiry_date').limit(limit);

Future<List<dynamic>> loadLicensesGrouped({int limit = 5000}) async {
  final rows = await loadLicenses(limit: limit);
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
    String bullets(String key) => list.map((r) => '• ${formatValue(r[key])}').join('\\n');
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'license_ids': list.map((r) => r['id']).toList(),
      'license_records': list,
      'license_name': bullets('license_name'),
      'license_number': bullets('license_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name']).compareTo(formatValue(b['employee_name'])));
  return out;
}

Future<List<dynamic>> loadCertificates({int limit = 1500}) => db.from('employee_certificates').select('id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, attachment_url, employees(full_name)').order('expiry_date').limit(limit);"""
if old_loads not in s:
    raise SystemExit('loadLicenses/loadCertificates block not found')
s = s.replace(old_loads, new_loads, 1)

# Use grouped license loader and add view button.
s = s.replace("""        load: () => loadLicenses(),""", """        load: () => loadLicensesGrouped(),""", 1)
s = s.replace("""        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onEdit: editLicense,
        onDelete: (row) => db.from('employee_licenses').delete().eq('id', row['id']),""", """        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onView: viewLicenseGroup,
        onEdit: editLicense,
        onDelete: (row) => db.from('employee_licenses').delete().eq('id', row['id']),""", 1)

# Add view dialog for grouped license rows before editLicense.
if 'Future<void> viewLicenseGroup(BuildContext context, Map<String, dynamic> row)' not in s:
    view_fn = r'''
Future<void> viewLicenseGroup(BuildContext context, Map<String, dynamic> row) async {
  final records = (row['license_records'] is List) ? List<Map<String, dynamic>>.from(row['license_records'] as List) : <Map<String, dynamic>>[row];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('License Details - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 920,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            for (final rec in records)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                child: Wrap(spacing: 10, runSpacing: 10, children: [
                  DetailTile('License Name', formatValue(rec['license_name'])),
                  DetailTile('License Number', formatValue(rec['license_number'])),
                  DetailTile('Expiry Date', formatValue(rec['expiry_date'])),
                  DetailTile('Status', formatValue(rec['status'])),
                  DetailTile('Attachment PDF', formatValue(rec['attachment_url'])),
                ]),
              ),
          ]),
        ),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    ),
  );
}

'''
    s = s.replace('Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', view_fn + 'Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', 1)

# Add certificate options helper after licenseNameOptions.
if 'Future<List<String>> certificateNameOptions() async' not in s:
    s = s.replace(
        """Future<Map<String, String>> rankingAppointmentByEmployee() async {""",
        """Future<List<String>> certificateNameOptions() async {
  const defaults = <String>[
    'National Certificate I (NC I)',
    'National Certificate II (NC II)',
    'National Certificate III (NC III)',
    'National Certificate IV (NC IV)',
    'Trainer Methodology Certificate I (TM I)',
    'Trainer Methodology Certificate II (TM II)',
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
    final rows = await db.from('employee_certificates').select('certificate_name').order('certificate_name').limit(3000);
    for (final r in rows) {
      addName('${r['certificate_name'] ?? ''}');
    }
  } catch (_) {}
  return out;
}

Future<Map<String, String>> rankingAppointmentByEmployee() async {""",
        1,
    )

# Add shared selected certificate model and dialog before editCertificate.
if 'class SelectedCertificateInput' not in s:
    cert_dialog = r'''
class SelectedCertificateInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;
  String status = '';

  SelectedCertificateInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
  }
}

String certificateStatusFromExpiry(String text) => licenseStatusFromExpiry(text);

Future<void> pickAndUploadCertificatePdf(BuildContext context, SelectedCertificateInput entry, StateSetter setDialogState) async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return;
  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return;
  }
  setDialogState(() => entry.uploadingAttachment = true);
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path = 'certificates/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes, fileOptions: const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      entry.attachmentUrl = url;
      entry.attachmentFileName = file.name;
      entry.uploadingAttachment = false;
    });
  } catch (e) {
    setDialogState(() => entry.uploadingAttachment = false);
    showSnack(context, 'PDF upload failed: $e');
  }
}

Future<List<Map<String, dynamic>>?> showAddCertificateDialog(BuildContext context, List<EditOption> employees, List<String> certificates) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  final selected = <String, SelectedCertificateInput>{};

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add Certificate'),
        content: SizedBox(
          width: 1040,
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
                const DialogSectionTitle('Certificate Checklist'),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    for (final cert in certificates)
                      SizedBox(
                        width: 278,
                        child: CheckboxListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          controlAffinity: ListTileControlAffinity.leading,
                          title: Text(cert, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
                          value: selected.containsKey(cert),
                          onChanged: (checked) => setDialogState(() {
                            if (checked == true) {
                              selected.putIfAbsent(cert, () => SelectedCertificateInput(cert));
                            } else {
                              selected.remove(cert)?.dispose();
                            }
                          }),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('Selected Certificates'),
                if (selected.isEmpty)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                    child: const Text('Select one or more certificates above. The selected certificates will appear here as a table.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
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
                          Expanded(flex: 3, child: Text('Certificate Name', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Certificate Number', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Expiry Date', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Attachment (PDF)', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
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
                                decoration: const InputDecoration(labelText: 'Certificate Number'),
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
                                onChanged: (v) => setDialogState(() => entry.status = certificateStatusFromExpiry(v)),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                OutlinedButton.icon(
                                  onPressed: entry.uploadingAttachment ? null : () => pickAndUploadCertificatePdf(context, entry, setDialogState),
                                  icon: entry.uploadingAttachment
                                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                      : const Icon(Icons.picture_as_pdf_rounded),
                                  label: Text(entry.uploadingAttachment ? 'Uploading...' : (entry.attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF')),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  entry.attachmentFileName.isEmpty ? 'No PDF attached' : entry.attachmentFileName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontSize: 12, color: entry.attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700),
                                ),
                              ]),
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
                showSnack(context, 'Please select at least one certificate.');
                return;
              }
              final missingPdf = selected.values.where((entry) => entry.attachmentUrl.trim().isEmpty).toList();
              if (missingPdf.isNotEmpty) {
                showSnack(context, 'Please attach a PDF file for every selected certificate.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {
                final status = certificateStatusFromExpiry(entry.expiry.text);
                return <String, dynamic>{
                  'employee_id': employeeId,
                  'certificate_type': 'National Certificate',
                  'certificate_name': entry.name,
                  'certificate_number': entry.number.text.trim(),
                  'expiry_date': entry.expiry.text.trim(),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),
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
    s = s.replace('Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', cert_dialog + 'Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {', 1)

# Replace editCertificate add branch with multi-certificate dialog.
old_edit_cert = """Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Certificate' : 'Edit Certificate',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('certificate_type', 'Certificate Type'),
      const EditField('certificate_name', 'Certificate Name', required: true),
      const EditField('certificate_number', 'Certificate Number'),
      const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      const EditField('attachment_url', 'Attachment URL'),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_certificates', data['employee_id'], 'certificate')) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row?['id'], data, refresh);
}"""
new_edit_cert = """Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddCertificateDialog(context, await employeeOptions(), await certificateNameOptions());
    if (records == null || records.isEmpty) return;
    try {
      await db.from('employee_certificates').insert(records);
      showSnack(context, records.length == 1 ? 'Certificate record added.' : '${records.length} certificate records added.');
      refresh();
    } catch (e) {
      showSnack(context, 'Add Certificate Failed: $e');
    }
    return;
  }

  final data = await showRecordDialog(
    context,
    'Edit Certificate',
    const [
      EditField('certificate_type', 'Certificate Type'),
      EditField('certificate_name', 'Certificate Name', required: true),
      EditField('certificate_number', 'Certificate Number'),
      EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      EditField('attachment_url', 'Attachment URL'),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row['id'], data, refresh);
}"""
if old_edit_cert not in s:
    raise SystemExit('old editCertificate block not found')
s = s.replace(old_edit_cert, new_edit_cert, 1)

p.write_text(s)
