from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

old_edit = """Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await activeEmployeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Contract' : 'Edit Contract',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('contract_type', 'Contract Type'),
      const EditField('contract_start_date', 'Start Date', kind: FieldKind.date),
      const EditField('duration_months', 'Duration In Months', kind: FieldKind.integer),
      const EditField('contract_end_date', 'End Date', kind: FieldKind.date),
      const EditField('attachment_url', 'Attachment URL'),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived'), EditOption('Resigned', 'Resigned')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}
"""
new_edit = """Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showContractDialog(
    context,
    isAdd ? await activeEmployeeOptions() : const <EditOption>[],
    await contractTypeOptions(),
    row,
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}
"""
if old_edit in s:
    s = s.replace(old_edit, new_edit, 1)
elif new_edit not in s:
    raise SystemExit('editContract block not found')

marker = """class SelectedLicenseInput {
"""
insert = r'''String contractStatusFromEndDate(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final end = DateTime(parsed.year, parsed.month, parsed.day);
  if (end.isBefore(today)) return 'Expired';
  if (end.difference(today).inDays <= 90) return 'For Renewal';
  return 'On-going';
}

Future<List<String>> contractTypeOptions() async {
  const defaults = <String>[
    'Probationary Contract',
    'Regular Contract',
    'Fixed-Term Contract',
    'Part-Time Contract',
    'Full-Time Contract',
    'Service Contract',
  ];
  final seen = <String>{};
  final out = <String>[];
  void addType(String value) {
    final clean = value.trim();
    if (clean.isEmpty) return;
    if (seen.add(clean.toLowerCase())) out.add(clean);
  }
  for (final value in defaults) {
    addType(value);
  }
  try {
    final rows = await db.from('employee_contracts').select('contract_type').order('contract_type').limit(3000);
    for (final r in rows) {
      addType('${r['contract_type'] ?? ''}');
    }
  } catch (_) {}
  out.sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
  return out;
}

Future<void> pickAndUploadContractPdf(BuildContext context, TextEditingController attachmentUrl, void Function(void Function()) setDialogState, void Function(String) setFileName, void Function(bool) setUploading) async {
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
  setDialogState(() => setUploading(true));
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
    final path = 'contracts/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes, fileOptions: const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      attachmentUrl.text = url;
      setFileName(file.name);
      setUploading(false);
    });
  } catch (e) {
    setDialogState(() => setUploading(false));
    showSnack(context, 'Contract PDF upload failed: $e');
  }
}

Widget contractDatePickerBox(BuildContext context, String label, TextEditingController controller, void Function(String) onPicked) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: true,
        decoration: InputDecoration(labelText: label, hintText: 'January 02, 2026', suffixIcon: const Icon(Icons.calendar_month_rounded)),
        validator: (v) {
          if (v == null || v.trim().isEmpty) return null;
          if (parseFlexibleDate(v.trim()) == null) return 'Use date picker or January 02, 2026';
          return null;
        },
        onTap: () async {
          final initial = parseFlexibleDate(controller.text) ?? DateTime.now();
          final picked = await showDatePicker(
            context: context,
            initialDate: initial,
            firstDate: DateTime(1990),
            lastDate: DateTime(2100),
          );
          if (picked == null) return;
          final text = DateFormat('MMMM dd, yyyy').format(picked);
          controller.text = text;
          onPicked(text);
        },
      ),
    );

Widget contractTypeAutocompleteBox(TextEditingController controller, List<String> contractTypes) => SizedBox(
      width: 354,
      child: Autocomplete<String>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option,
        optionsBuilder: (textEditingValue) {
          final options = contractTypes.toList()..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return options;
          return options.where((option) => option.toLowerCase().contains(query));
        },
        onSelected: (option) => controller.text = option,
        fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: const InputDecoration(labelText: 'Contract Type', hintText: 'Select or type contract type', suffixIcon: Icon(Icons.search_rounded)),
          validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
          onChanged: (value) => controller.text = value,
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
                  return ListTile(dense: true, title: Text(option, overflow: TextOverflow.ellipsis), onTap: () => onSelected(option));
                },
              ),
            ),
          ),
        ),
      ),
    );

Future<Map<String, dynamic>?> showContractDialog(BuildContext context, List<EditOption> employees, List<String> contractTypes, Map<String, dynamic>? initial) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  final contractType = TextEditingController(text: formatEditValue(initial?['contract_type']));
  final startDate = TextEditingController(text: formatEditValue(initial?['contract_start_date']));
  final durationMonths = TextEditingController(text: formatEditValue(initial?['duration_months']));
  final endDate = TextEditingController(text: formatEditValue(initial?['contract_end_date']));
  final attachmentUrl = TextEditingController(text: formatEditValue(initial?['attachment_url']));
  String status = contractStatusFromEndDate(endDate.text);
  if (status.isEmpty) status = formatEditValue(initial?['status']);
  if (!const ['On-going', 'For Renewal', 'Expired'].contains(status)) status = '';
  String attachmentFileName = attachmentUrl.text.trim().isEmpty ? '' : 'Existing contract PDF attached';
  bool uploadingAttachment = false;

  void refreshStatus(StateSetter setDialogState) {
    setDialogState(() => status = contractStatusFromEndDate(endDate.text));
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Contract' : 'Edit Contract'),
        content: SizedBox(
          width: 760,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                if (isAdd)
                  SizedBox(
                    width: 354,
                    child: Autocomplete<EditOption>(
                      displayStringForOption: (option) => option.label,
                      optionsBuilder: (textEditingValue) {
                        final sortedEmployees = uniqueOptions(employees).toList()..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
                        final query = textEditingValue.text.trim().toLowerCase();
                        if (query.isEmpty) return sortedEmployees;
                        final normalizedQuery = normalizeName(query);
                        return sortedEmployees.where((option) {
                          final label = option.label.toLowerCase();
                          final normalizedLabel = normalizeName(option.label);
                          return label.contains(query) || normalizedLabel.contains(normalizedQuery);
                        });
                      },
                      onSelected: (option) => setDialogState(() => employeeId = option.value),
                      fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(labelText: 'Employee Name', hintText: 'Select or type employee name', suffixIcon: Icon(Icons.search_rounded)),
                        validator: (_) => employeeId == null || employeeId!.isEmpty ? 'Please select employee from the list' : null,
                        onChanged: (value) => setDialogState(() {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees).where((option) => option.label.toLowerCase() == typed).toList();
                          employeeId = exact.isNotEmpty ? exact.first.value : null;
                        }),
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
                                return ListTile(dense: true, title: Text(option.label, overflow: TextOverflow.ellipsis), onTap: () => onSelected(option));
                              },
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                contractTypeAutocompleteBox(contractType, contractTypes),
                contractDatePickerBox(context, 'Start Date', startDate, (_) {}),
                textBox('Duration In Months', durationMonths, kind: FieldKind.integer),
                contractDatePickerBox(context, 'End Date', endDate, (_) => refreshStatus(setDialogState)),
                SizedBox(
                  width: 354,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      OutlinedButton.icon(
                        onPressed: uploadingAttachment ? null : () => pickAndUploadContractPdf(context, attachmentUrl, setDialogState, (name) => attachmentFileName = name, (v) => uploadingAttachment = v),
                        icon: uploadingAttachment ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.picture_as_pdf_rounded),
                        label: Text(uploadingAttachment ? 'Uploading...' : (attachmentFileName.isEmpty ? 'Attach Contract' : 'Change Contract')),
                      ),
                      const SizedBox(height: 8),
                      Text(attachmentFileName.isEmpty ? 'No contract PDF attached' : attachmentFileName, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 12, color: attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700)),
                    ]),
                  ),
                ),
                SizedBox(width: 354, child: Padding(padding: const EdgeInsets.only(top: 8), child: StatusChip(status.isEmpty ? 'Select End Date' : status))),
                SizedBox(width: 728, child: Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)), child: const Text('Status is automatic from End Date: expired when past due, for renewal within 90 days, otherwise on-going.', style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)))),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              final finalStatus = contractStatusFromEndDate(endDate.text);
              final out = <String, dynamic>{
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'contract_type': emptyToNull(contractType.text),
                'contract_start_date': toIsoDateInput(startDate.text),
                'duration_months': int.tryParse(durationMonths.text.replaceAll(RegExp(r'[^0-9-]'), '')),
                'contract_end_date': toIsoDateInput(endDate.text),
                'attachment_url': emptyToNull(attachmentUrl.text),
                'status': finalStatus.isEmpty ? null : finalStatus,
              };
              Navigator.pop(context, out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  for (final c in [contractType, startDate, durationMonths, endDate, attachmentUrl]) {
    c.dispose();
  }
  return result;
}

'''
if 'Future<Map<String, dynamic>?> showContractDialog(' not in s:
    if marker not in s:
        raise SystemExit('contract dialog insert marker not found')
    s = s.replace(marker, insert + marker, 1)

p.write_text(s)
