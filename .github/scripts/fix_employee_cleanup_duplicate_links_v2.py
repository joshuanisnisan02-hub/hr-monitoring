from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

apply_marker = 'Future<void> employeeNameCleanupApply(List<EmployeeNameCleanupAction> actions, List<Map<String, dynamic>> allRows) async {'
if apply_marker not in text:
    raise SystemExit('employeeNameCleanupApply was not found. Run add_employee_name_cleanup_tool.py first, then run this v2 script.')

safe_function = r'''
Future<void> employeeNameCleanupReassignLinksSafe(Object? fromId, Object? toId) async {
  if (fromId == null || toId == null) return;
  final from = fromId.toString();
  final to = toId.toString();

  Future<void> updateOrDeleteSingleRecordTable(String table) async {
    final target = await db.from(table).select('id').eq('employee_id', to).limit(1);
    if (target.isNotEmpty) {
      await db.from(table).delete().eq('employee_id', from);
    } else {
      await db.from(table).update({'employee_id': to}).eq('employee_id', from);
    }
  }

  await updateOrDeleteSingleRecordTable('employee_contracts');
  await updateOrDeleteSingleRecordTable('employee_appointments');

  final targetLicenses = await db.from('employee_licenses').select('id, license_name').eq('employee_id', to).limit(5000);
  final targetLicenseKeys = targetLicenses.map((item) => formatValue((item as Map)['license_name']).toLowerCase().trim()).toSet();
  final sourceLicenses = await db.from('employee_licenses').select('id, license_name').eq('employee_id', from).limit(5000);
  for (final item in sourceLicenses) {
    final row = Map<String, dynamic>.from(item as Map);
    final key = formatValue(row['license_name']).toLowerCase().trim();
    if (key.isNotEmpty && targetLicenseKeys.contains(key)) {
      await db.from('employee_licenses').delete().eq('id', row['id']);
    } else {
      await db.from('employee_licenses').update({'employee_id': to}).eq('id', row['id']);
      if (key.isNotEmpty) targetLicenseKeys.add(key);
    }
  }

  final targetCertificates = await db.from('employee_certificates').select('id, certificate_name').eq('employee_id', to).limit(5000);
  final targetCertificateKeys = targetCertificates.map((item) => formatValue((item as Map)['certificate_name']).toLowerCase().trim()).toSet();
  final sourceCertificates = await db.from('employee_certificates').select('id, certificate_name').eq('employee_id', from).limit(5000);
  for (final item in sourceCertificates) {
    final row = Map<String, dynamic>.from(item as Map);
    final key = formatValue(row['certificate_name']).toLowerCase().trim();
    if (key.isNotEmpty && targetCertificateKeys.contains(key)) {
      await db.from('employee_certificates').delete().eq('id', row['id']);
    } else {
      await db.from('employee_certificates').update({'employee_id': to}).eq('id', row['id']);
      if (key.isNotEmpty) targetCertificateKeys.add(key);
    }
  }

  final targetEvaluations = await db.from('evaluation_records').select('id, academic_year, semester').eq('employee_id', to).limit(5000);
  final targetEvaluationKeys = targetEvaluations.map((item) {
    final row = Map<String, dynamic>.from(item as Map);
    return '${formatValue(row['academic_year']).toLowerCase().trim()}|${formatValue(row['semester']).toLowerCase().trim()}';
  }).toSet();
  final sourceEvaluations = await db.from('evaluation_records').select('id, academic_year, semester').eq('employee_id', from).limit(5000);
  for (final item in sourceEvaluations) {
    final row = Map<String, dynamic>.from(item as Map);
    final key = '${formatValue(row['academic_year']).toLowerCase().trim()}|${formatValue(row['semester']).toLowerCase().trim()}';
    if (targetEvaluationKeys.contains(key)) {
      await db.from('evaluation_records').delete().eq('id', row['id']);
    } else {
      await db.from('evaluation_records').update({'employee_id': to}).eq('id', row['id']);
      targetEvaluationKeys.add(key);
    }
  }

  final targetRankings = await db.from('ranking_applications').select('id, cycle_id').eq('employee_id', to).limit(5000);
  final targetRankingKeys = targetRankings.map((item) => '${(item as Map)['cycle_id'] ?? ''}').toSet();
  final sourceRankings = await db.from('ranking_applications').select('id, cycle_id').eq('employee_id', from).limit(5000);
  for (final item in sourceRankings) {
    final row = Map<String, dynamic>.from(item as Map);
    final key = '${row['cycle_id'] ?? ''}';
    if (targetRankingKeys.contains(key)) {
      await db.from('ranking_applications').delete().eq('id', row['id']);
    } else {
      await db.from('ranking_applications').update({'employee_id': to}).eq('id', row['id']);
      targetRankingKeys.add(key);
    }
  }
}

'''

if 'Future<void> employeeNameCleanupReassignLinksSafe' not in text:
    text = text.replace(apply_marker, safe_function + apply_marker, 1)

# Redirect any older cleanup call to the safe conflict-aware version.
text = text.replace('await employeeNameCleanupReassignLinks(removeId, keepId);', 'await employeeNameCleanupReassignLinksSafe(removeId, keepId);')
text = text.replace('await employeeNameCleanupReassignLinksSafeSafe(removeId, keepId);', 'await employeeNameCleanupReassignLinksSafe(removeId, keepId);')

path.write_text(text, encoding='utf-8')
print('Employee cleanup linked-record conflict handling fixed with v2 script in lib/main.dart')
