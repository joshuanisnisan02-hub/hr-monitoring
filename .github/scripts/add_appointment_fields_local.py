from pathlib import Path
import re

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('Run from project root')
s = p.read_text(encoding='utf-8-sig')
o = s

def match_brace(src, i):
    d=0; sq=dq=False; esc=False
    for n in range(i, len(src)):
        c=src[n]
        if sq:
            if c=='\\' and not esc: esc=True; continue
            if c=="'" and not esc: sq=False
            esc=False; continue
        if dq:
            if c=='\\' and not esc: esc=True; continue
            if c=='"' and not esc: dq=False
            esc=False; continue
        if c=="'": sq=True; continue
        if c=='"': dq=True; continue
        if c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: return n
    return -1

# Add constants and small searchable autocomplete widget.
if 'appointmentTypeOptions = <EditOption>' not in s:
    insert = r'''
const appointmentCategoryOptions = <EditOption>[
  EditOption('FULL-TIME', 'FULL-TIME'),
  EditOption('PART-TIME', 'PART-TIME'),
  EditOption('PROBATIONARY', 'PROBATIONARY'),
  EditOption('COMPLIANCE', 'COMPLIANCE'),
  EditOption('ADMINISTRATIVE', 'ADMINISTRATIVE'),
  EditOption('ACADEMIC', 'ACADEMIC'),
];

const appointmentTypeOptions = <EditOption>[
  EditOption('PACUCOA', 'PACUCOA'),
  EditOption('RQUAT (CHED)', 'RQUAT (CHED)'),
  EditOption('INSTITUTION', 'INSTITUTION'),
  EditOption('BASIC ED', 'BASIC ED'),
  EditOption('ESC', 'ESC'),
  EditOption('DEPED', 'DEPED'),
  EditOption('PEAC', 'PEAC'),
];

Widget searchableOptionBox(String label, TextEditingController controller,
        List<EditOption> options, {double width = 354}) =>
    SizedBox(
      width: width,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.label,
        optionsBuilder: (value) {
          final q = value.text.trim().toLowerCase();
          final list = uniqueOptions(options).toList()
            ..sort((a, b) => a.label.compareTo(b.label));
          if (q.isEmpty) return list;
          return list.where((x) =>
              x.label.toLowerCase().contains(q) ||
              x.value.toLowerCase().contains(q));
        },
        onSelected: (option) => controller.text = option.value,
        fieldViewBuilder: (context, textController, focusNode, _) =>
            TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: InputDecoration(
              labelText: label,
              hintText: 'Select or type $label',
              suffixIcon: const Icon(Icons.search_rounded)),
          validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
          onChanged: (v) => controller.text = v,
        ),
      ),
    );

Future<UploadedAttachment?> pickAndUploadAppointmentPdf(BuildContext context) async {
  final file = await pickPdfFileOrNull();
  if (file == null) return null;
  if (!file.name.toLowerCase().endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return null;
  }
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    final bytes = result is ByteBuffer ? Uint8List.view(result) : result as Uint8List;
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final uploadPath = 'appointments/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(uploadPath, bytes,
        fileOptions: const FileOptions(contentType: 'application/pdf', upsert: true));
    return UploadedAttachment(db.storage.from('hr-attachments').getPublicUrl(uploadPath), file.name);
  } catch (e) {
    showSnack(context, 'Appointment PDF upload failed: $e');
    return null;
  }
}

'''
    s = s.replace('Future<html.File?> pickPdfFileOrNull() async {', insert + 'Future<html.File?> pickPdfFileOrNull() async {', 1)

# Load new columns.
s = s.replace("'id, employee_id, category, appointment_title, employees(full_name)'",
              "'id, employee_id, category, appointment_title, appointment_type, other_duties, attachment_url, employees(full_name)'", 1)

# Table labels/columns.
s = s.replace("searchHint: 'Search employee, type, or appointment'", "searchHint: 'Search employee, appointment type, appointment, other duties, type, or PDF'", 1)
s = s.replace("GridCol('category', 'Type', flex: 2),", "GridCol('category', 'Appointment Type', flex: 2),", 1)
s = s.replace("GridCol('appointment_title', 'Appointment', flex: 4),", "GridCol('appointment_title', 'Appointment', flex: 3),\n            GridCol('other_duties', 'Other Duties', flex: 3),\n            GridCol('appointment_type', 'Type', flex: 2),", 1)

