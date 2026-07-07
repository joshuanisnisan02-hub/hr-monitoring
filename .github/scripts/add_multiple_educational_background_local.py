from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# 1) PDF upload helper for educational background attachments.
# -----------------------------------------------------------------------------
if 'Future<UploadedAttachment?> pickAndUploadEducationPdf' not in text:
    marker = 'Widget contractTypeAutocompleteBox('
    helper = r'''
Future<UploadedAttachment?> pickAndUploadEducationPdf(BuildContext context) async {
  final file = await pickPdfFileOrNull();
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
    final uploadPath =
        'education/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(uploadPath, bytes,
        fileOptions:
            const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(uploadPath);
    return UploadedAttachment(url, file.name);
  } catch (e) {
    showSnack(context, 'Education PDF upload failed: $e');
    return null;
  }
}

'''
    if marker not in text:
        raise SystemExit('Could not find insertion point for education PDF upload helper.')
    text = text.replace(marker, helper + marker, 1)

# -----------------------------------------------------------------------------
# 2) Input model and card widget for multiple educational backgrounds.
# -----------------------------------------------------------------------------
if 'class EducationBackgroundInput' not in text:
    marker = 'class AddEmployeeFullResult {'
    education_code = r'''
class EducationBackgroundInput {
  final TextEditingController educationLevel = TextEditingController();
  final TextEditingController schoolGraduated = TextEditingController();
  final TextEditingController degreeCourse = TextEditingController();
  final TextEditingController yearGraduated = TextEditingController();
  final TextEditingController status = TextEditingController();
  final TextEditingController attachment = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;

  void dispose() {
    educationLevel.dispose();
    schoolGraduated.dispose();
    degreeCourse.dispose();
    yearGraduated.dispose();
    status.dispose();
    attachment.dispose();
  }

  bool get hasInput =>
      educationLevel.text.trim().isNotEmpty ||
      schoolGraduated.text.trim().isNotEmpty ||
      degreeCourse.text.trim().isNotEmpty ||
      yearGraduated.text.trim().isNotEmpty ||
      status.text.trim().isNotEmpty ||
      attachmentUrl.trim().isNotEmpty;

  Map<String, dynamic> toMap() => <String, dynamic>{
        'education_level': educationLevel.text.trim(),
        'school_graduated': schoolGraduated.text.trim(),
        'degree_course': degreeCourse.text.trim(),
        'year_graduated': yearGraduated.text.trim(),
        'status': status.text.trim(),
        'attachment_url': attachmentUrl.trim(),
      }..removeWhere(
          (_, value) => value == null || value.toString().trim().isEmpty);
}

Widget educationBackgroundInputCard(
  BuildContext context,
  EducationBackgroundInput entry,
  StateSetter setDialogState,
  VoidCallback onRemove,
) =>
    Container(
      width: 728,
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.school_rounded, color: _primary, size: 20),
          const SizedBox(width: 8),
          const Expanded(
            child: Text('Educational Background',
                style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
          ),
          IconButton(
            tooltip: 'Remove educational background',
            onPressed: onRemove,
            icon: const Icon(Icons.close_rounded, color: _danger),
          ),
        ]),
        const SizedBox(height: 10),
        Wrap(spacing: 10, runSpacing: 10, children: [
          SizedBox(
            width: 342,
            child: TextFormField(
              controller: entry.educationLevel,
              decoration:
                  const InputDecoration(labelText: 'Educational Attainment'),
            ),
          ),
          SizedBox(
            width: 342,
            child: TextFormField(
              controller: entry.schoolGraduated,
              decoration: const InputDecoration(labelText: 'School Graduated'),
            ),
          ),
          SizedBox(
            width: 342,
            child: TextFormField(
              controller: entry.degreeCourse,
              decoration: const InputDecoration(labelText: 'Degree / Course'),
            ),
          ),
          SizedBox(
            width: 164,
            child: TextFormField(
              controller: entry.yearGraduated,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Year Graduated'),
            ),
          ),
          SizedBox(
            width: 164,
            child: TextFormField(
              controller: entry.status,
              decoration: const InputDecoration(labelText: 'Status'),
            ),
          ),
          SizedBox(
            width: 342,
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              OutlinedButton.icon(
                onPressed: entry.uploadingAttachment
                    ? null
                    : () async {
                        setDialogState(() => entry.uploadingAttachment = true);
                        final uploaded = await pickAndUploadEducationPdf(context);
                        if (!context.mounted) return;
                        setDialogState(() {
                          if (uploaded != null) {
                            entry.attachmentUrl = uploaded.url;
                            entry.attachmentFileName = uploaded.fileName;
                            entry.attachment.text = uploaded.url;
                          }
                          entry.uploadingAttachment = false;
                        });
                      },
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
              const SizedBox(height: 6),
              Text(
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
            ]),
          ),
        ]),
      ]),
    );

'''
    if marker not in text:
        raise SystemExit('Could not find AddEmployeeFullResult insertion point.')
    text = text.replace(marker, education_code + marker, 1)

