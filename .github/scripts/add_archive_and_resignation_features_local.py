from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# 1) Navigation: add Archived module after Resigned Employees.
# -----------------------------------------------------------------------------
text = text.replace(
    """      const ReportsPage(),
      const ResignedEmployeesPage(),
    ];""",
    """      const ReportsPage(),
      const ResignedEmployeesPage(),
      const ArchivedPage(),
    ];""",
    1,
)
text = text.replace(
    """      NavItem('Reports', Icons.summarize_rounded),
      NavItem('Resigned Employees', Icons.person_off_rounded),
    ];""",
    """      NavItem('Reports', Icons.summarize_rounded),
      NavItem('Resigned Employees', Icons.person_off_rounded),
      NavItem('Archived', Icons.archive_rounded),
    ];""",
    1,
)

# -----------------------------------------------------------------------------
# 2) Date resigned support.
# -----------------------------------------------------------------------------
text = text.replace(
    "id, name_key, employee_code, full_name, bio_number, gender, education_level, date_hired, starting_date, employment_status, designation, employee_type, civil_status, teaching_status, current_salary, license_summary, birth_date, address, contact_number, email, guardian_name, guardian_relationship, guardian_contact, guardian_address, school_graduated, degree_course, notes",
    "id, name_key, employee_code, full_name, bio_number, gender, education_level, date_hired, starting_date, date_resigned, employment_status, designation, employee_type, civil_status, teaching_status, current_salary, license_summary, birth_date, address, contact_number, email, guardian_name, guardian_relationship, guardian_contact, guardian_address, school_graduated, degree_course, notes",
    1,
)
text = text.replace(
    "    'employment_status': 'Employment Information',\n    'date_hired': 'Employment Information',",
    "    'employment_status': 'Employment Information',\n    'date_hired': 'Employment Information',\n    'date_resigned': 'Employment Information',",
    1,
)
text = text.replace(
    "                'Date Hired': 'date_hired_display',\n                'Employee Status': 'employment_status',",
    "                'Date Hired': 'date_hired_display',\n                'Date Resigned': 'date_resigned_display',\n                'Employee Status': 'employment_status',",
    1,
)
text = text.replace(
    "  'date_hired',\n  'starting_date',",
    "  'date_hired',\n  'starting_date',\n  'date_resigned',",
    1,
)
text = text.replace(
    "      EditField('employment_status', 'Employee Status'",
    "      EditField('date_resigned', 'Date Resigned',\n          kind: FieldKind.date),\n      EditField('employment_status', 'Employee Status'",
    1,
)
text = text.replace(
    "  out['date_hired_display'] = out['date_hired'] ?? out['starting_date'];\n  if (out.containsKey('contract_end_date'))",
    "  out['date_hired_display'] = out['date_hired'] ?? out['starting_date'];\n  out['date_resigned_display'] = out['date_resigned'];\n  if (out.containsKey('contract_end_date'))",
    1,
)
text = text.replace(
    """    await db
        .from('employees')
        .update({'employment_status': 'resigned'}).eq('id', id);""",
    """    await db.from('employees').update({
      'employment_status': 'resigned',
      'date_resigned': DateFormat('yyyy-MM-dd').format(DateTime.now()),
    }).eq('id', id);""",
    1,
)

# Resigned Employees columns/actions.
text = text.replace(
    """          showActions: false,
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('employee_type', 'Type'),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onView: viewEmployee,
          onEdit: editEmployee,""",
    """          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('employee_type', 'Type'),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('date_resigned_display', 'Date Resigned'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onView: viewEmployee,
          onEdit: editEmployee,""",
    1,
)

