from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# Helpers for safe block replacement.
# -----------------------------------------------------------------------------
def find_matching_brace(src: str, open_brace: int) -> int:
    depth = 0
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    escape = False
    for i in range(open_brace, len(src)):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ''
        if in_line_comment:
            if ch == '\n':
                in_line_comment = False
            continue
        if in_block_comment:
            if ch == '*' and nxt == '/':
                in_block_comment = False
                continue
            continue
        if in_single:
            if ch == '\\' and not escape:
                escape = True
                continue
            if ch == "'" and not escape:
                in_single = False
            escape = False
            continue
        if in_double:
            if ch == '\\' and not escape:
                escape = True
                continue
            if ch == '"' and not escape:
                in_double = False
            escape = False
            continue
        if ch == '/' and nxt == '/':
            in_line_comment = True
            continue
        if ch == '/' and nxt == '*':
            in_block_comment = True
            continue
        if ch == "'":
            in_single = True
            continue
        if ch == '"':
            in_double = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1

def replace_class_block(src: str, class_name: str, new_block: str) -> str:
    start = src.find(f'class {class_name}')
    if start < 0:
        return src
    brace = src.find('{', start)
    end = find_matching_brace(src, brace)
    if brace < 0 or end < 0:
        return src
    line_end = src.find('\n', end)
    if line_end < 0:
        line_end = end
    return src[:start] + new_block + src[line_end + 1:]

def replace_onpressed_after(src: str, anchor: str, function_name: str) -> str:
    anchor_i = src.find(anchor)
    if anchor_i < 0:
        return src
    marker = 'onPressed: () {'
    start = src.find(marker, anchor_i)
    if start < 0:
        return src
    brace = src.find('{', start)
    end = find_matching_brace(src, brace)
    if brace < 0 or end < 0:
        return src
    # Include the trailing comma after the function body when present.
    comma_end = end + 1
    while comma_end < len(src) and src[comma_end].isspace():
        comma_end += 1
    if comma_end < len(src) and src[comma_end] == ',':
        comma_end += 1
    replacement = f'onPressed: {function_name},'
    return src[:start] + replacement + src[comma_end:]

# -----------------------------------------------------------------------------
# 1) Add 1/10/100 display filter to every CrudTable by default.
# -----------------------------------------------------------------------------
text = text.replace(
    'this.pageSizeOptions = const [10],',
    'this.pageSizeOptions = const [1, 10, 100],',
)
text = text.replace(
    'widget.pageSizeOptions.isEmpty ? const [10] : widget.pageSizeOptions;',
    'widget.pageSizeOptions.isEmpty ? const [1, 10, 100] : widget.pageSizeOptions;',
)

# -----------------------------------------------------------------------------
# 2) Date input: simple MM/DD/YYYY typing with automatic slash.
# -----------------------------------------------------------------------------
if "import 'package:flutter/services.dart';" not in text:
    text = text.replace(
        "import 'package:flutter/material.dart';\n",
        "import 'package:flutter/material.dart';\nimport 'package:flutter/services.dart';\n",
        1,
    )

if 'class DateSlashInputFormatter extends TextInputFormatter' not in text:
    formatter = r'''
class DateSlashInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    var digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (digits.length > 8) digits = digits.substring(0, 8);
    final buffer = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i == 2 || i == 4) buffer.write('/');
      buffer.write(digits[i]);
    }
    final out = buffer.toString();
    return TextEditingValue(
      text: out,
      selection: TextSelection.collapsed(offset: out.length),
    );
  }
}

'''
    text = text.replace(
        'void safeRefresh(VoidCallback refresh) {\n  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());\n}\n',
        'void safeRefresh(VoidCallback refresh) {\n  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());\n}\n\n' + formatter,
        1,
    )

