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
        return False
    b = text.find(end, a + len(start))
    if b < 0:
        return False
    text = text[:a] + replacement + text[b:]
    return True

# -----------------------------------------------------------------------------
# Alert modal used for save/resigned results.
# -----------------------------------------------------------------------------
if 'Future<void> showActionAlert(' not in text:
    alert_helper = r'''
Future<void> showActionAlert(
    BuildContext context, String title, String message,
    {IconData icon = Icons.check_circle_rounded,
    Color iconColor = const Color(0xFF16A34A)}) async {
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Row(children: [
        Icon(icon, color: iconColor),
        const SizedBox(width: 10),
        Expanded(child: Text(title)),
      ]),
      content: Text(message),
      actions: [
        FilledButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('OK'),
        ),
      ],
    ),
  );
}

'''
    insert_before('Future<void> main() async {', alert_helper)

# -----------------------------------------------------------------------------
# PDF picker should complete when user cancels the picker.
# -----------------------------------------------------------------------------
if 'Future<html.File?> pickPdfFileOrNull' not in text:
    picker_helper = r'''
Future<html.File?> pickPdfFileOrNull() async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await Future.any<dynamic>([
    input.onChange.first,
    input.on['cancel'].first,
    Future.delayed(const Duration(seconds: 30), () => html.Event('timeout')),
  ]);
  return input.files?.isNotEmpty == true ? input.files!.first : null;
}

'''
    insert_before('Future<UploadedAttachment?> pickAndUploadContractPdf(', picker_helper)

old_file_picker = """  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
"""
text = text.replace(old_file_picker, """  final file = await pickPdfFileOrNull();
""")

