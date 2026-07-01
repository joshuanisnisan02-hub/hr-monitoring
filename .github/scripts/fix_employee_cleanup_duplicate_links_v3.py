from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

apply_pos = text.find('employeeNameCleanupApply')
if apply_pos == -1:
    raise SystemExit('employeeNameCleanupApply was not found. The cleanup tool is not fully inserted yet.')
insert_at = text.rfind('Future<void>', 0, apply_pos)
if insert_at == -1:
    insert_at = apply_pos

safe_function = r'''
Future<void> employeeNameCleanupReassignLinksSafe(Object? fromId, Object? toId) async {
  if (fromId == null || toId == null) return;
  final from = fromId.toString();
  final to = toId.toString();

  Future<void> moveOrRemoveSingle(String table) async {
    final target = await db.from(table).select('id').eq('employee_id', to).limit(1);
    if (target.isNotEmpty) {
      await db.from(table).delete().eq('employee_id', from);
    } else {
      await db.from(table).update({'employee_id': to}).eq('employee_id', from);
    }
  }

  await moveOrRemoveSingle('employee_contracts');
  await moveOrRemoveSingle('employee_appointments');

  Future<void> moveOrRemoveByKey(String table, String keyColumn) async {
    final targetRows = await db.from(table).select('id, $keyColumn').eq('employee_id', to).limit(5000);
    final keys = targetRows.map((item) => formatValue((item as Map)[keyColumn]).toLowerCase().trim()).toSet();
    final sourceRows = await db.from(table).select('id, $keyColumn').eq('employee_id', from).limit(5000);
    for (final item in sourceRows) {
      final row = Map<String, dynamic>.from(item as Map);
      final key = formatValue(row[keyColumn]).toLowerCase().trim();
      if (key.isNotEmpty && keys.contains(key)) {
        await db.from(table).delete().eq('id', row['id']);
      } else {
        await db.from(table).update({'employee_id': to}).eq('id', row['id']);
        if (key.isNotEmpty) keys.add(key);
      }
    }
  }

  await moveOrRemoveByKey('employee_licenses', 'license_name');
  await moveOrRemoveByKey('employee_certificates', 'certificate_name');

  final targetEvaluations = await db.from('evaluation_records').select('id, academic_year, semester').eq('employee_id', to).limit(5000);
  final evaluationKeys = targetEvaluations.map((item) {
    final row = Map<String, dynamic>.from(item as Map);
    return '${formatValue(row['academic_year']).toLowerCase().trim()}|${formatValue(row['semester']).toLowerCase().trim()}';
  }).toSet();
  final sourceEvaluations = await db.from('evaluation_records').select('id, academic_year, semester').eq('employee_id', from).limit(5000);
  for (final item in sourceEvaluations) {
    final row = Map<String, dynamic>.from(item as Map);
    final key = '${formatValue(row['academic_year']).toLowerCase().trim()}|${formatValue(row['semester']).toLowerCase().trim()}';
    if (evaluationKeys.contains(key)) {
      await db.from('evaluation_records').delete().eq('id', row['id']);
    } else {
      await db.from('evaluation_records').update({'employee_id': to}).eq('id', row['id']);
      evaluationKeys.add(key);
    }
  }

  final targetRankings = await db.from('ranking_applications').select('id, cycle_id').eq('employee_id', to).limit(5000);
  final rankingKeys = targetRankings.map((item) => '${(item as Map)['cycle_id'] ?? ''}').toSet();
  final sourceRankings = await db.from('ranking_applications').select('id, cycle_id').eq('employee_id', from).limit(5000);
  for (final item in sourceRankings) {
    final row = Map<String, dynamic>.from(item as Map);
    final key = '${row['cycle_id'] ?? ''}';
    if (rankingKeys.contains(key)) {
      await db.from('ranking_applications').delete().eq('id', row['id']);
    } else {
      await db.from('ranking_applications').update({'employee_id': to}).eq('id', row['id']);
      rankingKeys.add(key);
    }
  }
}

'''

if 'employeeNameCleanupReassignLinksSafe(Object? fromId, Object? toId)' not in text:
    text = text[:insert_at] + safe_function + text[insert_at:]

text = text.replace('await employeeNameCleanupReassignLinks(removeId, keepId);', 'await employeeNameCleanupReassignLinksSafe(removeId, keepId);')
text = text.replace('await employeeNameCleanupReassignLinksSafeSafe(removeId, keepId);', 'await employeeNameCleanupReassignLinksSafe(removeId, keepId);')

path.write_text(text, encoding='utf-8')
print('Employee cleanup duplicate linked-record handling fixed with v3 script.')