# Date picker still exists, but selected values now use the faster typed format.
text = text.replace(
    "controller.text = DateFormat('MMMM dd, yyyy').format(picked);",
    "controller.text = DateFormat('MM/dd/yyyy').format(picked);",
)
text = text.replace(
    "controller.text = DateFormat('MMMM dd, yyyy').format(picked);",
    "controller.text = DateFormat('MM/dd/yyyy').format(picked);",
)
text = text.replace(
    "endDate.text = DateFormat('MMMM dd, yyyy').format(computedEnd);",
    "endDate.text = DateFormat('MM/dd/yyyy').format(computedEnd);",
)
text = text.replace(
    "contractEnd.text = DateFormat('MMMM dd, yyyy').format(end);",
    "contractEnd.text = DateFormat('MM/dd/yyyy').format(end);",
)

# Make generic showRecordDialog date fields typeable and allow Enter to save.
text = text.replace(
    '''  StateSetter setDialogState,
) {''',
    '''  StateSetter setDialogState,
  {VoidCallback? onDateSubmit}
) {''',
    1,
)
text = text.replace(
    '''        readOnly: isDate,
        onTap: isDate
            ? () => pickDateIntoController(context, controllers[f.key]!)
            : null,
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer
            ? TextInputType.number
            : TextInputType.text,''',
    '''        readOnly: false,
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: isDate
            ? TextInputType.datetime
            : (f.kind == FieldKind.number || f.kind == FieldKind.integer
                ? TextInputType.number
                : TextInputType.text),
        inputFormatters: isDate ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: isDate ? (_) => onDateSubmit?.call() : null,''',
    1,
)
text = text.replace(
    "hintText: isDate ? 'Select date' : null,",
    "hintText: isDate ? 'MM/DD/YYYY' : null,",
    1,
)

submit_record = r'''  void submitDialog() {
    if (!formKey.currentState!.validate()) return;
    final out = <String, dynamic>{};
    for (final f in fields) {
      out[f.key] = f.kind == FieldKind.dropdown
          ? emptyToNull(selected[f.key])
          : parseFieldValue(controllers[f.key]!.text, f.kind);
    }
    Navigator.pop(context, out);
  }

'''
if 'void submitDialog() {' not in text:
    text = text.replace(
        '  final result = await showDialog<Map<String, dynamic>>(\n',
        submit_record + '  final result = await showDialog<Map<String, dynamic>>(\n',
        1,
    )
text = text.replace(
    '''                ...buildDialogFieldWidgets(
                    context, fields, controllers, selected, setDialogState),''',
    '''                ...buildDialogFieldWidgets(
                  context,
                  fields,
                  controllers,
                  selected,
                  setDialogState,
                  onDateSubmit: submitDialog,
                ),''',
    1,
)
text = replace_onpressed_after(text, 'Future<Map<String, dynamic>?> showRecordDialog', 'submitDialog')