# Update viewAppointment details if present.
s = s.replace("'Type': 'category',\n      'Appointment': 'appointment_title',", "'Appointment Type': 'category',\n      'Appointment': 'appointment_title',\n      'Other Duties': 'other_duties',\n      'Type': 'appointment_type',", 1)

# Replace editAppointment with richer dialog.
start = s.find('Future<void> editAppointment(')
if start >= 0:
    b = s.find('{', start); e = match_brace(s, b); le = s.find('\n', e)
    repl = r'''Future<void> editAppointment(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final source = normalizeRow(row ?? {});
  final employees = await employeeOptions();
  String? employeeId = isAdd ? null : source['employee_id']?.toString();
  final category = TextEditingController(text: formatEditValue(source['category']));
  final appointmentTitle = TextEditingController(text: formatEditValue(source['appointment_title']));
  final otherDuties = TextEditingController(text: formatEditValue(source['other_duties']));
  final appointmentType = TextEditingController(text: formatEditValue(source['appointment_type']));
  String attachmentUrl = formatEditValue(source['attachment_url']);
  String attachmentFileName = attachmentUrl.isEmpty || attachmentUrl == '-'
      ? ''
      : Uri.decodeFull(attachmentUrl.split('/').last.split('?').first);
  bool uploading = false;
  final formKey = GlobalKey<FormState>();

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Appointment' : 'Edit Appointment'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                const DialogSectionTitle('Employee Information'),
                if (isAdd)
                  employeeAutocompleteField(
                    employees: employees,
                    employeeId: employeeId,
                    width: 728,
                    onEmployeeChanged: (v) => setDialogState(() => employeeId = v),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(source)),
                const DialogSectionTitle('Appointment Information'),
                searchableOptionBox('Appointment Type', category, appointmentCategoryOptions),
                SizedBox(width: 354, child: TextFormField(controller: appointmentTitle, decoration: const InputDecoration(labelText: 'Appointment'), validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null)),
                SizedBox(width: 728, child: TextFormField(controller: otherDuties, minLines: 2, maxLines: 4, decoration: const InputDecoration(labelText: 'Other Duties'))),
                searchableOptionBox('Type', appointmentType, appointmentTypeOptions),
                SizedBox(
                  width: 354,
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18), border: Border.all(color: _line)),
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      OutlinedButton.icon(
                        onPressed: uploading ? null : () async {
                          setDialogState(() => uploading = true);
                          final uploaded = await pickAndUploadAppointmentPdf(context);
                          if (!context.mounted) return;
                          setDialogState(() {
                            if (uploaded != null) { attachmentUrl = uploaded.url; attachmentFileName = uploaded.fileName; }
                            uploading = false;
                          });
                        },
                        icon: uploading ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.picture_as_pdf_rounded),
                        label: Text(uploading ? 'Uploading...' : (attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF')),
                      ),
                      const SizedBox(height: 8),
                      Text(attachmentFileName.isEmpty ? 'No PDF attached' : attachmentFileName, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(color: attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700, fontSize: 12)),
                      if (attachmentUrl.trim().isNotEmpty && attachmentUrl != '-') TextButton.icon(onPressed: () => openPdfAttachment(context, attachmentUrl), icon: const Icon(Icons.open_in_new_rounded), label: const Text('Open PDF')),
                    ]),
                  ),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(onPressed: () {
            if (!formKey.currentState!.validate()) return;
            Navigator.pop(context, <String, dynamic>{
              'employee_id': isAdd ? emptyToNull(employeeId) : source['employee_id'],
              'category': category.text.trim(),
              'appointment_title': appointmentTitle.text.trim(),
              'other_duties': otherDuties.text.trim(),
              'appointment_type': appointmentType.text.trim(),
              'attachment_url': emptyToNull(attachmentUrl),
            }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty));
          }, child: const Text('Save')),
        ],
      ),
    ),
  );
  for (final c in [category, appointmentTitle, otherDuties, appointmentType]) { c.dispose(); }
  if (result == null) return;
  await saveRow(context, 'employee_appointments', isAdd ? null : source['id'], result, refresh);
}

'''
    s = s[:start] + repl + s[le+1:]

p.write_text(s, encoding='utf-8')
print('Applied appointment module fields: other duties, PDF, appointment type label, and searchable Type.')
