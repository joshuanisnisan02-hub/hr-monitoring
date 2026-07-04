from pathlib import Path

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

# 1) Use the requested standard contract types in every contract picker.
text = replace_between(text, 'const _contractTypeOptions = <EditOption>[', 'class UploadedAttachment {', r'''const _contractTypeOptions = <EditOption>[
  EditOption('Full-time', 'Full-time'),
  EditOption('Full-time-Probationary', 'Full-time-Probationary'),
  EditOption('Part-time', 'Part-time'),
  EditOption('Probationary', 'Probationary'),
  EditOption('Compliance', 'Compliance'),
];

''')

# 2) Add a reusable date picker and Mark as Resigned status action widget.
insert_marker = 'String dialogSectionForField(String key) {'
if 'Future<void> pickDateIntoController(' not in text:
    helper = r'''
Future<void> pickDateIntoController(
    BuildContext context, TextEditingController controller,
    {VoidCallback? afterPick}) async {
  final initial = parseFlexibleDate(controller.text) ?? DateTime.now();
  final picked = await showDatePicker(
    context: context,
    initialDate: initial,
    firstDate: DateTime(1900),
    lastDate: DateTime(DateTime.now().year + 30),
  );
  if (picked == null) return;
  controller.text = DateFormat('MMMM dd, yyyy').format(picked);
  afterPick?.call();
}

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
                  : () async {
                      await onMarkResigned();
                      if (context.mounted) Navigator.of(context).pop();
                    },
              icon: const Icon(Icons.person_off_rounded),
              label: const Text('Mark as Resigned'),
            ),
          ]),
        ),
      );
}

'''
    if insert_marker not in text:
        raise SystemExit('Could not find dialogSectionForField marker.')
    text = text.replace(insert_marker, helper + insert_marker, 1)

# 3) Make generic date fields use a date picker instead of plain typing.
old_field_block = r'''    widgets.add(SizedBox(
      width: width,
      child: TextFormField(
        controller: controllers[f.key],
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer
            ? TextInputType.number
            : TextInputType.text,
        decoration: InputDecoration(
            labelText: f.label,
            hintText: f.kind == FieldKind.date ? 'January 02, 2026' : null),
        validator: (v) =>
            f.required && (v == null || v.trim().isEmpty) ? 'Required' : null,
      ),
    ));
'''
new_field_block = r'''    final isDate = f.kind == FieldKind.date;
    widgets.add(SizedBox(
      width: width,
      child: TextFormField(
        controller: controllers[f.key],
        readOnly: isDate,
        onTap: isDate
            ? () => pickDateIntoController(context, controllers[f.key]!)
            : null,
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer
            ? TextInputType.number
            : TextInputType.text,
        decoration: InputDecoration(
          labelText: f.label,
          hintText: isDate ? 'Select date' : null,
          suffixIcon: isDate
              ? IconButton(
                  tooltip: 'Pick date',
                  icon: const Icon(Icons.calendar_month_rounded),
                  onPressed: () =>
                      pickDateIntoController(context, controllers[f.key]!),
                )
              : null,
        ),
        validator: (v) {
          if (f.required && (v == null || v.trim().isEmpty)) return 'Required';
          if (isDate && v != null && v.trim().isNotEmpty &&
              parseFlexibleDate(v.trim()) == null) {
            return 'Select a valid date';
          }
          return null;
        },
      ),
    ));
'''
if old_field_block in text:
    text = text.replace(old_field_block, new_field_block, 1)

