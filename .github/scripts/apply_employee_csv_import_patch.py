from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

text = text.replace(".select('id, full_name, bio_number, gender, education_level, date_hired, starting_date, employment_status, designation, employee_type, civil_status, teaching_status, current_salary, license_summary, birth_date, address, contact_number, email, guardian_name, guardian_relationship, guardian_contact, guardian_address, school_graduated, degree_course, notes')", ".select('id, name_key, employee_code, full_name, bio_number, gender, education_level, date_hired, starting_date, employment_status, designation, employee_type, civil_status, teaching_status, current_salary, license_summary, birth_date, address, contact_number, email, guardian_name, guardian_relationship, guardian_contact, guardian_address, school_graduated, degree_course, notes')")

old_page = """class EmployeesPage extends StatelessWidget {
  const EmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Add full employee information, contract, credentials, and view complete records.',
        child: CrudTable(
          load: () => loadEmployees(),
          searchHint: 'Search employee, bio number, gender, education, status, or date hired',
          addLabel: 'Add Employee',
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('education_level', 'Educational Attainment', flex: 2),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onAdd: (ctx, refresh) => addEmployeeFull(ctx, refresh),
          onView: viewEmployee,
          onEdit: editEmployee,
          onDelete: (row) => db.from('employees').delete().eq('id', row['id']),
        ),
      );
}
"""
new_page = """class EmployeesPage extends StatefulWidget {
  const EmployeesPage({super.key});

  @override
  State<EmployeesPage> createState() => _EmployeesPageState();
}

class _EmployeesPageState extends State<EmployeesPage> {
  int refreshToken = 0;

  void refreshEmployees() => setState(() => refreshToken++);

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Add full employee information, contract, credentials, and view complete records.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                Expanded(
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [
                    Text('Excel Employee Matching', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                    SizedBox(height: 4),
                    Text('Import tbl_employee CSV to fill missing employee profile fields. Existing non-empty values are not overwritten.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600)),
                  ]),
                ),
                FilledButton.icon(
                  onPressed: () async {
                    await importEmployeeCsvInfo(context);
                    if (mounted) refreshEmployees();
                  },
                  icon: const Icon(Icons.upload_file_rounded),
                  label: const Text('Import Employee Info'),
                ),
              ]),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey('employees-$refreshToken'),
              load: () => loadEmployees(),
              searchHint: 'Search employee, bio number, gender, education, status, or date hired',
              addLabel: 'Add Employee',
              columns: const [
                GridCol('full_name', 'Employee Name', flex: 3, primary: true),
                GridCol('bio_number', 'Bio Number'),
                GridCol('gender', 'Gender'),
                GridCol('education_level', 'Educational Attainment', flex: 2),
                GridCol('date_hired_display', 'Date Hired'),
                GridCol('employment_status', 'Status', isStatus: true),
              ],
              onAdd: (ctx, refresh) => addEmployeeFull(ctx, refresh),
              onView: viewEmployee,
              onEdit: editEmployee,
              onDelete: (row) => db.from('employees').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}
"""
if old_page not in text:
    if 'Import Employee Info' in text:
        print('Employee CSV import patch is already applied.')
        raise SystemExit(0)
    raise SystemExit('EmployeesPage block not found.')
text = text.replace(old_page, new_page, 1)

