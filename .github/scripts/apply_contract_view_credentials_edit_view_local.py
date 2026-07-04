from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

def insert_before(marker: str, value: str):
    global text
    if value.strip().split('\n')[0] in text:
        return
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f'Missing marker: {marker}')
    text = text[:idx] + value + text[idx:]

def replace_between(start: str, end: str, replacement: str):
    global text
    a = text.find(start)
    if a < 0:
        raise SystemExit(f'Missing start marker: {start}')
    b = text.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f'Missing end marker: {end}')
    text = text[:a] + replacement + text[b:]

# -----------------------------------------------------------------------------
# Shared PDF display/open helper for view modals.
# -----------------------------------------------------------------------------
if 'class AttachmentPdfTile extends StatelessWidget' not in text:
    pdf_helper = r'''
class AttachmentPdfTile extends StatelessWidget {
  final String label;
  final Object? url;
  const AttachmentPdfTile(this.label, this.url, {super.key});

  @override
  Widget build(BuildContext context) {
    final link = formatValue(url).trim();
    final hasPdf = link.isNotEmpty && link != '-';
    return SizedBox(
      width: 245,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _line)),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label,
              style: const TextStyle(
                  fontSize: 11, color: _muted, fontWeight: FontWeight.w800)),
          const SizedBox(height: 6),
          if (!hasPdf)
            const Text('No PDF attached',
                style: TextStyle(
                    fontSize: 13, color: _muted, fontWeight: FontWeight.w700))
          else ...[
            Text(link,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                    fontSize: 12, color: _ink, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () => html.window.open(link, '_blank'),
              icon: const Icon(Icons.picture_as_pdf_rounded, size: 16),
              label: const Text('Open PDF'),
            ),
          ],
        ]),
      ),
    );
  }
}

'''
    insert_before('class DetailTile extends StatelessWidget', pdf_helper)

# -----------------------------------------------------------------------------
# Contracts: add View button and detail dialog with open PDF action.
# -----------------------------------------------------------------------------
if 'Future<void> viewContract(' not in text:
    contract_view = r'''
Future<void> viewContract(BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Contract Details - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child: Wrap(spacing: 10, runSpacing: 10, children: [
            DetailTile('Employee Name', formatValue(normalized['employee_name'])),
            DetailTile('Contract Type', formatValue(normalized['contract_type'])),
            DetailTile('Status', formatValue(normalized['status'])),
            DetailTile('Start Date', formatValue(normalized['contract_start_date'])),
            DetailTile('Duration Months', formatValue(normalized['duration_months'])),
            DetailTile('End Date', formatValue(normalized['contract_end_date'])),
            DetailTile('Days Left', formatValue(normalized['days_left'])),
            AttachmentPdfTile('Contract PDF', normalized['attachment_url']),
          ]),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
      ],
    ),
  );
}

'''
    insert_before('Future<void> editContract(', contract_view)

if 'onView: viewContract,' not in text:
    text = text.replace('              onAdd: (ctx, refresh) => editContract(ctx, null, refresh),\n              onEdit: editContract,',
                        '              onAdd: (ctx, refresh) => editContract(ctx, null, refresh),\n              onView: viewContract,\n              onEdit: editContract,', 1)

# -----------------------------------------------------------------------------
# License / Certificate view: replace URL-only tile with Open PDF tile.
# -----------------------------------------------------------------------------
text = text.replace("""                  DetailTile(
                      'Attachment PDF', formatValue(rec['attachment_url'])),""",
                    """                  AttachmentPdfTile('Attachment PDF', rec['attachment_url']),""")

