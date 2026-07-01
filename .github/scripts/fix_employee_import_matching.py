from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

if 'List<Map<String, dynamic>> employeeImportFindMatches' not in text:
    marker = "bool employeeImportIsBlank(Object? value) {\n  final v = employeeImportClean('$value');\n  return v.isEmpty || v == '0';\n}\n\n"
    helper = r'''String employeeImportAny(Map<String, String> row, List<String> keys) {
  String normHeader(String value) => value.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
  final normalized = <String, String>{};
  for (final entry in row.entries) {
    normalized[normHeader(entry.key)] = entry.value;
  }
  for (final key in keys) {
    final direct = employeeImportClean(row[key]);
    if (direct.isNotEmpty) return direct;
    final loose = employeeImportClean(normalized[normHeader(key)]);
    if (loose.isNotEmpty) return loose;
  }
  return '';
}

String employeeImportPrimaryNameKey(String value) {
  final cleaned = value.replaceAll('.', ' ').replaceAll(',', ',').trim();
  if (cleaned.contains(',')) {
    final parts = cleaned.split(',');
    final last = parts.first.trim();
    final rest = parts.skip(1).join(' ').trim();
    final first = rest.split(RegExp(r'\s+')).where((p) => p.trim().isNotEmpty).cast<String>().toList();
    if (last.isNotEmpty && first.isNotEmpty) return employeeImportNormalizeName('$last ${first.first}');
  }
  final tokens = employeeImportNormalizeName(cleaned).split(RegExp(r'\s+')).where((p) => p.isNotEmpty).toList();
  if (tokens.length >= 2) return '${tokens.first} ${tokens[1]}';
  return employeeImportNormalizeName(cleaned);
}

Set<String> employeeImportCsvMatchKeys(Map<String, String> row) {
  final first = employeeImportAny(row, const ['emp_first_name', 'first_name', 'firstname', 'given_name', 'givenname']);
  final middle = employeeImportAny(row, const ['emp_middle_name', 'middle_name', 'middlename', 'middle_initial']);
  final last = employeeImportAny(row, const ['emp_last_name', 'last_name', 'lastname', 'surname', 'family_name']);
  final full = employeeImportAny(row, const ['full_name', 'employee_name', 'name']);
  return <String>{
    employeeImportNormalizeName('$last $first $middle'),
    employeeImportNormalizeName('$last $first'),
    employeeImportNormalizeName('$first $middle $last'),
    employeeImportNormalizeName('$first $last'),
    employeeImportNormalizeName(full),
    employeeImportPrimaryNameKey(full),
    employeeImportPrimaryNameKey('$last, $first $middle'),
  }..removeWhere((k) => k.isEmpty || k == 'NONE');
}

List<Map<String, dynamic>> employeeImportFindMatches(List<Map<String, dynamic>> existingRows, Map<String, List<Map<String, dynamic>>> byKey, Map<String, String> csvRow, String exactKey, String fullName) {
  final found = <String, Map<String, dynamic>>{};
  void addMatches(Iterable<Map<String, dynamic>> matches) {
    for (final item in matches) {
      found['${item['id']}'] = item;
    }
  }

  addMatches(byKey[exactKey] ?? const <Map<String, dynamic>>[]);
  for (final key in employeeImportCsvMatchKeys(csvRow)) {
    addMatches(byKey[key] ?? const <Map<String, dynamic>>[]);
  }

  if (found.isNotEmpty) return found.values.toList();

  final csvKeys = employeeImportCsvMatchKeys(csvRow);
  for (final item in existingRows) {
    final existingKeys = <String>{
      employeeImportNormalizeName('${item['name_key'] ?? ''}'),
      employeeImportNormalizeName('${item['full_name'] ?? ''}'),
      employeeImportPrimaryNameKey('${item['full_name'] ?? ''}'),
    }..removeWhere((k) => k.isEmpty);
    if (existingKeys.any(csvKeys.contains)) found['${item['id']}'] = item;
  }
  return found.values.toList();
}

'''
    if marker not in text:
        raise SystemExit('Could not find insertion point for matching helpers.')
    text = text.replace(marker, marker + helper, 1)