# -----------------------------------------------------------------------------
# 3) Part-time Add Employee: remove required validation when employee type is Part Time.
# -----------------------------------------------------------------------------
text = text.replace(
    """  bool uploadingContract = false;
  final selectedLicenses = <String, SelectedLicenseInput>{};""",
    """  bool uploadingContract = false;
  bool get isPartTimeEmployee => employeeType == 'part_time';
  final selectedLicenses = <String, SelectedLicenseInput>{};""",
    1,
)
text = text.replace(
    """  Widget dropdownBox(String label, String? value,
      List<DropdownMenuItem<String>> items, ValueChanged<String?> onChanged) {""",
    """  Widget dropdownBox(String label, String? value,
      List<DropdownMenuItem<String>> items, ValueChanged<String?> onChanged,
      {bool required = true}) {""",
    1,
)
text = text.replace(
    "validator: (v) => v == null || v.isEmpty ? 'Required' : null,",
    "validator: (v) => required && (v == null || v.isEmpty) ? 'Required' : null,",
    1,
)
for old, new in {
    "textBox('Full Name', fullName),": "textBox('Full Name', fullName, required: !isPartTimeEmployee),",
    "textBox('Bio Number', bioNumber),": "textBox('Bio Number', bioNumber, required: !isPartTimeEmployee),",
    "textBox('Birth Date', birthDate, date: true),": "textBox('Birth Date', birthDate, date: true, required: !isPartTimeEmployee),",
    "textBox('Address', address, lines: 2),": "textBox('Address', address, lines: 2, required: !isPartTimeEmployee),",
    "textBox('Contact Number', contactNumber),": "textBox('Contact Number', contactNumber, required: !isPartTimeEmployee),",
    "textBox('Educational Attainment', educationLevel),": "textBox('Educational Attainment', educationLevel, required: !isPartTimeEmployee),",
    "textBox('School Graduated', schoolGraduated),": "textBox('School Graduated', schoolGraduated, required: !isPartTimeEmployee),",
    "textBox('Degree / Course', degreeCourse),": "textBox('Degree / Course', degreeCourse, required: !isPartTimeEmployee),",
    "textBox('Guardian Name', guardianName),": "textBox('Guardian Name', guardianName, required: !isPartTimeEmployee),",
    "textBox('Guardian Relationship', guardianRelationship),": "textBox('Guardian Relationship', guardianRelationship, required: !isPartTimeEmployee),",
    "textBox('Guardian Contact', guardianContact),": "textBox('Guardian Contact', guardianContact, required: !isPartTimeEmployee),",
    "textBox('Guardian Address', guardianAddress, lines: 2),": "textBox('Guardian Address', guardianAddress, lines: 2, required: !isPartTimeEmployee),",
    "textBox('Designation', designation),": "textBox('Designation', designation, required: !isPartTimeEmployee),",
    "textBox('Date Hired', dateHired, date: true),": "textBox('Date Hired', dateHired, date: true, required: !isPartTimeEmployee),",
}.items():
    text = text.replace(old, new, 1)

# Add required: !isPartTimeEmployee to selected dropdowns in Add Employee.
text = text.replace(
    """                           (v) => setDialogState(() => gender = v)),""",
    """                           (v) => setDialogState(() => gender = v),
                           required: !isPartTimeEmployee),""",
    1,
)
text = text.replace(
    """                           (v) => setDialogState(() => civilStatus = v)),""",
    """                           (v) => setDialogState(() => civilStatus = v),
                           required: !isPartTimeEmployee),""",
    1,
)
# Employee Type remains required.
text = text.replace(
    """                           (v) => setDialogState(() => teachingStatus = v)),""",
    """                           (v) => setDialogState(() => teachingStatus = v),
                           required: !isPartTimeEmployee),""",
    1,
)
text = text.replace(
    """                           (v) => setDialogState(() => employmentStatus = v)),""",
    """                           (v) => setDialogState(() => employmentStatus = v),
                           required: !isPartTimeEmployee),""",
    1,
)
text = text.replace(
    """                           (v) => setDialogState(() => contractType = v)),""",
    """                           (v) => setDialogState(() => contractType = v),
                           required: !isPartTimeEmployee),""",
    1,
)
text = text.replace("validator: requiredDate,", "validator: (v) => isPartTimeEmployee ? null : requiredDate(v),", 1)
text = text.replace(
    """                          validator: (v) {
                            if (v == null || v.trim().isEmpty)
                              return 'Required';
                            final months = int.tryParse(v.trim());
                            if (months == null || months <= 0)
                              return 'Enter valid months';
                            return null;
                          },""",
    """                          validator: (v) {
                            if (v == null || v.trim().isEmpty) {
                              return isPartTimeEmployee ? null : 'Required';
                            }
                            final months = int.tryParse(v.trim());
                            if (months == null || months <= 0)
                              return 'Enter valid months';
                            return null;
                          },""",
    1,
)
text = text.replace(
    """textBox('Contract End Date', contractEnd,
                          date: true, required: true),""",
    """textBox('Contract End Date', contractEnd,
                          date: true, required: !isPartTimeEmployee),""",
    1,
)
text = text.replace("validator: requiredText,", "validator: (v) => isPartTimeEmployee ? null : requiredText(v),", 1)