# -----------------------------------------------------------------------------
# Edit License/Certificate group dialogs: same behavior as Add modal plus checklist
# to add another license/certificate under the same employee.
# -----------------------------------------------------------------------------
if 'Future<List<Map<String, dynamic>>?> showEditLicenseGroupDialog' not in text:
    edit_group_helpers = r'''
Future<List<Map<String, dynamic>>?> showEditLicenseGroupDialog(
    BuildContext context, Map<String, dynamic> row, List<String> licenseNames) async {
  final records = (row['license_records'] is List)
      ? List<Map<String, dynamic>>.from(row['license_records'] as List)
      : <Map<String, dynamic>>[row];
  final employeeId = '${row['employee_id'] ?? (records.isNotEmpty ? records.first['employee_id'] : '')}';
  final employeeName = formatValue(row['employee_name']);
  final formKey = GlobalKey<FormState>();
  final selected = <String, SelectedLicenseInput>{};
  for (final rec in records) {
    final name = formatValue(rec['license_name']);
    if (name == '-' || name.trim().isEmpty) continue;
    final entry = SelectedLicenseInput(name);
    entry.number.text = formatEditValue(rec['license_number']);
    entry.expiry.text = formatEditValue(rec['expiry_date']);
    entry.attachmentUrl = formatEditValue(rec['attachment_url']);
    entry.attachmentFileName = entry.attachmentUrl.isEmpty ? '' : entry.attachmentUrl.split('/').last;
    entry.status = formatEditValue(rec['status']).isEmpty
        ? licenseStatusFromExpiry(entry.expiry.text)
        : formatEditValue(rec['status']);
    entry.attachment.text = entry.attachmentUrl;
    selected[name] = entry;
  }
  final allNames = <String>{...licenseNames, ...selected.keys}.toList()
    ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Edit License'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                ReadOnlyEmployeeBox(employeeName == '-' ? linkedEmployeeName(row) : employeeName),
                const SizedBox(height: 16),
                const DialogSectionTitle('License Information'),
                Wrap(spacing: 10, runSpacing: 8, children: [
                  for (final license in allNames)
                    SizedBox(
                      width: 228,
                      child: CheckboxListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                        title: Text(license,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                                fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
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
                ]),
                const SizedBox(height: 12),
                if (selected.isEmpty)
                  Container(
                    width: 728,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: _line)),
                    child: const Text('Select one or more licenses above.',
                        style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
                  )
                else
                  for (final entry in selected.values)
                    addEmployeeSelectedLicenseCard(context, entry, setDialogState),
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
                final existing = records.cast<Map<String, dynamic>?>().firstWhere(
                    (rec) => formatValue(rec?['license_name']) == entry.name,
                    orElse: () => null);
                final status = licenseStatusFromExpiry(entry.expiry.text);
                return <String, dynamic>{
                  if (existing?['id'] != null) 'id': existing!['id'],
                  'employee_id': employeeId,
                  'license_name': entry.name,
                  'license_number': entry.number.text.trim(),
                  'expiry_date': toIsoDateInput(entry.expiry.text),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),
                  'status': entry.status.isEmpty ? (status.isEmpty ? null : status) : entry.status,
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
  for (final entry in selected.values) {
    entry.dispose();
  }
  return result;
}

Future<List<Map<String, dynamic>>?> showEditCertificateGroupDialog(
    BuildContext context, Map<String, dynamic> row, List<String> certificateNames) async {
  final records = (row['certificate_records'] is List)
      ? List<Map<String, dynamic>>.from(row['certificate_records'] as List)
      : <Map<String, dynamic>>[row];
  final employeeId = '${row['employee_id'] ?? (records.isNotEmpty ? records.first['employee_id'] : '')}';
  final employeeName = formatValue(row['employee_name']);
  final formKey = GlobalKey<FormState>();
  final selected = <String, SelectedCertificateInput>{};
  for (final rec in records) {
    final name = formatValue(rec['certificate_name']);
    if (name == '-' || name.trim().isEmpty) continue;
    final entry = SelectedCertificateInput(name);
    entry.number.text = formatEditValue(rec['certificate_number']);
    entry.expiry.text = formatEditValue(rec['expiry_date']);
    entry.attachmentUrl = formatEditValue(rec['attachment_url']);
    entry.attachmentFileName = entry.attachmentUrl.isEmpty ? '' : entry.attachmentUrl.split('/').last;
    entry.status = formatEditValue(rec['status']).isEmpty
        ? certificateStatusFromExpiry(entry.expiry.text)
        : formatEditValue(rec['status']);
    entry.attachment.text = entry.attachmentUrl;
    selected[name] = entry;
  }
  final allNames = <String>{...certificateNames, ...selected.keys}.toList()
    ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Edit Certificate'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                ReadOnlyEmployeeBox(employeeName == '-' ? linkedEmployeeName(row) : employeeName),
                const SizedBox(height: 16),
                const DialogSectionTitle('Certificate Information'),
                Wrap(spacing: 10, runSpacing: 8, children: [
                  for (final cert in allNames)
                    SizedBox(
                      width: 228,
                      child: CheckboxListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                        title: Text(cert,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                                fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
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
                ]),
                const SizedBox(height: 12),
                if (selected.isEmpty)
                  Container(
                    width: 728,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: _line)),
                    child: const Text('Select one or more certificates above.',
                        style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
                  )
                else
                  for (final entry in selected.values)
                    addEmployeeSelectedCertificateCard(context, entry, setDialogState),
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
              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {
                final existing = records.cast<Map<String, dynamic>?>().firstWhere(
                    (rec) => formatValue(rec?['certificate_name']) == entry.name,
                    orElse: () => null);
                final status = certificateStatusFromExpiry(entry.expiry.text);
                return <String, dynamic>{
                  if (existing?['id'] != null) 'id': existing!['id'],
                  'employee_id': employeeId,
                  'certificate_type': 'National Certificate',
                  'certificate_name': entry.name,
                  'certificate_number': entry.number.text.trim(),
                  'expiry_date': toIsoDateInput(entry.expiry.text),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),
                  'status': entry.status.isEmpty ? (status.isEmpty ? null : status) : entry.status,
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
  for (final entry in selected.values) {
    entry.dispose();
  }
  return result;
}

Future<void> saveCredentialRecords(BuildContext context, String tableName,
    List<Map<String, dynamic>> records, VoidCallback refresh, String label) async {
  try {
    for (final record in records) {
      final data = Map<String, dynamic>.from(record);
      final id = data.remove('id');
      if (id == null) {
        await db.from(tableName).insert(data);
      } else {
        await db.from(tableName).update(data).eq('id', id);
      }
    }
    refresh();
    showSnack(context, '$label information saved.');
  } catch (e) {
    showSnack(context, 'Save $label Failed: $e');
  }
}

'''
    insert_before('Future<void> viewLicenseGroup(', edit_group_helpers)