# Add Employee full dialog: make its date fields typeable and allow Enter to save.
submit_add = r'''  void submitAddEmployeeDialog() {
    recomputeContract();
    if (!formKey.currentState!.validate()) return;
    final employee = <String, dynamic>{
      'full_name': fullName.text.trim(),
      'bio_number': bioNumber.text.trim(),
      'gender': gender,
      'civil_status': civilStatus,
      'birth_date': toIsoDateInput(birthDate.text),
      'address': address.text.trim(),
      'contact_number': contactNumber.text.trim(),
      'email': emptyToNull(email.text.trim()),
      'education_level': educationLevel.text.trim(),
      'school_graduated': schoolGraduated.text.trim(),
      'degree_course': degreeCourse.text.trim(),
      'guardian_name': guardianName.text.trim(),
      'guardian_relationship': guardianRelationship.text.trim(),
      'guardian_contact': guardianContact.text.trim(),
      'guardian_address': guardianAddress.text.trim(),
      'designation': designation.text.trim(),
      'employee_type': employeeType,
      'teaching_status': teachingStatus,
      'employment_status': employmentStatus,
      'date_hired': toIsoDateInput(dateHired.text),
      'starting_date': toIsoDateInput(dateHired.text),
    }..removeWhere((_, value) =>
        value == null || value.toString().trim().isEmpty);
    employee['name_key'] = normalizeName(employee['full_name']?.toString() ?? '');
    final contract = <String, dynamic>{
      'contract_type': contractType,
      'contract_start_date': toIsoDateInput(contractStart.text),
      'duration_months': int.tryParse(durationMonths.text.trim()),
      'contract_end_date': toIsoDateInput(contractEnd.text),
      'attachment_url': emptyToNull(contractAttachmentUrl),
      'status': emptyToNull(contractStatus.text),
    }..removeWhere((_, value) =>
        value == null || value.toString().trim().isEmpty);
    final licenses = selectedLicenses.values
        .map((entry) => <String, dynamic>{
              'license_name': entry.name,
              'license_number': entry.number.text.trim(),
              'expiry_date': toIsoDateInput(entry.expiry.text),
              'attachment_url': emptyToNull(entry.attachmentUrl),
              'status': entry.status.isEmpty
                  ? licenseStatusFromExpiry(entry.expiry.text)
                  : entry.status,
            }..removeWhere((_, value) =>
                value == null || value.toString().trim().isEmpty))
        .toList();
    final certificates = selectedCertificates.values
        .map((entry) => <String, dynamic>{
              'certificate_type': 'National Certificate',
              'certificate_name': entry.name,
              'certificate_number': entry.number.text.trim(),
              'expiry_date': toIsoDateInput(entry.expiry.text),
              'attachment_url': emptyToNull(entry.attachmentUrl),
              'status': entry.status.isEmpty
                  ? certificateStatusFromExpiry(entry.expiry.text)
                  : entry.status,
            }..removeWhere((_, value) =>
                value == null || value.toString().trim().isEmpty))
        .toList();
    Navigator.pop(
        context,
        AddEmployeeFullResult(
          employee: employee,
          contract: contract,
          licenses: licenses,
          certificates: certificates,
        ));
  }

'''
if 'void submitAddEmployeeDialog() {' not in text and 'Future<AddEmployeeFullResult?> showAddEmployeeFullDialog' in text:
    insert_at = text.find('  Widget textBox(String label, TextEditingController controller,')
    if insert_at > 0:
        text = text[:insert_at] + submit_add + text[insert_at:]
text = text.replace(
    '''        readOnly: date,
        keyboardType: keyboardType,
        onTap: date ? () => pickDateIntoController(context, controller) : null,''',
    '''        readOnly: false,
        keyboardType: date ? TextInputType.datetime : keyboardType,
        inputFormatters: date ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: date ? (_) => submitAddEmployeeDialog() : null,''',
    1,
)
text = text.replace("hintText: date ? 'Select date' : null,", "hintText: date ? 'MM/DD/YYYY' : null,", 1)
# Contract start date field inside Add Employee.
text = text.replace(
    '''                          controller: contractStart,
                          readOnly: true,
                          onTap: () => pickDateIntoController(
                              context, contractStart,
                              afterPick: () =>
                                  setDialogState(recomputeContract)),
                          decoration: InputDecoration(
                            labelText: 'Contract Start Date',
                            hintText: 'Select date',''',
    '''                          controller: contractStart,
                          readOnly: false,
                          keyboardType: TextInputType.datetime,
                          inputFormatters: [DateSlashInputFormatter()],
                          onFieldSubmitted: (_) => submitAddEmployeeDialog(),
                          decoration: InputDecoration(
                            labelText: 'Contract Start Date',
                            hintText: 'MM/DD/YYYY',''',
    1,
)
text = replace_onpressed_after(text, 'Future<AddEmployeeFullResult?> showAddEmployeeFullDialog', 'submitAddEmployeeDialog')