# -----------------------------------------------------------------------------
# 4) Archive helpers and Archive page.
# -----------------------------------------------------------------------------
helpers_marker = "Future<void> showActionAlert(BuildContext context, String title, String message,"
archive_helpers = r'''
String archiveModuleFromTitle(String? title, String fallback) {
  final raw = (title == null || title.trim().isEmpty) ? fallback : title;
  return raw.replaceAll(' Report', '').trim();
}

String archiveEmployeeNameFromRow(Map<String, dynamic> row) {
  if (row['employee_name'] != null) return formatValue(row['employee_name']);
  if (row['full_name'] != null) return formatValue(row['full_name']);
  if (row['employees'] is Map) return formatValue((row['employees'] as Map)['full_name']);
  return '-';
}

Object? archiveEmployeeIdFromRow(Map<String, dynamic> row) =>
    row['employee_id'] ?? row['id'];

Future<void> archiveRecordSnapshot({
  required String tableName,
  required String moduleName,
  required String archiveType,
  required Map<String, dynamic> row,
}) async {
  final normalized = normalizeRow(Map<String, dynamic>.from(row));
  await db.from('archived_records').insert({
    'module_name': moduleName,
    'table_name': tableName,
    'original_id': '${normalized['id'] ?? ''}',
    'employee_id': archiveEmployeeIdFromRow(normalized)?.toString(),
    'employee_name': archiveEmployeeNameFromRow(normalized),
    'archive_type': archiveType,
    'record_data': normalized,
    'archived_at': DateTime.now().toIso8601String(),
    'is_restored': false,
  });
}

Future<void> archiveDeletedRecord({
  required String? tableName,
  required String moduleName,
  required Map<String, dynamic> row,
}) async {
  if (tableName == null || tableName.trim().isEmpty) return;
  await archiveRecordSnapshot(
    tableName: tableName,
    moduleName: moduleName,
    archiveType: 'deleted',
    row: row,
  );
}

Future<void> archiveOldContractBeforeUpdate(String table, Object? id) async {
  if (table != 'employee_contracts' || id == null) return;
  try {
    final rows = await db
        .from('employee_contracts')
        .select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name)')
        .eq('id', id)
        .limit(1);
    if (rows is List && rows.isNotEmpty) {
      await archiveRecordSnapshot(
        tableName: 'employee_contracts',
        moduleName: 'Contracts',
        archiveType: 'old_contract',
        row: normalizeRow(Map<String, dynamic>.from(rows.first as Map)),
      );
    }
  } catch (_) {}
}

Future<List<dynamic>> loadArchivedRecords({required bool oldContracts}) async {
  final rows = await db
      .from('archived_records')
      .select()
      .eq('archive_type', oldContracts ? 'old_contract' : 'deleted')
      .order('archived_at', ascending: false)
      .limit(5000);
  return rows.map((item) {
    final row = Map<String, dynamic>.from(item as Map);
    row['archived_at_display'] = row['archived_at'];
    row['restore_status'] = row['is_restored'] == true ? 'Restored' : 'Archived';
    return row;
  }).toList();
}

Map<String, dynamic> archiveRestoreData(Map<String, dynamic> data) {
  final out = Map<String, dynamic>.from(data);
  out.remove('id');
  out.remove('employees');
  out.remove('ranking_cycles');
  out.remove('employee_name');
  out.remove('cycle_name');
  out.remove('date_hired_display');
  out.remove('date_resigned_display');
  out.remove('days_left');
  out.remove('license_ids');
  out.remove('license_records');
  out.remove('certificate_ids');
  out.remove('certificate_records');
  out.removeWhere((key, value) => value == null || value.toString() == '-');
  return out;
}

Future<void> restoreArchivedRecord(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  if (row['is_restored'] == true) {
    showSnack(context, 'This archive was already restored.');
    return;
  }
  final table = '${row['table_name'] ?? ''}'.trim();
  final dataRaw = row['record_data'];
  if (table.isEmpty || dataRaw is! Map) {
    showSnack(context, 'Archive data is incomplete.');
    return;
  }
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Restore Archived Record?'),
      content: Text(
          'This will restore ${formatValue(row['employee_name'])} back to ${formatValue(row['module_name'])} as a new active record.'),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel')),
        FilledButton.icon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.restore_rounded),
          label: const Text('Restore'),
        ),
      ],
    ),
  );
  if (ok != true) return;
  try {
    final data = Map<String, dynamic>.from(dataRaw);
    if (table == 'employee_licenses' && data['license_records'] is List) {
      final records = (data['license_records'] as List)
          .whereType<Map>()
          .map((r) => archiveRestoreData(Map<String, dynamic>.from(r)))
          .toList();
      if (records.isNotEmpty) await db.from(table).insert(records);
    } else if (table == 'employee_certificates' &&
        data['certificate_records'] is List) {
      final records = (data['certificate_records'] as List)
          .whereType<Map>()
          .map((r) => archiveRestoreData(Map<String, dynamic>.from(r)))
          .toList();
      if (records.isNotEmpty) await db.from(table).insert(records);
    } else {
      await db.from(table).insert(archiveRestoreData(data));
    }
    await db.from('archived_records').update({
      'is_restored': true,
      'restored_at': DateTime.now().toIso8601String(),
    }).eq('id', row['id']);
    refresh();
    if (context.mounted) showSnack(context, 'Archived record restored.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Restore failed: $e');
  }
}

Widget? restoreArchivedRecordAction(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) {
  if (row['is_restored'] == true) return null;
  return IconButton(
    tooltip: 'Restore',
    onPressed: () => restoreArchivedRecord(context, row, refresh),
    icon: const Icon(Icons.restore_rounded, color: Color(0xFF16A34A), size: 19),
  );
}

Future<void> viewArchivedRecord(
    BuildContext context, Map<String, dynamic> row) async {
  final data = row['record_data'] is Map
      ? Map<String, dynamic>.from(row['record_data'] as Map)
      : <String, dynamic>{};
  final cleanEntries = data.entries
      .where((entry) =>
          entry.value != null &&
          entry.value.toString().trim().isNotEmpty &&
          entry.key != 'employees' &&
          entry.key != 'ranking_cycles')
      .toList();
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(
          '${formatValue(row['module_name'])} - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 850,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Archive Information', row, const {
              'Module': 'module_name',
              'Table': 'table_name',
              'Type': 'archive_type',
              'Archived At': 'archived_at_display',
              'Status': 'restore_status',
            }),
            const SizedBox(height: 8),
            const Text('Stored Record Data',
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
            const SizedBox(height: 8),
            Wrap(spacing: 10, runSpacing: 10, children: [
              for (final entry in cleanEntries)
                DetailTile(titleCase(entry.key), formatDetailValue(entry.value, entry.key)),
            ]),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

'''
if archive_helpers not in text:
    text = text.replace(helpers_marker, archive_helpers + helpers_marker, 1)