# 4) Update edit employee dropdowns and remove current salary/license summary/notes from the edit modal too.
text = replace_between(text, 'List<EditField> employeeEditFields() => const [', 'List<EditField> addEmployeeFields() => const [', r'''List<EditField> employeeEditFields() => const [
      EditField('full_name', 'Full Name', required: true),
      EditField('bio_number', 'Bio Number', required: true),
      EditField('gender', 'Gender', kind: FieldKind.dropdown, required: true, options: [
        EditOption('Male', 'Male'),
        EditOption('Female', 'Female')
      ]),
      EditField('civil_status', 'Civil Status', kind: FieldKind.dropdown, required: true, options: [
        EditOption('Single', 'Single'),
        EditOption('Married', 'Married'),
        EditOption('Widowed', 'Widowed'),
        EditOption('Separated', 'Separated')
      ]),
      EditField('birth_date', 'Birth Date', kind: FieldKind.date, required: true),
      EditField('address', 'Address', kind: FieldKind.multiline, lines: 2, required: true),
      EditField('contact_number', 'Contact Number', required: true),
      EditField('email', 'Email'),
      EditField('education_level', 'Educational Attainment', required: true),
      EditField('school_graduated', 'School Graduated', required: true),
      EditField('degree_course', 'Degree / Course', required: true),
      EditField('guardian_name', 'Guardian Name', required: true),
      EditField('guardian_relationship', 'Guardian Relationship', required: true),
      EditField('guardian_contact', 'Guardian Contact', required: true),
      EditField('guardian_address', 'Guardian Address',
          kind: FieldKind.multiline, lines: 2, required: true),
      EditField('designation', 'Designation', required: true),
      EditField('employee_type', 'Employee Type',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('full_time', 'Full Time'),
            EditOption('probationary', 'Probationary'),
            EditOption('part_time', 'Part Time'),
            EditOption('staff', 'Staff'),
            EditOption('faculty_staff', 'Faculty / Staff')
          ]),
      EditField('teaching_status', 'Teaching Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Teaching', 'Teaching'),
            EditOption('Non-Teaching', 'Non-Teaching')
          ]),
      EditField('employment_status', 'Employee Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('active', 'Active'),
            EditOption('inactive', 'Inactive'),
            EditOption('separated', 'Separated'),
            EditOption('resigned', 'Resigned')
          ]),
      EditField('date_hired', 'Date Hired', kind: FieldKind.date, required: true),
    ];

''')

# 5) Keep addEmployeeFields from exposing removed credential/current salary fields if any fallback still calls it.
text = replace_between(text, 'List<EditField> addEmployeeFields() => const [', 'const employeeKeys = [', r'''List<EditField> addEmployeeFields() => const [
      EditField('full_name', 'Full Name', required: true),
      EditField('bio_number', 'Bio Number', required: true),
      EditField('gender', 'Gender', kind: FieldKind.dropdown, required: true, options: [
        EditOption('Male', 'Male'),
        EditOption('Female', 'Female')
      ]),
      EditField('civil_status', 'Civil Status', kind: FieldKind.dropdown, required: true, options: [
        EditOption('Single', 'Single'),
        EditOption('Married', 'Married'),
        EditOption('Widowed', 'Widowed'),
        EditOption('Separated', 'Separated')
      ]),
      EditField('birth_date', 'Birth Date', kind: FieldKind.date, required: true),
      EditField('address', 'Address', kind: FieldKind.multiline, lines: 2, required: true),
      EditField('contact_number', 'Contact Number', required: true),
      EditField('email', 'Email'),
      EditField('education_level', 'Educational Attainment', required: true),
      EditField('school_graduated', 'School Graduated', required: true),
      EditField('degree_course', 'Degree / Course', required: true),
      EditField('guardian_name', 'Guardian Name', required: true),
      EditField('guardian_relationship', 'Guardian Relationship', required: true),
      EditField('guardian_contact', 'Guardian Contact', required: true),
      EditField('guardian_address', 'Guardian Address',
          kind: FieldKind.multiline, lines: 2, required: true),
      EditField('designation', 'Designation', required: true),
      EditField('employee_type', 'Employee Type',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('full_time', 'Full Time'),
            EditOption('probationary', 'Probationary'),
            EditOption('part_time', 'Part Time'),
            EditOption('staff', 'Staff'),
            EditOption('faculty_staff', 'Faculty / Staff')
          ]),
      EditField('teaching_status', 'Teaching Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Teaching', 'Teaching'),
            EditOption('Non-Teaching', 'Non-Teaching')
          ]),
      EditField('employment_status', 'Employee Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('active', 'Active'),
            EditOption('inactive', 'Inactive'),
            EditOption('separated', 'Separated'),
            EditOption('resigned', 'Resigned')
          ]),
      EditField('date_hired', 'Date Hired', kind: FieldKind.date, required: true),
    ];

''')

