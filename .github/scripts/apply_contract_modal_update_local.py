from pathlib import Path
import re

MAIN_DART = Path('lib/main.dart')
if not MAIN_DART.exists():
    raise SystemExit('Run this from the Flutter project root. lib/main.dart was not found.')

text = MAIN_DART.read_text(encoding='utf-8')
original = text


def matching_brace(source, open_i):
    depth = 0
    for i in range(open_i, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    raise SystemExit('Could not find matching closing brace in lib/main.dart.')


def line_end(source, i):
    if i < len(source) and source[i:i + 2] == '\r\n':
        return i + 2
    if i < len(source) and source[i] == '\n':
        return i + 1
    return i

# Also repair the orphaned async block that the old resigned duplicate script could leave behind.
for m in reversed(list(re.finditer(r'(?m)^\s*\)\s*async\s*\{\s*\n', text))):
    preview = text[m.start():m.start() + 800]
    if 'loadResignedEmployeeIdSet' not in preview or 'loadEmployees(limit: limit)' not in preview:
        continue
    open_i = text.find('{', m.start(), m.end())
    close_i = matching_brace(text, open_i)
    text = text[:m.start()] + text[line_end(text, close_i + 1):]

replacement = r'''const _contractTypeOptions = <EditOption>[
  EditOption('Permanent', 'Permanent'),
  EditOption('Probationary', 'Probationary'),
  EditOption('Contractual', 'Contractual'),
  EditOption('Part-time', 'Part-time'),
  EditOption('Full-time', 'Full-time'),
  EditOption('Temporary', 'Temporary'),
  EditOption('Renewal', 'Renewal'),
];

class UploadedAttachment {
  final String url;
  final String fileName;
  const UploadedAttachment(this.url, this.fileName);
}

Future<List<EditOption>> contractTypeOptions() async {
  final rows = await db.from('employee_contracts').select('contract_type').limit(5000);
  final out = <EditOption>[];
  final seen = <String>{};

  void addType(Object? raw) {
    final value = '${raw ?? ''}'.trim();
    if (value.isEmpty || value == '-') return;
    if (seen.add(value.toLowerCase())) out.add(EditOption(value, value));
  }

  for (final option in _contractTypeOptions) {
    addType(option.value);
  }
  for (final item in rows) {
    if (item is Map) addType(item['contract_type']);
  }
  out.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return out;
}

String contractDateText(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  return DateFormat('MMMM dd, yyyy').format(parsed);
}

DateTime addContractMonths(DateTime start, int months) {
  final monthIndex = start.month + months - 1;
  final year = start.year + (monthIndex ~/ 12);
  final month = (monthIndex % 12) + 1;
  final lastDay = DateTime(year, month + 1, 0).day;
  final day = start.day > lastDay ? lastDay : start.day;
  return DateTime(year, month, day);
}

String contractStatusFromEndDate(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final end = DateTime(parsed.year, parsed.month, parsed.day);
  final days = end.difference(today).inDays;
  if (days < 0) return 'Expired';
  if (days <= 90) return 'For Renewal';
  return 'On-going';
}

Future<UploadedAttachment?> pickAndUploadContractPdf(BuildContext context) async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return null;

  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return null;
  }

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
    return UploadedAttachment(url, file.name);
  } catch (e) {
    showSnack(context, 'PDF upload failed: $e');
    return null;
  }
}

Widget contractTypeAutocompleteBox(TextEditingController controller, List<EditOption> options) => SizedBox(
      width: 354,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.label,
        optionsBuilder: (textEditingValue) {
          final sorted = uniqueOptions(options).toList()..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return sorted;
          final normalizedQuery = normalizeName(query);
          return sorted.where((option) {
            final label = option.label.toLowerCase();
            final normalizedLabel = normalizeName(option.label);
            return label.contains(query) || normalizedLabel.contains(normalizedQuery);
          });
        },
        onSelected: (option) => controller.text = option.value,
        fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: const InputDecoration(
            labelText: 'Contract Type',
            hintText: 'Select or type contract type',
            suffixIcon: Icon(Icons.search_rounded),
          ),
          validator: (value) => value == null || value.trim().isEmpty ? 'Required' : null,
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
                  return ListTile(
                    dense: true,
                    title: Text(option.label, overflow: TextOverflow.ellipsis),
                    onTap: () => onSelected(option),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );

Widget contractDatePickerBox(BuildContext context, TextEditingController controller, StateSetter setDialogState, VoidCallback recomputeContract) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: true,
        decoration: const InputDecoration(
          labelText: 'Start Date',
          hintText: 'Select start date',
          suffixIcon: Icon(Icons.calendar_month_rounded),
        ),
        validator: (value) {
          if (value == null || value.trim().isEmpty) return 'Required';
          if (parseFlexibleDate(value.trim()) == null) return 'Invalid date';
          return null;
        },
        onTap: () async {
          final current = parseFlexibleDate(controller.text) ?? DateTime.now();
          final picked = await showDatePicker(
            context: context,
            initialDate: current,
            firstDate: DateTime(1950),
            lastDate: DateTime(2100),
          );
          if (picked == null) return;
          setDialogState(() {
            controller.text = DateFormat('MMMM dd, yyyy').format(picked);
            recomputeContract();
          });
        },
      ),
    );

Widget contractReadOnlyBox(String label, TextEditingController controller, {IconData? icon}) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: true,
        style: const TextStyle(color: _muted, fontWeight: FontWeight.w800),
        decoration: InputDecoration(labelText: label, fillColor: const Color(0xFFF8FAFC), suffixIcon: icon == null ? null : Icon(icon)),
      ),
    );

Future<Map<String, dynamic>?> showContractDialog(BuildContext context, List<EditOption> employees, List<EditOption> contractTypes, Map<String, dynamic>? initial) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  String selectedEmployeeName = isAdd ? '' : linkedEmployeeName(initial);
  final contractType = TextEditingController(text: formatEditValue(initial?['contract_type']));
  final startDate = TextEditingController(text: contractDateText(initial?['contract_start_date']));
  final durationMonths = TextEditingController(text: formatEditValue(initial?['duration_months']));
  final endDate = TextEditingController(text: contractDateText(initial?['contract_end_date']));
  final status = TextEditingController(text: formatEditValue(initial?['status']));
  String attachmentUrl = formatEditValue(initial?['attachment_url']);
  String attachmentFileName = attachmentUrl.isEmpty || attachmentUrl == '-' ? '' : Uri.decodeFull(attachmentUrl.split('/').last.split('?').first);
  bool uploadingAttachment = false;

  void recomputeContract() {
    final start = parseFlexibleDate(startDate.text);
    final months = int.tryParse(durationMonths.text.trim());
    if (start != null && months != null && months > 0) {
      final computedEnd = addContractMonths(DateTime(start.year, start.month, start.day), months);
      endDate.text = DateFormat('MMMM dd, yyyy').format(computedEnd);
    }
    status.text = contractStatusFromEndDate(endDate.text);
  }

  if (endDate.text.isEmpty) {
    recomputeContract();
  } else {
    status.text = contractStatusFromEndDate(endDate.text);
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
                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        selectedEmployeeName = option.label;
                      }),
                      fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: 'Employee Name',
                          hintText: 'Select or type employee name',
                          suffixIcon: Icon(Icons.search_rounded),
                        ),
                        validator: (_) => employeeId == null || employeeId!.isEmpty ? 'Please select employee from the list' : null,
                        onChanged: (value) => setDialogState(() {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees).where((option) => option.label.toLowerCase() == typed).toList();
                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            selectedEmployeeName = exact.first.label;
                          } else {
                            employeeId = null;
                            selectedEmployeeName = '';
                          }
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
                                return ListTile(
                                  dense: true,
                                  title: Text(option.label, overflow: TextOverflow.ellipsis),
                                  onTap: () => onSelected(option),
                                );
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
                contractDatePickerBox(context, startDate, setDialogState, recomputeContract),
                SizedBox(
                  width: 354,
                  child: TextFormField(
                    controller: durationMonths,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Duration In Months'),
                    validator: (value) {
                      final months = int.tryParse('${value ?? ''}'.trim());
                      if (months == null || months <= 0) return 'Enter valid months';
                      return null;
                    },
                    onChanged: (_) => setDialogState(recomputeContract),
                  ),
                ),
                contractReadOnlyBox('End Date', endDate, icon: Icons.event_available_rounded),
                contractReadOnlyBox('Status', status, icon: Icons.verified_rounded),
                SizedBox(
                  width: 728,
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
                    child: Row(children: [
                      const Icon(Icons.picture_as_pdf_rounded, color: _danger),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          const Text('Attach File (Upload PDF)', style: TextStyle(color: Color(0xFF1E40AF), fontWeight: FontWeight.w700, fontSize: 12)),
                          const SizedBox(height: 4),
                          Text(
                            attachmentFileName.isEmpty ? 'No PDF attached' : attachmentFileName,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(color: attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w800),
                          ),
                        ]),
                      ),
                      const SizedBox(width: 12),
                      OutlinedButton.icon(
                        onPressed: uploadingAttachment
                            ? null
                            : () async {
                                setDialogState(() => uploadingAttachment = true);
                                final uploaded = await pickAndUploadContractPdf(context);
                                if (uploaded != null) {
                                  setDialogState(() {
                                    attachmentUrl = uploaded.url;
                                    attachmentFileName = uploaded.fileName;
                                  });
                                }
                                setDialogState(() => uploadingAttachment = false);
                              },
                        icon: uploadingAttachment ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.upload_file_rounded),
                        label: Text(uploadingAttachment ? 'Uploading...' : 'Upload PDF'),
                      ),
                    ]),
                  ),
                ),
                SizedBox(
                  width: 728,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)),
                    child: const Text('Select an employee, choose the contract type, pick the start date, then enter the duration in months. End Date and Status are automatically computed from those values.', style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)),
                  ),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: uploadingAttachment
                ? null
                : () {
                    recomputeContract();
                    if (!formKey.currentState!.validate()) return;
                    FocusManager.instance.primaryFocus?.unfocus();
                    Navigator.of(context, rootNavigator: true).pop({
                      'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                      'contract_type': emptyToNull(contractType.text),
                      'contract_start_date': toIsoDateInput(startDate.text),
                      'duration_months': int.tryParse(durationMonths.text.trim()),
                      'contract_end_date': toIsoDateInput(endDate.text),
                      'attachment_url': emptyToNull(attachmentUrl),
                      'status': emptyToNull(status.text),
                    });
                  },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final c in [contractType, startDate, durationMonths, endDate, status]) {
    c.dispose();
  }
  return result;
}

Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final types = await contractTypeOptions();
  final data = await showContractDialog(context, employees, types, row == null ? null : normalizeRow(row));
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}
'''

marker = 'class SelectedLicenseInput'
marker_index = text.find(marker)
if marker_index == -1:
    raise SystemExit('Could not find class SelectedLicenseInput marker in lib/main.dart.')

updated_start = text.rfind('const _contractTypeOptions', 0, marker_index)
legacy_start = text.rfind('Future<void> editContract', 0, marker_index)
start = updated_start if updated_start != -1 else legacy_start
if start == -1:
    raise SystemExit('Could not find editContract block in lib/main.dart.')

text = text[:start] + replacement + '\n\n' + text[marker_index:]

if text != original:
    MAIN_DART.write_text(text, encoding='utf-8')
    print('Applied contract modal update to lib/main.dart.')
else:
    print('No changes needed.')