# Replace editLicense body with grouped checklist edit dialog.
replace_between('Future<void> editLicense(BuildContext context, Map<String, dynamic>? row,',
                'class SelectedCertificateInput {',
                r'''Future<void> editLicense(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddLicenseDialog(
        context, await employeeOptions(), await licenseNameOptions());
    if (records == null || records.isEmpty) return;
    await saveCredentialRecords(
        context, 'employee_licenses', records, refresh, 'License');
    return;
  }

  final records = await showEditLicenseGroupDialog(
      context, row, await licenseNameOptions());
  if (records == null || records.isEmpty) return;
  await saveCredentialRecords(
      context, 'employee_licenses', records, refresh, 'License');
}

''')

# Replace editCertificate body with grouped checklist edit dialog.
replace_between('Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row,',
                'Future<void> editEvaluation(',
                r'''Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddCertificateDialog(
        context, await employeeOptions(), await certificateNameOptions());
    if (records == null || records.isEmpty) return;
    await saveCredentialRecords(
        context, 'employee_certificates', records, refresh, 'Certificate');
    return;
  }

  final records = await showEditCertificateGroupDialog(
      context, row, await certificateNameOptions());
  if (records == null || records.isEmpty) return;
  await saveCredentialRecords(
      context, 'employee_certificates', records, refresh, 'Certificate');
}

''')

# License group delete should remove all grouped license IDs, not only first row.
text = text.replace("""        onDelete: (row) =>
            db.from('employee_licenses').delete().eq('id', row['id']),""",
                    """        onDelete: (row) async {
          final ids = row['license_ids'];
          if (ids is List && ids.isNotEmpty) {
            for (final id in ids) {
              await db.from('employee_licenses').delete().eq('id', id);
            }
          } else {
            await db.from('employee_licenses').delete().eq('id', row['id']);
          }
        },""")

if text == original:
    print('No changes applied. Contract view and credential edit/view patch may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Applied contract View button, credential grouped edit checklist, and open PDF view buttons.')