# -----------------------------------------------------------------------------
# Better UI cards for selected License and Certificate rows in Add Employee.
# -----------------------------------------------------------------------------
if 'Widget addEmployeeSelectedLicenseCard(' not in text:
    credential_card_helpers = r'''
Widget addEmployeeSelectedLicenseCard(BuildContext context,
        SelectedLicenseInput entry, StateSetter setDialogState) =>
    SizedBox(
      width: 728,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: _line),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
              child: Text(entry.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontWeight: FontWeight.w900, color: _ink)),
            ),
            StatusChip(entry.status.isEmpty ? 'Select Expiry' : entry.status),
          ]),
          const SizedBox(height: 12),
          Wrap(spacing: 12, runSpacing: 12, crossAxisAlignment: WrapCrossAlignment.center, children: [
            SizedBox(
              width: 220,
              child: TextFormField(
                controller: entry.number,
                decoration: const InputDecoration(labelText: 'License Number'),
                validator: (value) => value == null || value.trim().isEmpty
                    ? 'Required'
                    : null,
              ),
            ),
            SizedBox(
              width: 220,
              child: TextFormField(
                controller: entry.expiry,
                readOnly: true,
                onTap: () => pickDateIntoController(context, entry.expiry,
                    afterPick: () => setDialogState(() => entry.status =
                        licenseStatusFromExpiry(entry.expiry.text))),
                decoration: InputDecoration(
                  labelText: 'Expiry Date',
                  suffixIcon: IconButton(
                    tooltip: 'Pick expiry date',
                    icon: const Icon(Icons.calendar_month_rounded),
                    onPressed: () => pickDateIntoController(context, entry.expiry,
                        afterPick: () => setDialogState(() => entry.status =
                            licenseStatusFromExpiry(entry.expiry.text))),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) return 'Required';
                  return parseFlexibleDate(value.trim()) == null
                      ? 'Select a valid date'
                      : null;
                },
              ),
            ),
            OutlinedButton.icon(
              onPressed: entry.uploadingAttachment
                  ? null
                  : () => pickAndUploadLicensePdf(context, entry, setDialogState),
              icon: entry.uploadingAttachment
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.picture_as_pdf_rounded),
              label: Text(entry.uploadingAttachment
                  ? 'Uploading...'
                  : (entry.attachmentFileName.isEmpty
                      ? 'Attach PDF'
                      : 'Change PDF')),
            ),
            SizedBox(
              width: 220,
              child: Text(
                entry.attachmentFileName.isEmpty
                    ? 'No PDF attached'
                    : entry.attachmentFileName,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                    color: entry.attachmentFileName.isEmpty ? _muted : _ink,
                    fontWeight: FontWeight.w700,
                    fontSize: 12),
              ),
            ),
          ]),
        ]),
      ),
    );

Widget addEmployeeSelectedCertificateCard(BuildContext context,
        SelectedCertificateInput entry, StateSetter setDialogState) =>
    SizedBox(
      width: 728,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: _line),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
              child: Text(entry.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontWeight: FontWeight.w900, color: _ink)),
            ),
            StatusChip(entry.status.isEmpty ? 'Select Expiry' : entry.status),
          ]),
          const SizedBox(height: 12),
          Wrap(spacing: 12, runSpacing: 12, crossAxisAlignment: WrapCrossAlignment.center, children: [
            SizedBox(
              width: 220,
              child: TextFormField(
                controller: entry.number,
                decoration:
                    const InputDecoration(labelText: 'Certificate Number'),
                validator: (value) => value == null || value.trim().isEmpty
                    ? 'Required'
                    : null,
              ),
            ),
            SizedBox(
              width: 220,
              child: TextFormField(
                controller: entry.expiry,
                readOnly: true,
                onTap: () => pickDateIntoController(context, entry.expiry,
                    afterPick: () => setDialogState(() => entry.status =
                        certificateStatusFromExpiry(entry.expiry.text))),
                decoration: InputDecoration(
                  labelText: 'Expiry Date',
                  suffixIcon: IconButton(
                    tooltip: 'Pick expiry date',
                    icon: const Icon(Icons.calendar_month_rounded),
                    onPressed: () => pickDateIntoController(context, entry.expiry,
                        afterPick: () => setDialogState(() => entry.status =
                            certificateStatusFromExpiry(entry.expiry.text))),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) return 'Required';
                  return parseFlexibleDate(value.trim()) == null
                      ? 'Select a valid date'
                      : null;
                },
              ),
            ),
            OutlinedButton.icon(
              onPressed: entry.uploadingAttachment
                  ? null
                  : () => pickAndUploadCertificatePdf(
                      context, entry, setDialogState),
              icon: entry.uploadingAttachment
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.picture_as_pdf_rounded),
              label: Text(entry.uploadingAttachment
                  ? 'Uploading...'
                  : (entry.attachmentFileName.isEmpty
                      ? 'Attach PDF'
                      : 'Change PDF')),
            ),
            SizedBox(
              width: 220,
              child: Text(
                entry.attachmentFileName.isEmpty
                    ? 'No PDF attached'
                    : entry.attachmentFileName,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                    color: entry.attachmentFileName.isEmpty ? _muted : _ink,
                    fontWeight: FontWeight.w700,
                    fontSize: 12),
              ),
            ),
          ]),
        ]),
      ),
    );

'''
    insert_before('class DialogSectionTitle extends StatelessWidget {', credential_card_helpers)

# Replace selected license detailed rows inside Add Employee only.
license_start = 'for (final entry in selectedLicenses.values)'
license_end = "\n                ],\n                const SizedBox(height: 16),\n                const DialogSectionTitle('Certificate Information (Optional)'),"
if license_start in text and license_end in text:
    a = text.find(license_start)
    b = text.find(license_end, a)
    if a >= 0 and b >= 0:
        text = text[:a] + "for (final entry in selectedLicenses.values)\n                    addEmployeeSelectedLicenseCard(context, entry, setDialogState)," + text[b:]