# Add archive metadata fields to CrudTable.
text = text.replace(
    "  final String? reportTitle;\n  final List<int> pageSizeOptions;",
    "  final String? reportTitle;\n  final String? archiveTableName;\n  final String? archiveModuleName;\n  final List<int> pageSizeOptions;",
    1,
)
text = text.replace(
    "      this.reportTitle,\n      this.pageSizeOptions = const [10],",
    "      this.reportTitle,\n      this.archiveTableName,\n      this.archiveModuleName,\n      this.pageSizeOptions = const [10],",
    1,
)
text = text.replace(
    """      await widget.onDelete(row);
      refresh();""",
    """      await archiveDeletedRecord(
        tableName: widget.archiveTableName,
        moduleName: widget.archiveModuleName ??
            archiveModuleFromTitle(widget.reportTitle, widget.addLabel),
        row: row,
      );
      await widget.onDelete(row);
      refresh();""",
    1,
)

# Archive old contract snapshots before update.
text = text.replace(
    """    } else {
      await db.from(table).update(data).eq('id', id);
      showSnack(context, 'Record Updated.');""",
    """    } else {
      await archiveOldContractBeforeUpdate(table, id);
      await db.from(table).update(data).eq('id', id);
      showSnack(context, 'Record Updated.');""",
    1,
)