insert_before = "class GridCol {"
helper = r'''
String employeeImportClean(String? value) {
  final v = (value ?? '').replaceAll('\u0000', '').trim();
  if (v.isEmpty) return '';
  final lower = v.toLowerCase();
  if (lower == 'null' || lower == 'none' || lower == 'n/a') return '';
  return v;
}

bool employeeImportIsBlank(Object? value) {
  final v = employeeImportClean('$value');
  return v.isEmpty || v == '0';
}

String employeeImportNormalizeName(String value) {
  var v = value.toUpperCase().replaceAll('Ñ', 'N');
  for (final token in const ['ATTY', 'MR', 'MS', 'MRS', 'JR', 'SR', 'III', 'IV', 'LPT', 'MAED', 'MBM', 'MBA', 'PHD', 'RSW', 'RCRIM', 'RGC', 'CPA', 'RL', 'CHRA', 'MIT', 'MST', 'MSCRIM', 'MSSW', 'MMREM', 'REA', 'REB', 'RPM', 'PRM', 'DBM', 'CEPL', 'MAPS', 'MAT', 'PE', 'MSHRM', 'CTP', 'CHP', 'MSPSY', 'MSPY']) {
    v = v.replaceAll(RegExp('\\b$token\\b'), ' ');
  }
  return v.replaceAll(RegExp(r'[^A-Z0-9]+'), ' ').trim().replaceAll(RegExp(r'\s+'), ' ');
}

List<List<String>> parseEmployeeImportCsv(String input) {
  final rows = <List<String>>[];
  var row = <String>[];
  final cell = StringBuffer();
  var quoted = false;
  for (var i = 0; i < input.length; i++) {
    final ch = input[i];
    if (quoted) {
      if (ch == '"') {
        if (i + 1 < input.length && input[i + 1] == '"') {
          cell.write('"');
          i++;
        } else {
          quoted = false;
        }
      } else {
        cell.write(ch);
      }
    } else {
      if (ch == '"') {
        quoted = true;
      } else if (ch == ',') {
        row.add(cell.toString());
        cell.clear();
      } else if (ch == '\n') {
        row.add(cell.toString().replaceAll('\r', ''));
        cell.clear();
        rows.add(row);
        row = <String>[];
      } else {
        cell.write(ch);
      }
    }
  }
  if (cell.isNotEmpty || row.isNotEmpty) {
    row.add(cell.toString().replaceAll('\r', ''));
    rows.add(row);
  }
  return rows;
}

String employeeImportFullName(Map<String, String> r) {
  final last = employeeImportClean(r['emp_last_name']).toUpperCase();
  final first = employeeImportClean(r['emp_first_name']).toUpperCase();
  final middle = employeeImportClean(r['emp_middle_name']).toUpperCase();
  return [if (last.isNotEmpty) '$last,', if (first.isNotEmpty) first, if (middle.isNotEmpty) middle].join(' ').replaceAll(RegExp(r'\s+'), ' ').trim();
}

String? employeeImportDate(String value) {
  final v = employeeImportClean(value);
  if (v.isEmpty || v == '0000-00-00') return null;
  final match = RegExp(r'^(\d{4})-(\d{1,2})-(\d{1,2})').firstMatch(v);
  if (match == null) return null;
  final y = int.tryParse(match.group(1)!);
  final m = int.tryParse(match.group(2)!);
  final d = int.tryParse(match.group(3)!);
  if (y == null || m == null || d == null || y < 1900) return null;
  return '${y.toString().padLeft(4, '0')}-${m.toString().padLeft(2, '0')}-${d.toString().padLeft(2, '0')}';
}

String employeeImportStatus(String value) {
  final v = employeeImportClean(value).toLowerCase();
  if (v.contains('inactive') || v.contains('resigned') || v.contains('separated')) return 'inactive';
  return 'active';
}

String employeeImportType(String value) {
  final v = employeeImportClean(value).toLowerCase();
  if (v.contains('part')) return 'part_time';
  if (v.contains('staff')) return 'staff';
  if (v.contains('probation')) return 'probationary';
  return 'full_time';
}

void putIfMissing(Map<String, dynamic> target, Map<String, dynamic> existing, String key, Object? value) {
  final v = value == null ? '' : employeeImportClean('$value');
  if (v.isEmpty) return;
  if (employeeImportIsBlank(existing[key])) target[key] = v;
}

Future<String> pickEmployeeCsvText() async {
  final input = html.FileUploadInputElement()..accept = '.csv,text/csv';
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return '';
  final reader = html.FileReader();
  reader.readAsText(file);
  await reader.onLoad.first;
  return '${reader.result ?? ''}';
}

Future<void> importEmployeeCsvInfo(BuildContext context) async {
  try {
    final csvText = await pickEmployeeCsvText();
    if (csvText.trim().isEmpty) return;
    final rows = parseEmployeeImportCsv(csvText);
    if (rows.length < 2) {
      if (context.mounted) showSnack(context, 'No CSV rows found.');
      return;
    }
    final headers = rows.first.map((h) => h.trim()).toList();
    final existingRows = (await loadEmployees(limit: 5000)).map((e) => normalizeRow(Map<String, dynamic>.from(e as Map))).toList();
    final byKey = <String, List<Map<String, dynamic>>>{};
    for (final e in existingRows) {
      final keys = <String>{
        employeeImportNormalizeName('${e['name_key'] ?? ''}'),
        employeeImportNormalizeName('${e['full_name'] ?? ''}'),
      }..removeWhere((k) => k.isEmpty);
      final notes = '${e['notes'] ?? ''}';
      if (notes.toLowerCase().contains('aliases:')) {
        for (final alias in notes.split('|')) {
          final k = employeeImportNormalizeName(alias.replaceAll('Aliases:', ''));
          if (k.isNotEmpty) keys.add(k);
        }
      }
      for (final k in keys) {
        byKey.putIfAbsent(k, () => <Map<String, dynamic>>[]).add(e);
      }
    }

    final updates = <Map<String, dynamic>>[];
    final inserts = <Map<String, dynamic>>[];
    final ambiguous = <String>[];
    var invalid = 0;
    var noChanges = 0;

    for (var i = 1; i < rows.length; i++) {
      final row = rows[i];
      final r = <String, String>{};
      for (var c = 0; c < headers.length && c < row.length; c++) {
        r[headers[c]] = row[c];
      }
      final first = employeeImportClean(r['emp_first_name']);
      final last = employeeImportClean(r['emp_last_name']);
      if (first.isEmpty || last.isEmpty || first.toUpperCase() == 'NONE' || last.toUpperCase() == 'NONE') {
        invalid++;
        continue;
      }
      final fullName = employeeImportFullName(r);
      final key = employeeImportNormalizeName('$last $first ${r['emp_middle_name'] ?? ''}');
      final data = <String, dynamic>{
        'name_key': key,
        'full_name': fullName,
        'gender': employeeImportClean(r['emp_gender']),
        'birth_date': employeeImportDate(r['birthdate']),
        'civil_status': employeeImportClean(r['civil_status']),
        'address': employeeImportClean(r['emp_address']),
        'email': employeeImportClean(r['email']),
        'contact_number': employeeImportClean(r['contact_no']),
        'school_graduated': employeeImportClean(r['school_graduated']),
        'degree_course': employeeImportClean(r['degree_attained']),
        'date_hired': employeeImportDate(r['employment_date']),
        'starting_date': employeeImportDate(r['employment_date']),
        'guardian_name': employeeImportClean(r['emp_g_name']),
        'guardian_address': employeeImportClean(r['emp_g_address']),
        'guardian_contact': employeeImportClean(r['emp_g_contact']),
        'designation': employeeImportClean(r['emp_designation']),
        'employment_status': employeeImportStatus(r['is_active'] ?? ''),
        'employee_type': employeeImportType(r['emp_status'] ?? ''),
        'source_workbook': 'tbl_employee.csv',
        'source_sheet': 'CSV Import',
        'source_row': i + 1,
        'updated_at': DateTime.now().toIso8601String(),
      }..removeWhere((_, value) => value == null || employeeImportClean('$value').isEmpty);

      final matches = byKey[key] ?? const <Map<String, dynamic>>[];
      if (matches.length > 1) {
        ambiguous.add(fullName);
        continue;
      }
      if (matches.length == 1) {
        final e = matches.first;
        final update = <String, dynamic>{'id': e['id'], 'label': fullName};
        for (final field in ['gender','birth_date','civil_status','address','email','contact_number','school_graduated','degree_course','date_hired','starting_date','guardian_name','guardian_address','guardian_contact','designation']) {
          putIfMissing(update, e, field, data[field]);
        }
        if (update.length > 2) updates.add(update); else noChanges++;
      } else {
        data['employment_status'] ??= 'active';
        data['employee_type'] ??= 'full_time';
        data['is_faculty'] = true;
        inserts.add(data);
      }
    }

    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Import Employee Info?'),
        content: SizedBox(
          width: 520,
          child: Text('Matched updates: ${updates.length}\nNew employees to insert: ${inserts.length}\nNo changes needed: $noChanges\nSkipped invalid: $invalid\nSkipped ambiguous: ${ambiguous.length}\n\nOnly blank/missing fields will be filled. Existing non-empty values will not be overwritten. Government IDs and photos are not imported.'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Apply Import')),
        ],
      ),
    );
    if (ok != true) return;

    for (final u in updates) {
      final id = u.remove('id');
      u.remove('label');
      await db.from('employees').update(u).eq('id', id);
    }
    for (final row in inserts) {
      await db.from('employees').insert(row);
    }
    if (context.mounted) showSnack(context, 'Employee import completed. Updated ${updates.length}, inserted ${inserts.length}, skipped ${ambiguous.length + invalid}.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Employee import failed: $e');
  }
}

'''
if 'Future<void> importEmployeeCsvInfo' not in text:
    text = text.replace(insert_before, helper + insert_before, 1)

path.write_text(text, encoding='utf-8')
print('Employee CSV import patch applied to lib/main.dart')