cert_start = 'for (final entry in selectedCertificates.values)'
cert_end = "\n                ],\n              ]),\n            ),\n          ),\n        ),\n        actions: ["
if cert_start in text and cert_end in text:
    a = text.find(cert_start)
    b = text.find(cert_end, a)
    if a >= 0 and b >= 0:
        text = text[:a] + "for (final entry in selectedCertificates.values)\n                    addEmployeeSelectedCertificateCard(context, entry, setDialogState)," + text[b:]

# Keep Add Employee modal a practical size after narrowing.
text = text.replace('width: 1060,', 'width: 790,')

# -----------------------------------------------------------------------------
# Add row-level Mark as Resigned action beside View/Edit/Delete in Employees.
# -----------------------------------------------------------------------------
if 'typedef ExtraRowActionBuilder' not in text:
    text = text.replace(
        "typedef ViewHandler = Future<void> Function(\n    BuildContext context, Map<String, dynamic> row);",
        "typedef ViewHandler = Future<void> Function(\n    BuildContext context, Map<String, dynamic> row);\ntypedef ExtraRowActionBuilder = Widget? Function(\n    BuildContext context, Map<String, dynamic> row, VoidCallback refresh);",
        1,
    )

if 'final ExtraRowActionBuilder? extraAction;' not in text:
    text = text.replace('  final EditHandler? onApprove;\n', '  final EditHandler? onApprove;\n  final ExtraRowActionBuilder? extraAction;\n', 1)
    text = text.replace('      this.onApprove,\n', '      this.onApprove,\n      this.extraAction,\n', 1)

if 'if (widget.extraAction != null) count++;' not in text:
    text = text.replace('    if (widget.showDelete) count++;\n', '    if (widget.showDelete) count++;\n    if (widget.extraAction != null) count++;\n', 1)

if 'final Widget? extraAction;' not in text:
    text = text.replace('  final VoidCallback? onApprove;\n  final VoidCallback? onDelete;\n', '  final VoidCallback? onApprove;\n  final Widget? extraAction;\n  final VoidCallback? onDelete;\n', 1)
    text = text.replace('      this.onApprove,\n      this.onDelete});\n', '      this.onApprove,\n      this.extraAction,\n      this.onDelete});\n', 1)

if 'extraAction: widget.extraAction == null' not in text:
    text = text.replace(
        "                  onApprove: widget.onApprove == null\n                      ? null\n                      : () => widget.onApprove!(context, rows[i], refresh),\n                  onDelete:",
        "                  onApprove: widget.onApprove == null\n                      ? null\n                      : () => widget.onApprove!(context, rows[i], refresh),\n                  extraAction: widget.extraAction == null\n                      ? null\n                      : widget.extraAction!(context, rows[i], refresh),\n                  onDelete:",
        1,
    )

if 'if (extraAction != null) extraAction!,' not in text:
    text = text.replace(
        "               if (onApprove != null)\n                 IconButton(\n                     tooltip: 'Approve Applied Rank',\n                     onPressed: onApprove,\n                     icon: const Icon(Icons.check_circle_rounded,\n                         color: Color(0xFF16A34A), size: 20)),\n               if (onDelete != null)",
        "               if (onApprove != null)\n                 IconButton(\n                     tooltip: 'Approve Applied Rank',\n                     onPressed: onApprove,\n                     icon: const Icon(Icons.check_circle_rounded,\n                         color: Color(0xFF16A34A), size: 20)),\n               if (extraAction != null) extraAction!,\n               if (onDelete != null)",
        1,
    )

