from pathlib import Path

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('Run from project root')
s = p.read_text(encoding='utf-8-sig')
o = s

# Add controllers/state in Add Employee dialog.
if 'employeeAppointmentCategory' not in s:
    s = s.replace(
        "  final contractStatus = TextEditingController(text: '');",
        "  final contractStatus = TextEditingController(text: '');\n"
        "  final employeeAppointmentCategory = TextEditingController();\n"
        "  final employeeAppointmentTitle = TextEditingController();\n"
        "  final employeeAppointmentOtherDuties = TextEditingController();\n"
        "  final employeeAppointmentType = TextEditingController();\n"
        "  String employeeAppointmentAttachmentUrl = '';\n"
        "  String employeeAppointmentAttachmentFileName = '';\n"
        "  bool uploadingEmployeeAppointmentAttachment = false;",
        1,
    )

# Add appointment property to AddEmployeeFullResult.
if 'final Map<String, dynamic> appointment;' not in s:
    s = s.replace(
        '  final List<Map<String, dynamic>> educationBackgrounds;\n',
        '  final List<Map<String, dynamic>> educationBackgrounds;\n  final Map<String, dynamic> appointment;\n',
        1,
    )
    s = s.replace(
        '    required this.educationBackgrounds,\n  });',
        '    required this.educationBackgrounds,\n    required this.appointment,\n  });',
        1,
    )

# Insert the Appointment section in Add Employee before Contract Information.
if "const DialogSectionTitle('Appointment Information')" not in s:
    target = "                    const SizedBox(height: 16),\n                    const DialogSectionTitle('Contract Information'),"
    block = r'''                    const SizedBox(height: 16),
                    const DialogSectionTitle('Appointment Information'),
                    Wrap(spacing: 14, runSpacing: 14, children: [
                      searchableOptionBox('Appointment Type',
                          employeeAppointmentCategory, appointmentCategoryOptions),
                      SizedBox(
                        width: 354,
                        child: TextFormField(
                          controller: employeeAppointmentTitle,
                          decoration:
                              const InputDecoration(labelText: 'Appointment'),
                        ),
                      ),
                      SizedBox(
                        width: 728,
                        child: TextFormField(
                          controller: employeeAppointmentOtherDuties,
                          minLines: 2,
                          maxLines: 4,
                          decoration:
                              const InputDecoration(labelText: 'Other Duties'),
                        ),
                      ),
                      searchableOptionBox(
                          'Type', employeeAppointmentType, appointmentTypeOptions),
                      SizedBox(
                        width: 354,
                        child: Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(color: _line)),
                          child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                OutlinedButton.icon(
                                  onPressed: uploadingEmployeeAppointmentAttachment
                                      ? null
                                      : () async {
                                          setDialogState(() =>
                                              uploadingEmployeeAppointmentAttachment = true);
                                          final uploaded =
                                              await pickAndUploadAppointmentPdf(context);
                                          if (!context.mounted) return;
                                          setDialogState(() {
                                            if (uploaded != null) {
                                              employeeAppointmentAttachmentUrl = uploaded.url;
                                              employeeAppointmentAttachmentFileName = uploaded.fileName;
                                            }
                                            uploadingEmployeeAppointmentAttachment = false;
                                          });
                                        },
                                  icon: uploadingEmployeeAppointmentAttachment
                                      ? const SizedBox(
                                          width: 16,
                                          height: 16,
                                          child: CircularProgressIndicator(strokeWidth: 2))
                                      : const Icon(Icons.picture_as_pdf_rounded),
                                  label: Text(uploadingEmployeeAppointmentAttachment
                                      ? 'Uploading...'
                                      : (employeeAppointmentAttachmentFileName.isEmpty
                                          ? 'Attach PDF'
                                          : 'Change PDF')),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  employeeAppointmentAttachmentFileName.isEmpty
                                      ? 'No PDF attached'
                                      : employeeAppointmentAttachmentFileName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                      color: employeeAppointmentAttachmentFileName.isEmpty
                                          ? _muted
                                          : _ink,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 12),
                                ),
                              ]),
                        ),
                      ),
                    ]),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Contract Information'),'''
    s = s.replace(target, block, 1)

# Create appointment payload before AddEmployeeFullResult is returned.
if 'final appointmentRecord = <String, dynamic>{' not in s:
    marker = """              final educationRecords = educationBackgrounds
                  .where((entry) => entry.hasInput)
                  .map((entry) => entry.toMap())
                  .where((record) => record.isNotEmpty)
                  .toList();"""
    payload = marker + r'''
              final appointmentRecord = <String, dynamic>{
                'category': employeeAppointmentCategory.text.trim(),
                'appointment_title': employeeAppointmentTitle.text.trim(),
                'other_duties': employeeAppointmentOtherDuties.text.trim(),
                'appointment_type': employeeAppointmentType.text.trim(),
                'attachment_url': employeeAppointmentAttachmentUrl.trim(),
              }..removeWhere((_, value) =>
                  value == null || value.toString().trim().isEmpty);'''
    s = s.replace(marker, payload, 1)

# Add required constructor argument.
s = s.replace(
    'educationBackgrounds: educationRecords,\n                  ));',
    'educationBackgrounds: educationRecords,\n                    appointment: appointmentRecord,\n                  ));',
)
s = s.replace(
    'educationBackgrounds: educationRecords,\n        ));',
    'educationBackgrounds: educationRecords,\n          appointment: appointmentRecord,\n        ));',
)

# Dispose controllers.
s = s.replace(
    '    contractStatus\n  ]) {',
    '    contractStatus,\n    employeeAppointmentCategory,\n    employeeAppointmentTitle,\n    employeeAppointmentOtherDuties,\n    employeeAppointmentType\n  ]) {',
    1,
)

# Save the Add Employee appointment record.
if 'result.appointment.isNotEmpty' not in s:
    s = s.replace(
        """    if (result.contract.isNotEmpty) {
      await db.from('employee_contracts').insert({
        ...upperCaseDataMap(result.contract),
        'employee_id': employeeId,
      });
    }""",
        """    if (result.appointment.isNotEmpty) {
      await db.from('employee_appointments').insert({
        ...upperCaseDataMap(result.appointment),
        'employee_id': employeeId,
      });
    }
    if (result.contract.isNotEmpty) {
      await db.from('employee_contracts').insert({
        ...upperCaseDataMap(result.contract),
        'employee_id': employeeId,
      });
    }""",
        1,
    )

p.write_text(s, encoding='utf-8')
if s == o:
    print('No changes applied. Add Employee appointment section may already be present.')
else:
    print('Added Appointment Information section to Add Employee and saves it to Appointment module.')