# 6) Add the custom Add Employee full modal and replace addEmployeeFull.
add_employee_replacement = r'''class AddEmployeeFullResult {
  final Map<String, dynamic> employee;
  final Map<String, dynamic> contract;
  final List<Map<String, dynamic>> licenses;
  final List<Map<String, dynamic>> certificates;
  const AddEmployeeFullResult(
      {required this.employee,
      required this.contract,
      required this.licenses,
      required this.certificates});
}

Future<AddEmployeeFullResult?> showAddEmployeeFullDialog(
    BuildContext context,
    List<EditOption> contractTypes,
    List<String> licenseNames,
    List<String> certificateNames) async {
  final formKey = GlobalKey<FormState>();
  final fullName = TextEditingController();
  final bioNumber = TextEditingController();
  final birthDate = TextEditingController();
  final address = TextEditingController();
  final contactNumber = TextEditingController();
  final email = TextEditingController();
  final educationLevel = TextEditingController();
  final schoolGraduated = TextEditingController();
  final degreeCourse = TextEditingController();
  final guardianName = TextEditingController();
  final guardianRelationship = TextEditingController();
  final guardianContact = TextEditingController();
  final guardianAddress = TextEditingController();
  final designation = TextEditingController();
  final dateHired = TextEditingController();
  final contractStart = TextEditingController();
  final durationMonths = TextEditingController();
  final contractEnd = TextEditingController();
  final contractStatus = TextEditingController();

  String? gender = 'Male';
  String? civilStatus = 'Single';
  String? employeeType = 'full_time';
  String? teachingStatus = 'Teaching';
  String? employmentStatus = 'active';
  String? contractType = contractTypes.isNotEmpty ? contractTypes.first.value : 'Full-time';
  String contractAttachmentUrl = '';
  String contractAttachmentFileName = '';
  bool uploadingContract = false;
  final selectedLicenses = <String, SelectedLicenseInput>{};
  final selectedCertificates = <String, SelectedCertificateInput>{};

  void recomputeContract() {
    final start = parseFlexibleDate(contractStart.text);
    final months = int.tryParse(durationMonths.text.trim());
    if (start == null || months == null || months <= 0) return;
    final end = addContractMonths(start, months);
    contractEnd.text = DateFormat('MMMM dd, yyyy').format(end);
    contractStatus.text = contractStatusFromEndDate(end);
  }

  String? requiredText(String? value) =>
      value == null || value.trim().isEmpty ? 'Required' : null;
  String? requiredDate(String? value) {
    if (value == null || value.trim().isEmpty) return 'Required';
    return parseFlexibleDate(value.trim()) == null ? 'Select a valid date' : null;
  }

  Widget textBox(String label, TextEditingController controller,
      {bool required = true, int lines = 1, bool date = false, TextInputType? keyboardType}) {
    return SizedBox(
      width: lines > 1 ? 728 : 354,
      child: TextFormField(
        controller: controller,
        maxLines: lines,
        readOnly: date,
        keyboardType: keyboardType,
        onTap: date ? () => pickDateIntoController(context, controller) : null,
        decoration: InputDecoration(
          labelText: label,
          hintText: date ? 'Select date' : null,
          suffixIcon: date
              ? IconButton(
                  tooltip: 'Pick date',
                  icon: const Icon(Icons.calendar_month_rounded),
                  onPressed: () => pickDateIntoController(context, controller),
                )
              : null,
        ),
        validator: (value) => required
            ? (date ? requiredDate(value) : requiredText(value))
            : (date && value != null && value.trim().isNotEmpty && parseFlexibleDate(value.trim()) == null
                ? 'Select a valid date'
                : null),
      ),
    );
  }

  Widget dropdownBox(String label, String? value, List<DropdownMenuItem<String>> items,
      ValueChanged<String?> onChanged) {
    return SizedBox(
      width: 354,
      child: DropdownButtonFormField<String>(
        value: value,
        isExpanded: true,
        decoration: InputDecoration(labelText: label),
        items: items,
        validator: (v) => v == null || v.isEmpty ? 'Required' : null,
        onChanged: onChanged,
      ),
    );
  }

  final result = await showDialog<AddEmployeeFullResult>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add Employee'),
        content: SizedBox(
          width: 1060,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  textBox('Full Name', fullName),
                  textBox('Bio Number', bioNumber),
                  dropdownBox('Gender', gender, const [
                    DropdownMenuItem(value: 'Male', child: Text('Male')),
                    DropdownMenuItem(value: 'Female', child: Text('Female')),
                  ], (v) => setDialogState(() => gender = v)),
                  dropdownBox('Civil Status', civilStatus, const [
                    DropdownMenuItem(value: 'Single', child: Text('Single')),
                    DropdownMenuItem(value: 'Married', child: Text('Married')),
                    DropdownMenuItem(value: 'Widowed', child: Text('Widowed')),
                    DropdownMenuItem(value: 'Separated', child: Text('Separated')),
                  ], (v) => setDialogState(() => civilStatus = v)),
                  textBox('Birth Date', birthDate, date: true),
                  textBox('Address', address, lines: 2),
                  textBox('Contact Number', contactNumber),
                  textBox('Email', email, required: false),
                  textBox('Educational Attainment', educationLevel),
                  textBox('School Graduated', schoolGraduated),
                  textBox('Degree / Course', degreeCourse),
                  textBox('Guardian Name', guardianName),
                  textBox('Guardian Relationship', guardianRelationship),
                  textBox('Guardian Contact', guardianContact),
                  textBox('Guardian Address', guardianAddress, lines: 2),
                  textBox('Designation', designation),
                  dropdownBox('Employee Type', employeeType, const [
                    DropdownMenuItem(value: 'full_time', child: Text('Full Time')),
                    DropdownMenuItem(value: 'probationary', child: Text('Probationary')),
                    DropdownMenuItem(value: 'part_time', child: Text('Part Time')),
                    DropdownMenuItem(value: 'staff', child: Text('Staff')),
                    DropdownMenuItem(value: 'faculty_staff', child: Text('Faculty / Staff')),
                  ], (v) => setDialogState(() => employeeType = v)),
                  dropdownBox('Teaching Status', teachingStatus, const [
                    DropdownMenuItem(value: 'Teaching', child: Text('Teaching')),
                    DropdownMenuItem(value: 'Non-Teaching', child: Text('Non-Teaching')),
                  ], (v) => setDialogState(() => teachingStatus = v)),
                  dropdownBox('Employee Status', employmentStatus, const [
                    DropdownMenuItem(value: 'active', child: Text('Active')),
                    DropdownMenuItem(value: 'inactive', child: Text('Inactive')),
                    DropdownMenuItem(value: 'separated', child: Text('Separated')),
                    DropdownMenuItem(value: 'resigned', child: Text('Resigned')),
                  ], (v) => setDialogState(() => employmentStatus = v)),
                  textBox('Date Hired', dateHired, date: true),
                ]),
                const SizedBox(height: 16),
                const DialogSectionTitle('Contract Information'),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  dropdownBox('Contract Type', contractType,
                      contractTypes.map((o) => DropdownMenuItem(value: o.value, child: Text(o.label))).toList(),
                      (v) => setDialogState(() => contractType = v)),
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: contractStart,
                      readOnly: true,
                      onTap: () => pickDateIntoController(context, contractStart,
                          afterPick: () => setDialogState(recomputeContract)),
                      decoration: InputDecoration(
                        labelText: 'Contract Start Date',
                        hintText: 'Select date',
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.calendar_month_rounded),
                          onPressed: () => pickDateIntoController(context, contractStart,
                              afterPick: () => setDialogState(recomputeContract)),
                        ),
                      ),
                      validator: requiredDate,
                    ),
                  ),
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: durationMonths,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Duration in Months'),
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) return 'Required';
                        final months = int.tryParse(v.trim());
                        if (months == null || months <= 0) return 'Enter valid months';
                        return null;
                      },
                      onChanged: (_) => setDialogState(recomputeContract),
                    ),
                  ),
                  textBox('Contract End Date', contractEnd, date: true, required: true),
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: contractStatus,
                      readOnly: true,
                      decoration: const InputDecoration(labelText: 'Contract Status'),
                      validator: requiredText,
                    ),
                  ),
                  SizedBox(
                    width: 354,
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      OutlinedButton.icon(
                        onPressed: uploadingContract
                            ? null
                            : () async {
                                setDialogState(() => uploadingContract = true);
                                final uploaded = await pickAndUploadContractPdf(context);
                                setDialogState(() {
                                  if (uploaded != null) {
                                    contractAttachmentUrl = uploaded.url;
                                    contractAttachmentFileName = uploaded.fileName;
                                  }
                                  uploadingContract = false;
                                });
                              },
                        icon: uploadingContract
                            ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                            : const Icon(Icons.picture_as_pdf_rounded),
                        label: Text(uploadingContract ? 'Uploading...' : 'Attach Contract PDF'),
                      ),
                      const SizedBox(height: 6),
                      Text(contractAttachmentFileName.isEmpty ? 'No PDF attached' : contractAttachmentFileName,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(color: _muted, fontWeight: FontWeight.w700, fontSize: 12)),
                    ]),
                  ),
                ]),
                const SizedBox(height: 16),
                const DialogSectionTitle('License Information (Optional)'),
                Wrap(spacing: 10, runSpacing: 8, children: [
                  for (final license in licenseNames)
                    SizedBox(
                      width: 278,
                      child: CheckboxListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                        title: Text(license, maxLines: 2, overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
                        value: selectedLicenses.containsKey(license),
                        onChanged: (checked) => setDialogState(() {
                          if (checked == true) {
                            selectedLicenses.putIfAbsent(license, () => SelectedLicenseInput(license));
                          } else {
                            selectedLicenses.remove(license)?.dispose();
                          }
                        }),
                      ),
                    ),
                ]),
                if (selectedLicenses.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  for (final entry in selectedLicenses.values)
                    Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(border: Border.all(color: _line), borderRadius: BorderRadius.circular(14)),
                      child: Wrap(spacing: 10, runSpacing: 10, children: [
                        SizedBox(width: 260, child: Text(entry.name, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                        textBox('License Number', entry.number),
                        SizedBox(
                          width: 354,
                          child: TextFormField(
                            controller: entry.expiry,
                            readOnly: true,
                            onTap: () => pickDateIntoController(context, entry.expiry,
                                afterPick: () => setDialogState(() => entry.status = licenseStatusFromExpiry(entry.expiry.text))),
                            decoration: InputDecoration(
                              labelText: 'Expiry Date',
                              suffixIcon: IconButton(
                                icon: const Icon(Icons.calendar_month_rounded),
                                onPressed: () => pickDateIntoController(context, entry.expiry,
                                    afterPick: () => setDialogState(() => entry.status = licenseStatusFromExpiry(entry.expiry.text))),
                              ),
                            ),
                            validator: requiredDate,
                          ),
                        ),
                        SizedBox(width: 130, child: StatusChip(entry.status.isEmpty ? 'Select Expiry' : entry.status)),
                        OutlinedButton.icon(
                          onPressed: entry.uploadingAttachment ? null : () => pickAndUploadLicensePdf(context, entry, setDialogState),
                          icon: const Icon(Icons.picture_as_pdf_rounded),
                          label: Text(entry.attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF'),
                        ),
                      ]),
                    ),
                ],
                const SizedBox(height: 16),
                const DialogSectionTitle('Certificate Information (Optional)'),
                Wrap(spacing: 10, runSpacing: 8, children: [
                  for (final cert in certificateNames)
                    SizedBox(
                      width: 278,
                      child: CheckboxListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                        title: Text(cert, maxLines: 2, overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
                        value: selectedCertificates.containsKey(cert),
                        onChanged: (checked) => setDialogState(() {
                          if (checked == true) {
                            selectedCertificates.putIfAbsent(cert, () => SelectedCertificateInput(cert));
                          } else {
                            selectedCertificates.remove(cert)?.dispose();
                          }
                        }),
                      ),
                    ),
                ]),
                if (selectedCertificates.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  for (final entry in selectedCertificates.values)
                    Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(border: Border.all(color: _line), borderRadius: BorderRadius.circular(14)),
                      child: Wrap(spacing: 10, runSpacing: 10, children: [
                        SizedBox(width: 260, child: Text(entry.name, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                        textBox('Certificate Number', entry.number),
                        SizedBox(
                          width: 354,
                          child: TextFormField(
                            controller: entry.expiry,
                            readOnly: true,
                            onTap: () => pickDateIntoController(context, entry.expiry,
                                afterPick: () => setDialogState(() => entry.status = certificateStatusFromExpiry(entry.expiry.text))),
                            decoration: InputDecoration(
                              labelText: 'Expiry Date',
                              suffixIcon: IconButton(
                                icon: const Icon(Icons.calendar_month_rounded),
                                onPressed: () => pickDateIntoController(context, entry.expiry,
                                    afterPick: () => setDialogState(() => entry.status = certificateStatusFromExpiry(entry.expiry.text))),
                              ),
                            ),
                            validator: requiredDate,
                          ),
                        ),
                        SizedBox(width: 130, child: StatusChip(entry.status.isEmpty ? 'Select Expiry' : entry.status)),
                        OutlinedButton.icon(
                          onPressed: entry.uploadingAttachment ? null : () => pickAndUploadCertificatePdf(context, entry, setDialogState),
                          icon: const Icon(Icons.picture_as_pdf_rounded),
                          label: Text(entry.attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF'),
                        ),
                      ]),
                    ),
                ],
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
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
              }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty);
              employee['name_key'] = normalizeName(employee['full_name']?.toString() ?? '');
              final contract = <String, dynamic>{
                'contract_type': contractType,
                'contract_start_date': toIsoDateInput(contractStart.text),
                'duration_months': int.tryParse(durationMonths.text.trim()),
                'contract_end_date': toIsoDateInput(contractEnd.text),
                'attachment_url': emptyToNull(contractAttachmentUrl),
                'status': emptyToNull(contractStatus.text),
              }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty);
              final licenses = selectedLicenses.values.map((entry) => <String, dynamic>{
                    'license_name': entry.name,
                    'license_number': entry.number.text.trim(),
                    'expiry_date': toIsoDateInput(entry.expiry.text),
                    'attachment_url': emptyToNull(entry.attachmentUrl),
                    'status': entry.status.isEmpty ? licenseStatusFromExpiry(entry.expiry.text) : entry.status,
                  }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty)).toList();
              final certificates = selectedCertificates.values.map((entry) => <String, dynamic>{
                    'certificate_type': 'National Certificate',
                    'certificate_name': entry.name,
                    'certificate_number': entry.number.text.trim(),
                    'expiry_date': toIsoDateInput(entry.expiry.text),
                    'attachment_url': emptyToNull(entry.attachmentUrl),
                    'status': entry.status.isEmpty ? certificateStatusFromExpiry(entry.expiry.text) : entry.status,
                  }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty)).toList();
              Navigator.pop(context, AddEmployeeFullResult(
                employee: employee,
                contract: contract,
                licenses: licenses,
                certificates: certificates,
              ));
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final c in [
    fullName, bioNumber, birthDate, address, contactNumber, email, educationLevel,
    schoolGraduated, degreeCourse, guardianName, guardianRelationship,
    guardianContact, guardianAddress, designation, dateHired, contractStart,
    durationMonths, contractEnd, contractStatus
  ]) {
    c.dispose();
  }
  for (final entry in selectedLicenses.values) {
    entry.dispose();
  }
  for (final entry in selectedCertificates.values) {
    entry.dispose();
  }
  return result;
}

Future<void> addEmployeeFull(BuildContext context, VoidCallback refresh) async {
  final result = await showAddEmployeeFullDialog(
    context,
    await contractTypeOptions(),
    await licenseNameOptions(),
    await certificateNameOptions(),
  );
  if (result == null) return;

  try {
    final inserted = await db
        .from('employees')
        .insert(result.employee)
        .select('id')
        .single();
    final employeeId = inserted['id'];

    if (result.contract.isNotEmpty) {
      await db.from('employee_contracts').insert({
        ...result.contract,
        'employee_id': employeeId,
      });
    }
    if (result.licenses.isNotEmpty) {
      await db.from('employee_licenses').insert([
        for (final license in result.licenses)
          {...license, 'employee_id': employeeId}
      ]);
    }
    if (result.certificates.isNotEmpty) {
      await db.from('employee_certificates').insert([
        for (final certificate in result.certificates)
          {...certificate, 'employee_id': employeeId}
      ]);
    }

    refresh();
    showSnack(context,
        'Employee, contract, license, and certificate information saved.');
  } catch (e) {
    showSnack(context, 'Save Failed: $e');
  }
}

'''
text = replace_between(text, 'Future<void> addEmployeeFull(BuildContext context, VoidCallback refresh) async {', 'Future<void> viewEmployee(', add_employee_replacement)

# 7) Add Mark as Resigned behavior and prefix button in Edit Employee.
mark_helper_marker = 'Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,'
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
    if mark_helper_marker not in text:
        raise SystemExit('Could not find editEmployee marker.')
    text = text.replace(mark_helper_marker, mark_helper + mark_helper_marker, 1)

text = replace_between(text, 'Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,', 'const _contractTypeOptions = <EditOption>[', r'''Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,
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

''')

if text == original:
    print('No changes applied. Employee modal updates may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Applied Add Employee modal updates, date pickers, and Mark as Resigned action.')