# Make contract dialog date picker box typeable too.
text = text.replace(
    '''        readOnly: true,
        decoration: const InputDecoration(
          labelText: 'Start Date',
          hintText: 'Select start date',''',
    '''        readOnly: false,
        keyboardType: TextInputType.datetime,
        inputFormatters: [DateSlashInputFormatter()],
        decoration: const InputDecoration(
          labelText: 'Start Date',
          hintText: 'MM/DD/YYYY',''',
    1,
)
# If the old onTap handler still exists in contractDatePickerBox, remove it.
text = text.replace(
    '''        onTap: () async {
          final current = parseFlexibleDate(controller.text) ?? DateTime.now();
          final picked = await showDatePicker(
            context: context,
            initialDate: current,
            firstDate: DateTime(1950),
            lastDate: DateTime(2100),
          );
          if (picked == null) return;
          setDialogState(() {
            controller.text = DateFormat('MM/dd/yyyy').format(picked);
            recomputeContract();
          });
        },''',
    '''        onFieldSubmitted: (_) => setDialogState(recomputeContract),''',
    1,
)

# -----------------------------------------------------------------------------
# 3) Open all PDF attachments through a button/dialog action rather than showing
#    a link only.
# -----------------------------------------------------------------------------
if 'void openPdfAttachment' not in text:
    pdf_helper = r'''
void openPdfAttachment(BuildContext context, Object? rawUrl) {
  final url = formatValue(rawUrl).trim();
  if (url.isEmpty || url == '-' || !url.toLowerCase().startsWith('http')) {
    showSnack(context, 'No PDF attachment available.');
    return;
  }
  final win = html.window.open(url, '_blank');
  if (win == null) {
    showSnack(context, 'Please allow pop-ups to open the PDF.');
  }
}

'''
    text = text.replace('class DialogSectionTitle extends StatelessWidget {', pdf_helper + 'class DialogSectionTitle extends StatelessWidget {', 1)

new_attachment_class = r'''class AttachmentPdfTile extends StatelessWidget {
  final String label;
  final Object? url;
  const AttachmentPdfTile(this.label, this.url, {super.key});

  @override
  Widget build(BuildContext context) {
    final value = formatValue(url).trim();
    final hasPdf = value.isNotEmpty && value != '-' && value.toLowerCase().startsWith('http');
    return SizedBox(
      width: 354,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: _surfaceSoft,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _line),
        ),
        child: Row(children: [
          const Icon(Icons.picture_as_pdf_rounded, color: _danger, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              hasPdf ? label : 'No PDF attached',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontWeight: FontWeight.w800, color: _ink),
            ),
          ),
          const SizedBox(width: 8),
          TextButton.icon(
            onPressed: hasPdf ? () => openPdfAttachment(context, value) : null,
            icon: const Icon(Icons.open_in_new_rounded, size: 17),
            label: const Text('Open'),
          ),
        ]),
      ),
    );
  }
}

'''
if 'class AttachmentPdfTile extends StatelessWidget' in text:
    text = replace_class_block(text, 'AttachmentPdfTile', new_attachment_class)

# Replace raw URL detail tiles for attachment_url in generic related sections when present.
text = text.replace(
    "DetailTile(titleCase(k), formatDetailValue(row[k], k))",
    "k == 'attachment_url'\n                    ? AttachmentPdfTile('Attachment PDF', row[k])\n                    : DetailTile(titleCase(k), formatDetailValue(row[k], k))",
)
text = text.replace(
    "DetailTile(titleCase(entry.key), formatDetailValue(entry.value, entry.key))",
    "entry.key == 'attachment_url'\n                    ? AttachmentPdfTile('Attachment PDF', entry.value)\n                    : DetailTile(titleCase(entry.key), formatDetailValue(entry.value, entry.key))",
)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Table page, PDF, and date input improvements may already be present.')
else:
    print('Applied 1/10/100 table display filter, openable PDF attachments, and faster MM/DD/YYYY date input with Enter-to-save behavior.')