old_full = r'''String employeeImportFullName(Map<String, String> r) {
  final last = employeeImportClean(r['emp_last_name']).toUpperCase();
  final first = employeeImportClean(r['emp_first_name']).toUpperCase();
  final middle = employeeImportClean(r['emp_middle_name']).toUpperCase();
  return [if (last.isNotEmpty) '$last,', if (first.isNotEmpty) first, if (middle.isNotEmpty) middle].join(' ').replaceAll(RegExp(r'\s+'), ' ').trim();
}
'''
new_full = r'''String employeeImportFullName(Map<String, String> r) {
  final existingFull = employeeImportAny(r, const ['full_name', 'employee_name', 'name']);
  if (existingFull.isNotEmpty) return existingFull.toUpperCase().replaceAll(RegExp(r'\s+'), ' ').trim();
  final last = employeeImportAny(r, const ['emp_last_name', 'last_name', 'lastname', 'surname', 'family_name']).toUpperCase();
  final first = employeeImportAny(r, const ['emp_first_name', 'first_name', 'firstname', 'given_name', 'givenname']).toUpperCase();
  final middle = employeeImportAny(r, const ['emp_middle_name', 'middle_name', 'middlename', 'middle_initial']).toUpperCase();
  return [if (last.isNotEmpty) '$last,', if (first.isNotEmpty) first, if (middle.isNotEmpty) middle].join(' ').replaceAll(RegExp(r'\s+'), ' ').trim();
}
'''
if old_full in text:
    text = text.replace(old_full, new_full, 1)

