from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

def replace_between(source: str, start: str, end: str, replacement: str) -> str:
    a = source.find(start)
    if a < 0:
        raise SystemExit(f'Missing start marker: {start}')
    b = source.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f'Missing end marker after {start}: {end}')
    return source[:a] + replacement + source[b:]

def patch_between(source: str, start: str, end: str, patcher) -> str:
    a = source.find(start)
    if a < 0:
        return source
    b = source.find(end, a + len(start))
    if b < 0:
        return source
    block = source[a:b]
    return source[:a] + patcher(block) + source[b:]

# 1) Make PDF picker return after cancel instead of waiting forever.
if 'Future<html.File?> pickPdfFileOrNull' not in text:
    helper = r'''
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
    marker = 'Future<UploadedAttachment?> pickAndUploadContractPdf('
    if marker not in text:
        raise SystemExit('Could not find pickAndUploadContractPdf marker.')
    text = text.replace(marker, helper + marker, 1)

# Replace old file input code in contract/license/certificate upload helpers.
old_picker = """  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
"""
new_picker = """  final file = await pickPdfFileOrNull();
"""
text = text.replace(old_picker, new_picker)

# 2) Tighten Add Employee modal width and checkbox layout so it does not leave a huge empty right side.
def patch_add_employee_ui(block: str) -> str:
    block = block.replace('width: 1060,', 'width: 790,', 1)
    block = block.replace('width: 278,', 'width: 228,')
    block = block.replace("const DialogSectionTitle('License Information (Optional)'),", "const DialogSectionTitle('License Information (Optional)'),")
    block = block.replace("const DialogSectionTitle('Certificate Information (Optional)'),", "const DialogSectionTitle('Certificate Information (Optional)'),")
    return block

text = patch_between(text, 'Future<AddEmployeeFullResult?> showAddEmployeeFullDialog(', 'Future<void> addEmployeeFull(', patch_add_employee_ui)

# 3) Ensure contract upload button always resets when no file is selected/cancelled.
text = text.replace("""                                final uploaded = await pickAndUploadContractPdf(context);
                                setDialogState(() {
                                  if (uploaded != null) {
                                    contractAttachmentUrl = uploaded.url;
                                    contractAttachmentFileName = uploaded.fileName;
                                  }
                                  uploadingContract = false;
                                });""", """                                final uploaded = await pickAndUploadContractPdf(context);
                                if (!context.mounted) return;
                                setDialogState(() {
                                  if (uploaded != null) {
                                    contractAttachmentUrl = uploaded.url;
                                    contractAttachmentFileName = uploaded.fileName;
                                  }
                                  uploadingContract = false;
                                });""")

# Also protect the Contract module upload button block.
text = text.replace("""                                final uploaded =
                                    await pickAndUploadContractPdf(context);
                                if (uploaded != null) {
                                  setDialogState(() {
                                    attachmentUrl = uploaded.url;
                                    attachmentFileName = uploaded.fileName;
                                  });
                                }
                                setDialogState(
                                    () => uploadingAttachment = false);""", """                                final uploaded =
                                    await pickAndUploadContractPdf(context);
                                if (!context.mounted) return;
                                setDialogState(() {
                                  if (uploaded != null) {
                                    attachmentUrl = uploaded.url;
                                    attachmentFileName = uploaded.fileName;
                                  }
                                  uploadingAttachment = false;
                                });""")

# 4) Add / ensure Mark as Resigned UI and update flow on Edit Employee.
if 'class EmployeeStatusActionRow extends StatelessWidget' not in text:
    status_widget = r'''
class EmployeeStatusActionRow extends StatelessWidget {
  final String status;
  final Future<void> Function() onMarkResigned;
  const EmployeeStatusActionRow(
      {super.key, required this.status, required this.onMarkResigned});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 728,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _line)),
          child: Row(children: [
            const Text('Status:',
                style: TextStyle(color: _muted, fontWeight: FontWeight.w800)),
            const SizedBox(width: 10),
            StatusChip(status.isEmpty || status == '-' ? 'Active' : status),
            const Spacer(),
            FilledButton.tonalIcon(
              onPressed: status.toLowerCase().contains('resign')
                  ? null
                  : onMarkResigned,
              icon: const Icon(Icons.person_off_rounded),
              label: const Text('Mark as Resigned'),
            ),
          ]),
        ),
      );
}

'''
    marker = 'String dialogSectionForField(String key) {'
    if marker in text:
        text = text.replace(marker, status_widget + marker, 1)

if 'Future<void> markEmployeeAsResigned(' not in text:
    mark_helper = r'''
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
    if (context.mounted) showSnack(context, 'Employee marked as resigned.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Mark as resigned failed: $e');
  }
}

'''
    marker = 'Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,'
    if marker in text:
        text = text.replace(marker, mark_helper + marker, 1)

if 'Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,' in text and 'const _contractTypeOptions = <EditOption>[' in text:
    edit_block = r'''Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final normalized = normalizeRow(row ?? {});
  final data = await showRecordDialog(
    context,
    row == null ? 'Add Employee' : 'Edit Employee',
    employeeEditFields(),
    normalized,
    prefix: row == null
        ? const []
        : [
            EmployeeStatusActionRow(
              status: formatValue(normalized['employment_status']),
              onMarkResigned: () => markEmployeeAsResigned(context, normalized, refresh),
            ),
          ],
  );
  if (data == null) return;
  data['name_key'] = normalizeName(data['full_name']?.toString() ?? '');
  data['date_hired'] ??= data['starting_date'];
  data['starting_date'] ??= data['date_hired'];
  await saveRow(context, 'employees', row?['id'], data, refresh);
}

'''
    text = replace_between(text, 'Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,', 'const _contractTypeOptions = <EditOption>[', edit_block)

# 5) Remove removed employee fields from view details as well, to match the modal cleanup.
text = text.replace("""                'Current Salary': 'current_salary',
                'License Summary': 'license_summary',
                'Notes': 'notes',
""", "")

if text == original:
    print('No changes applied. Employee modal UI/upload/resigned fixes may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Fixed Add Employee modal UI, PDF cancel/loading, and Edit Employee Mark as Resigned button.')