# Action helper and resignation behavior with confirmation + success alert.
if 'bool employeeRowIsResignedForAction(' not in text:
    action_helper = r'''
bool employeeRowIsResignedForAction(Map<String, dynamic> row) =>
    formatValue(row['employment_status']).toLowerCase().contains('resign') ||
    formatValue(row['status']).toLowerCase().contains('resign');

Widget? employeeResignRowAction(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) {
  if (employeeRowIsResignedForAction(row)) return null;
  return IconButton(
    tooltip: 'Mark as Resigned',
    onPressed: () => markEmployeeAsResigned(context, row, refresh),
    icon: const Icon(Icons.person_off_rounded, color: _danger, size: 20),
  );
}

Future<void> markEmployeeAsResigned(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final id = row['id'];
  if (id == null) return;
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Mark as Resigned?'),
      content: Text(
          'This will mark ${formatValue(row['full_name'])} as resigned and also mark linked contract records as Resigned.'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton.tonalIcon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.person_off_rounded),
          label: const Text('Mark as Resigned'),
        ),
      ],
    ),
  );
  if (ok != true) return;
  try {
    await db.from('employees').update({'employment_status': 'resigned'}).eq('id', id);
    await db.from('employee_contracts').update({'status': 'Resigned'}).eq('employee_id', id);
    refresh();
    await showActionAlert(context, 'Employee Marked as Resigned',
        '${formatValue(row['full_name'])} was marked as resigned.',
        icon: Icons.person_off_rounded, iconColor: _danger);
  } catch (e) {
    if (context.mounted) showSnack(context, 'Mark as resigned failed: $e');
  }
}

'''
    # Prefer inserting before editEmployee if available, otherwise before contract types.
    marker = 'Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,'
    if marker not in text:
        marker = 'const _contractTypeOptions = <EditOption>['
    insert_before(marker, action_helper)
else:
    # Replace older markEmployeeAsResigned function with the success-alert version if present.
    start = text.find('Future<void> markEmployeeAsResigned(')
    end = text.find('\nFuture<void> editEmployee(', start)
    if start >= 0 and end > start:
        replacement = r'''Future<void> markEmployeeAsResigned(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final id = row['id'];
  if (id == null) return;
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Mark as Resigned?'),
      content: Text(
          'This will mark ${formatValue(row['full_name'])} as resigned and also mark linked contract records as Resigned.'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton.tonalIcon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.person_off_rounded),
          label: const Text('Mark as Resigned'),
        ),
      ],
    ),
  );
  if (ok != true) return;
  try {
    await db.from('employees').update({'employment_status': 'resigned'}).eq('id', id);
    await db.from('employee_contracts').update({'status': 'Resigned'}).eq('employee_id', id);
    refresh();
    await showActionAlert(context, 'Employee Marked as Resigned',
        '${formatValue(row['full_name'])} was marked as resigned.',
        icon: Icons.person_off_rounded, iconColor: _danger);
  } catch (e) {
    if (context.mounted) showSnack(context, 'Mark as resigned failed: $e');
  }
}
'''
        text = text[:start] + replacement + text[end:]

if 'extraAction: employeeResignRowAction,' not in text:
    text = text.replace('              onEdit: editEmployee,\n', '              onEdit: editEmployee,\n              extraAction: employeeResignRowAction,\n', 1)

# Add success alert after Add Employee save. Keep snackbar as fallback removed.
text = text.replace(
    """    refresh();
    showSnack(context,
        'Employee, contract, license, and certificate information saved.');""",
    """    refresh();
    await showActionAlert(context, 'Employee Saved',
        'Employee, contract, license, and certificate information were saved successfully.');""",
)
text = text.replace(
    """    refresh();
    showSnack(context, 'Employee, contract, and credential details saved.');""",
    """    refresh();
    await showActionAlert(context, 'Employee Saved',
        'Employee, contract, and credential details were saved successfully.');""",
)

# Dispose certificate attachment controller if the field exists.
text = text.replace("""  void dispose() {
    number.dispose();
    expiry.dispose();
  }
}""", """  void dispose() {
    number.dispose();
    expiry.dispose();
    attachment.dispose();
  }
}""", 1)

if text == original:
    print('No changes applied. Employee modal credential UI/resigned alert fixes may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Fixed Add Employee license/certificate UI, added visible Mark as Resigned row action, and added alert modals.')