replacements = {
"final first = employeeImportClean(r['emp_first_name']);": "final first = employeeImportAny(r, const ['emp_first_name', 'first_name', 'firstname', 'given_name', 'givenname']);",
"final last = employeeImportClean(r['emp_last_name']);": "final last = employeeImportAny(r, const ['emp_last_name', 'last_name', 'lastname', 'surname', 'family_name']);",
"final key = employeeImportNormalizeName('$last $first ${r['emp_middle_name'] ?? ''}');": "final key = employeeImportNormalizeName('$last $first ${employeeImportAny(r, const ['emp_middle_name', 'middle_name', 'middlename', 'middle_initial'])}');",
"'gender': employeeImportClean(r['emp_gender']),": "'gender': employeeImportAny(r, const ['emp_gender', 'gender', 'sex']),",
"'birth_date': employeeImportDate(r['birthdate']),": "'birth_date': employeeImportDate(employeeImportAny(r, const ['birthdate', 'birth_date', 'date_of_birth', 'dob', 'emp_birthdate'])),",
"'birth_date': employeeImportDate(r['birthdate'] ?? ''),": "'birth_date': employeeImportDate(employeeImportAny(r, const ['birthdate', 'birth_date', 'date_of_birth', 'dob', 'emp_birthdate'])),",
"'civil_status': employeeImportClean(r['civil_status']),": "'civil_status': employeeImportAny(r, const ['civil_status', 'civilstatus', 'marital_status']),",
"'address': employeeImportClean(r['emp_address']),": "'address': employeeImportAny(r, const ['emp_address', 'address', 'home_address', 'residential_address']),",
"'email': employeeImportClean(r['email']),": "'email': employeeImportAny(r, const ['email', 'email_address', 'emp_email']),",
"'contact_number': employeeImportClean(r['contact_no']),": "'contact_number': employeeImportAny(r, const ['contact_no', 'contact_number', 'mobile_number', 'phone_number', 'emp_contact_no']),",
"'school_graduated': employeeImportClean(r['school_graduated']),": "'school_graduated': employeeImportAny(r, const ['school_graduated', 'school', 'college_university']),",
"'degree_course': employeeImportClean(r['degree_attained']),": "'degree_course': employeeImportAny(r, const ['degree_attained', 'degree_course', 'course', 'program']),\n        'education_level': employeeImportAny(r, const ['education_level', 'educational_attainment', 'degree_attained', 'degree_course']),",
"'date_hired': employeeImportDate(r['employment_date']),": "'date_hired': employeeImportDate(employeeImportAny(r, const ['employment_date', 'date_hired', 'hired_date', 'date_started'])),",
"'date_hired': employeeImportDate(r['employment_date'] ?? ''),": "'date_hired': employeeImportDate(employeeImportAny(r, const ['employment_date', 'date_hired', 'hired_date', 'date_started'])),",
"'starting_date': employeeImportDate(r['employment_date']),": "'starting_date': employeeImportDate(employeeImportAny(r, const ['employment_date', 'date_hired', 'hired_date', 'date_started'])),",
"'starting_date': employeeImportDate(r['employment_date'] ?? ''),": "'starting_date': employeeImportDate(employeeImportAny(r, const ['employment_date', 'date_hired', 'hired_date', 'date_started'])),",
"'guardian_name': employeeImportClean(r['emp_g_name']),": "'guardian_name': employeeImportAny(r, const ['emp_g_name', 'guardian_name', 'emergency_contact_name']),",
"'guardian_address': employeeImportClean(r['emp_g_address']),": "'guardian_address': employeeImportAny(r, const ['emp_g_address', 'guardian_address', 'emergency_contact_address']),",
"'guardian_contact': employeeImportClean(r['emp_g_contact']),": "'guardian_contact': employeeImportAny(r, const ['emp_g_contact', 'guardian_contact', 'emergency_contact_number']),",
"'designation': employeeImportClean(r['emp_designation']),": "'designation': employeeImportAny(r, const ['emp_designation', 'designation', 'position']),",
"'employment_status': employeeImportStatus(r['is_active'] ?? ''),": "'employment_status': employeeImportStatus(employeeImportAny(r, const ['is_active', 'status', 'employment_status'])),",
"'employee_type': employeeImportType(r['emp_status'] ?? ''),": "'employee_type': employeeImportType(employeeImportAny(r, const ['emp_status', 'employee_type', 'appointment_status'])),",
"final matches = byKey[key] ?? const <Map<String, dynamic>>[];": "final matches = employeeImportFindMatches(existingRows, byKey, r, key, fullName);",
"for (final field in ['gender','birth_date','civil_status','address','email','contact_number','school_graduated','degree_course','date_hired','starting_date','guardian_name','guardian_address','guardian_contact','designation']) {": "for (final field in ['bio_number','employee_code','gender','birth_date','civil_status','address','email','contact_number','school_graduated','degree_course','education_level','date_hired','starting_date','guardian_name','guardian_address','guardian_contact','designation','employment_status','employee_type']) {",
}

changed = False
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed = True

# Add bio_number/employee_code mapping after full_name inside data map if not present.
if "'bio_number': employeeImportAny(r," not in text:
    needle = "        'full_name': fullName,\n"
    text = text.replace(needle, needle + "        'bio_number': employeeImportAny(r, const ['bio_number', 'biometric_number', 'bio_no', 'emp_bio_number', 'emp_id', 'employee_id', 'employee_code']),\n        'employee_code': employeeImportAny(r, const ['employee_code', 'emp_code', 'emp_id', 'employee_id']),\n", 1)
    changed = True

# Add primary name key to index loop.
if "employeeImportPrimaryNameKey('${e['full_name'] ?? ''}')" not in text:
    needle = "        employeeImportNormalizeName('${e['full_name'] ?? ''}'),\n"
    text = text.replace(needle, needle + "        employeeImportPrimaryNameKey('${e['full_name'] ?? ''}'),\n", 1)
    changed = True

if not changed and 'List<Map<String, dynamic>> employeeImportFindMatches' in text:
    print('Employee import matching fix is already applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Employee import matching fix applied to lib/main.dart')
