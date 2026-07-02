from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()
start = s.index('String contractStatusFromEndDate(')
end = s.index('class SelectedLicenseInput {', start)
new = r'''String contractStatusFromEndDate(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final end = DateTime(parsed.year, parsed.month, parsed.day);
  if (end.isBefore(today)) return 'Expired';
  if (end.difference(today).inDays <= 90) return 'For Renewal';
  return 'On-going';
}

int? parseContractMonths(String text) {
  final cleaned = text.replaceAll(RegExp(r'[^0-9-]'), '').trim();
  if (cleaned.isEmpty) return null;
  final months = int.tryParse(cleaned);
  if (months == null || months <= 0) return null;
  return months;
}

DateTime? contractEndDateFromStartAndMonths(Object? startValue, Object? monthsValue) {
  final start = parseFlexibleDate(startValue);
  final months = parseContractMonths('${monthsValue ?? ''}');
  if (start == null || months == null) return null;
  final monthIndex = (start.month - 1) + months;
  final year = start.year + (monthIndex ~/ 12);
  final month = (monthIndex % 12) + 1;
  final lastDay = DateTime(year, month + 1, 0).day;
  final day = start.day > lastDay ? lastDay : start.day;
  return DateTime(year, month, day);
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

Future<void> pickAndUploadContractPdf(BuildContext context, TextEditingController attachmentUrl, StateSetter setDialogState, void Function(String) setFileName, void Function(bool) setUploading) async {
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

Widget contractDatePickerBox(BuildContext context, String label, TextEditingController controller, void Function(String) onPicked, {bool required = false, bool enabled = true}) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: true,
        enabled: enabled,
        decoration: InputDecoration(labelText: label, hintText: 'January 02, 2026', suffixIcon: const Icon(Icons.calendar_month_rounded)),
        validator: (v) {
          final value = (v ?? '').trim();
          if (required && value.isEmpty) return 'Required';
          if (value.isNotEmpty && parseFlexibleDate(value) == null) return 'Use date picker or January 02, 2026';
          return null;
        },
        onTap: !enabled
            ? null
            : () async {
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

Widget contractTextBox(String label, TextEditingController controller, {TextInputType keyboardType = TextInputType.text, String? Function(String?)? validator, void Function(String)? onChanged, bool readOnly = false}) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        readOnly: readOnly,
        decoration: InputDecoration(labelText: label),
        validator: validator,
        onChanged: onChanged,
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
  final statusController = TextEditingController();
  final attachmentUrl = TextEditingController(text: formatEditValue(initial?['attachment_url']));
  String attachmentFileName = attachmentUrl.text.trim().isEmpty ? '' : 'Existing contract PDF attached';
  bool uploadingAttachment = false;

  void computeEndAndStatus(StateSetter? setDialogState) {
    final computedEnd = contractEndDateFromStartAndMonths(startDate.text, durationMonths.text);
    if (computedEnd != null) {
      endDate.text = DateFormat('MMMM dd, yyyy').format(computedEnd);
    } else if (startDate.text.trim().isEmpty || durationMonths.text.trim().isEmpty) {
      endDate.clear();
    }
    final computedStatus = contractStatusFromEndDate(endDate.text);
    statusController.text = computedStatus.isEmpty ? 'Auto-filled after date input' : computedStatus;
    if (setDialogState != null) setDialogState(() {});
  }

  if (endDate.text.trim().isEmpty) {
    final computedEnd = contractEndDateFromStartAndMonths(startDate.text, durationMonths.text);
    if (computedEnd != null) endDate.text = DateFormat('MMMM dd, yyyy').format(computedEnd);
  }
  final initialStatus = contractStatusFromEndDate(endDate.text);
  statusController.text = initialStatus.isEmpty ? 'Auto-filled after date input' : initialStatus;

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
                const DialogSectionTitle('Contract Information'),
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
                contractDatePickerBox(context, 'Start Date', startDate, (_) => computeEndAndStatus(setDialogState), required: true),
                contractTextBox(
                  'Duration In Months',
                  durationMonths,
                  keyboardType: TextInputType.number,
                  validator: (v) => parseContractMonths(v ?? '') == null ? 'Required' : null,
                  onChanged: (_) => computeEndAndStatus(setDialogState),
                ),
                contractTextBox('End Date', endDate, readOnly: true, validator: (v) => (v == null || v.trim().isEmpty) ? 'Auto-fill requires start date and months' : null),
                contractTextBox('Status', statusController, readOnly: true),
                SizedBox(
                  width: 728,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
                    child: Row(children: [
                      OutlinedButton.icon(
                        onPressed: uploadingAttachment ? null : () => pickAndUploadContractPdf(context, attachmentUrl, setDialogState, (name) => attachmentFileName = name, (v) => uploadingAttachment = v),
                        icon: uploadingAttachment ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.picture_as_pdf_rounded),
                        label: Text(uploadingAttachment ? 'Uploading...' : 'Attach Contract'),
                      ),
                      const SizedBox(width: 12),
                      Expanded(child: Text(attachmentFileName.isEmpty ? 'No contract PDF attached' : attachmentFileName, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 13, color: attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700))),
                    ]),
                  ),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              computeEndAndStatus(setDialogState);
              if (!formKey.currentState!.validate()) return;
              final finalStatus = contractStatusFromEndDate(endDate.text);
              final out = <String, dynamic>{
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'contract_type': emptyToNull(contractType.text),
                'contract_start_date': toIsoDateInput(startDate.text),
                'duration_months': parseContractMonths(durationMonths.text),
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
  for (final c in [contractType, startDate, durationMonths, endDate, statusController, attachmentUrl]) {
    c.dispose();
  }
  return result;
}

'''
s = s[:start] + new + s[end:]
p.write_text(s)