# -----------------------------------------------------------------------------
# 3) Add educationBackgrounds to AddEmployeeFullResult.
# -----------------------------------------------------------------------------
text = text.replace(
    '''class AddEmployeeFullResult {
  final Map<String, dynamic> employee;
  final Map<String, dynamic> contract;
  final List<Map<String, dynamic>> licenses;
  final List<Map<String, dynamic>> certificates;
  const AddEmployeeFullResult(
      {required this.employee,
      required this.contract,
      required this.licenses,
      required this.certificates});
}''',
    '''class AddEmployeeFullResult {
  final Map<String, dynamic> employee;
  final Map<String, dynamic> contract;
  final List<Map<String, dynamic>> licenses;
  final List<Map<String, dynamic>> certificates;
  final List<Map<String, dynamic>> educationBackgrounds;
  const AddEmployeeFullResult(
      {required this.employee,
      required this.contract,
      required this.licenses,
      required this.certificates,
      required this.educationBackgrounds});
}''',
    1,
)

# -----------------------------------------------------------------------------
# 4) Add list state, UI section, payload mapping, dispose, and insert logic.
# -----------------------------------------------------------------------------
text = text.replace(
    "  final selectedCertificates = <String, SelectedCertificateInput>{};",
    "  final selectedCertificates = <String, SelectedCertificateInput>{};\n  final educationBackgrounds = <EducationBackgroundInput>[\n    EducationBackgroundInput(),\n  ];",
    1,
)

# Insert multiple education UI before Contract Information.
old = """                    const SizedBox(height: 16),
                    const DialogSectionTitle('Contract Information'),"""
new = """                    const SizedBox(height: 16),
                    const DialogSectionTitle('Educational Background Records'),
                    Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      for (final entry in educationBackgrounds)
                        educationBackgroundInputCard(
                          context,
                          entry,
                          setDialogState,
                          () => setDialogState(() {
                            if (educationBackgrounds.length > 1) {
                              educationBackgrounds.remove(entry);
                              entry.dispose();
                            } else {
                              entry.educationLevel.clear();
                              entry.schoolGraduated.clear();
                              entry.degreeCourse.clear();
                              entry.yearGraduated.clear();
                              entry.status.clear();
                              entry.attachment.clear();
                              entry.attachmentUrl = '';
                              entry.attachmentFileName = '';
                            }
                          }),
                        ),
                      OutlinedButton.icon(
                        onPressed: () => setDialogState(
                            () => educationBackgrounds.add(EducationBackgroundInput())),
                        icon: const Icon(Icons.add_rounded),
                        label: const Text('Add Educational Background'),
                      ),
                    ]),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Contract Information'),"""
if old in text and 'Educational Background Records' not in text:
    text = text.replace(old, new, 1)

# Add mapping after certificates list. Apply to all copies if submit helper + inline exist.
needle = """              final certificates = selectedCertificates.values
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
                  .toList();"""
insert = needle + """
              final educationRecords = educationBackgrounds
                  .where((entry) => entry.hasInput)
                  .map((entry) => entry.toMap())
                  .where((record) => record.isNotEmpty)
                  .toList();"""
text = text.replace(needle, insert)

# Add the property in AddEmployeeFullResult creation.
text = text.replace(
    """                    certificates: certificates,
                  ));""",
    """                    certificates: certificates,
                    educationBackgrounds: educationRecords,
                  ));""",
)

# Dispose education inputs.
text = text.replace(
    """  for (final entry in selectedCertificates.values) {
    entry.dispose();
  }
  return result;""",
    """  for (final entry in selectedCertificates.values) {
    entry.dispose();
  }
  for (final entry in educationBackgrounds) {
    entry.dispose();
  }
  return result;""",
    1,
)

# Insert education records after employee insert.
text = text.replace(
    """    if (result.licenses.isNotEmpty) {
      await db.from('employee_licenses').insert([
        for (final license in result.licenses)
          {...license, 'employee_id': employeeId}
      ]);
    }""",
    """    if (result.educationBackgrounds.isNotEmpty) {
      await db.from('employee_educational_backgrounds').insert([
        for (final education in result.educationBackgrounds)
          {...education, 'employee_id': employeeId}
      ]);
    }
    if (result.licenses.isNotEmpty) {
      await db.from('employee_licenses').insert([
        for (final license in result.licenses)
          {...license, 'employee_id': employeeId}
      ]);
    }""",
    1,
)

# -----------------------------------------------------------------------------
# 5) Show multiple education records in employee view.
# -----------------------------------------------------------------------------
text = text.replace(
    """    final licenses = await db
        .from('employee_licenses')""",
    """    final educationBackgrounds = await db
        .from('employee_educational_backgrounds')
        .select()
        .eq('employee_id', row['id'])
        .order('year_graduated', ascending: false);
    final licenses = await db
        .from('employee_licenses')""",
    1,
)
text = text.replace(
    """              detailSection('Educational Background', row, const {
                'Educational Attainment': 'education_level',
                'School Graduated': 'school_graduated',
                'Degree / Course': 'degree_course',
              }),""",
    """              detailSection('Educational Background', row, const {
                'Educational Attainment': 'education_level',
                'School Graduated': 'school_graduated',
                'Degree / Course': 'degree_course',
              }),
              relatedSection('Educational Background Records',
                  educationBackgrounds, const [
                'education_level',
                'school_graduated',
                'degree_course',
                'year_graduated',
                'status',
                'attachment_url'
              ]),""",
    1,
)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Multiple educational background may already be present.')
else:
    print('Applied multiple educational background records with PDF attachment, year graduated, and status.')