# Add archive metadata to CrudTable instances that delete records.
patches = {
    """              reportTitle: _employeeReportTitle(),
              columns: const [""": """              reportTitle: _employeeReportTitle(),
              archiveTableName: 'employees',
              archiveModuleName: 'Employees',
              columns: const [""",
    """              reportTitle: _reportTitle(),
              columns: const [""": """              reportTitle: _reportTitle(),
              archiveTableName: 'employee_contracts',
              archiveModuleName: 'Contracts',
              columns: const [""",
    """        addLabel: 'Add License',
        columns: const [""": """        addLabel: 'Add License',
        archiveTableName: 'employee_licenses',
        archiveModuleName: 'Credentials - Licenses',
        columns: const [""",
    """        addLabel: 'Add Certificate',
        columns: const [""": """        addLabel: 'Add Certificate',
        archiveTableName: 'employee_certificates',
        archiveModuleName: 'Credentials - Certificates',
        columns: const [""",
    """        reportTitle: '$title Report',
        columns: const [""": """        reportTitle: '$title Report',
        archiveTableName: 'evaluation_records',
        archiveModuleName: 'Evaluations',
        columns: const [""",
    """          reportTitle: 'Appointment Reference Report',
          columns: const [""": """          reportTitle: 'Appointment Reference Report',
          archiveTableName: 'employee_appointments',
          archiveModuleName: 'Appointment',
          columns: const [""",
    """              reportTitle: _rankingReportTitle(),
              columns: const [""": """              reportTitle: _rankingReportTitle(),
              archiveTableName: 'ranking_applications',
              archiveModuleName: 'Ranking',
              columns: const [""",
}
for old, new in patches.items():
    text = text.replace(old, new, 1)

# ArchivedPage class before ReportsPage.
archived_page = r'''
class ArchivedPage extends StatelessWidget {
  const ArchivedPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Archived',
        subtitle:
            'Preserved deleted records and old contract snapshots. Deleted rows can be viewed and restored.',
        child: const DefaultTabController(
          length: 2,
          child: Column(children: [
            Align(
              alignment: Alignment.centerLeft,
              child: SizedBox(
                width: 430,
                child: TabBar(tabs: [
                  Tab(text: 'Deleted Rows'),
                  Tab(text: 'Old Contracts'),
                ]),
              ),
            ),
            SizedBox(height: 16),
            Expanded(
              child: TabBarView(children: [
                ArchivedRecordsTab(oldContracts: false),
                ArchivedRecordsTab(oldContracts: true),
              ]),
            ),
          ]),
        ),
      );
}

class ArchivedRecordsTab extends StatelessWidget {
  final bool oldContracts;
  const ArchivedRecordsTab({super.key, required this.oldContracts});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => loadArchivedRecords(oldContracts: oldContracts),
        searchHint: oldContracts
            ? 'Search old contract, employee, type, date, or status'
            : 'Search archived row, module, employee, table, or date',
        addLabel: oldContracts ? 'Old Contract' : 'Archived Row',
        allowAdd: false,
        reportTitle: oldContracts
            ? 'Archived Old Contracts Report'
            : 'Archived Deleted Rows Report',
        columns: const [
          GridCol('module_name', 'Module', flex: 2),
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('table_name', 'Table', flex: 2),
          GridCol('archived_at_display', 'Archived At', flex: 2),
          GridCol('restore_status', 'Status', isStatus: true),
        ],
        onView: viewArchivedRecord,
        extraAction: oldContracts ? null : restoreArchivedRecordAction,
        showDelete: false,
        onDelete: (row) async {},
      );
}

'''
if 'class ArchivedPage extends StatelessWidget' not in text:
    text = text.replace('class ReportsPage extends StatefulWidget {', archived_page + 'class ReportsPage extends StatefulWidget {', 1)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Archive/resignation features may already be present.')
else:
    print('Applied archive module, date resigned, resigned view/edit, old contract preservation, and part-time validation changes.')
