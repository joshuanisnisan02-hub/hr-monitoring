from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

helper = r'''
class EmployeeNameCleanupAction {
  final Map<String, dynamic> keep;
  final Map<String, dynamic> remove;
  final int distance;
  const EmployeeNameCleanupAction({required this.keep, required this.remove, required this.distance});
}

final RegExp employeeNameCleanupCredentialRegex = RegExp(
  r'\b(LPT|CPA|RN|RCRIM|RSW|RL|RME|RCG|REA|REB|RPM|PTRP|RMT|RPH|RCE|REE|RMP|ARCH|CRIM|MD|DVM|JD|LLB|MBA|DBA|MAED|MED|PHD|ED\.D|EDD)\b',
  caseSensitive: false,
);

String employeeNameCleanupUpper(Object? value) {
  final raw = formatValue(value).trim();
  if (raw.isEmpty || raw == '-') return '';
  return raw.replaceAll(RegExp(r'\s+'), ' ').toUpperCase();
}

bool employeeNameCleanupHasCredential(Object? value) => employeeNameCleanupCredentialRegex.hasMatch(formatValue(value));

String employeeNameCleanupBase(Object? value) {
  var text = employeeNameCleanupUpper(value);
  text = text.replaceAll(employeeNameCleanupCredentialRegex, ' ');
  text = text.replaceAll(RegExp(r'[^A-Z0-9 ]+'), ' ');
  text = text.replaceAll(RegExp(r'\s+'), ' ').trim();
  return text;
}

int employeeNameCleanupDistance(String a, String b) {
  if (a == b) return 0;
  if (a.isEmpty) return b.length;
  if (b.isEmpty) return a.length;
  final previous = List<int>.generate(b.length + 1, (i) => i);
  final current = List<int>.filled(b.length + 1, 0);
  for (var i = 1; i <= a.length; i++) {
    current[0] = i;
    for (var j = 1; j <= b.length; j++) {
      final cost = a.codeUnitAt(i - 1) == b.codeUnitAt(j - 1) ? 0 : 1;
      current[j] = [
        current[j - 1] + 1,
        previous[j] + 1,
        previous[j - 1] + cost,
      ].reduce((x, y) => x < y ? x : y);
    }
    for (var j = 0; j <= b.length; j++) {
      previous[j] = current[j];
    }
  }
  return previous[b.length];
}

bool employeeNameCleanupSimilar(String a, String b) {
  if (a == b) return true;
  if (a.isEmpty || b.isEmpty) return false;
  final distance = employeeNameCleanupDistance(a, b);
  final maxLength = a.length > b.length ? a.length : b.length;
  return distance <= 2 || (maxLength >= 12 && distance <= 3);
}

bool employeeNameCleanupBlank(Object? value) {
  final text = formatValue(value).trim();
  return text.isEmpty || text == '-' || text.toLowerCase() == 'null';
}

int employeeNameCleanupScore(Map<String, dynamic> row) {
  var score = employeeNameCleanupHasCredential(row['full_name']) ? 10000 : 0;
  for (final key in const [
    'employee_code',
    'bio_number',
    'gender',
    'education_level',
    'date_hired',
    'starting_date',
    'employment_status',
    'designation',
    'employee_type',
    'license_summary',
    'contact_number',
    'email',
  ]) {
    if (!employeeNameCleanupBlank(row[key])) score += 1;
  }
  return score;
}

List<EmployeeNameCleanupAction> employeeNameCleanupFindDuplicates(List<Map<String, dynamic>> rows) {
  final actions = <EmployeeNameCleanupAction>[];
  final usedRemoveIds = <String>{};

  for (var i = 0; i < rows.length; i++) {
    final a = rows[i];
    final aBase = employeeNameCleanupBase(a['full_name']);
    if (aBase.isEmpty) continue;
    for (var j = i + 1; j < rows.length; j++) {
      final b = rows[j];
      final bBase = employeeNameCleanupBase(b['full_name']);
      if (bBase.isEmpty) continue;
      if (!employeeNameCleanupSimilar(aBase, bBase)) continue;

      final aHasCred = employeeNameCleanupHasCredential(a['full_name']);
      final bHasCred = employeeNameCleanupHasCredential(b['full_name']);
      if (!aHasCred && !bHasCred) continue;

      Map<String, dynamic> keep;
      Map<String, dynamic> remove;
      if (aHasCred && !bHasCred) {
        keep = a;
        remove = b;
      } else if (!aHasCred && bHasCred) {
        keep = b;
        remove = a;
      } else if (employeeNameCleanupScore(a) >= employeeNameCleanupScore(b)) {
        keep = a;
        remove = b;
      } else {
        keep = b;
        remove = a;
      }

      final removeId = '${remove['id'] ?? ''}';
      if (removeId.isEmpty || usedRemoveIds.contains(removeId)) continue;
      usedRemoveIds.add(removeId);
      actions.add(EmployeeNameCleanupAction(keep: keep, remove: remove, distance: employeeNameCleanupDistance(aBase, bBase)));
    }
  }
  return actions;
}

Map<String, dynamic> employeeNameCleanupMergeData(Map<String, dynamic> keep, Map<String, dynamic> remove) {
  final data = <String, dynamic>{
    'full_name': employeeNameCleanupUpper(keep['full_name']),
    'name_key': normalizeName(employeeNameCleanupUpper(keep['full_name'])),
  };
  for (final key in const [
    'employee_code',
    'bio_number',
    'gender',
    'education_level',
    'date_hired',
    'starting_date',
    'designation',
    'employee_type',
    'civil_status',
    'teaching_status',
    'current_salary',
    'license_summary',
    'birth_date',
    'address',
    'contact_number',
    'email',
    'guardian_name',
    'guardian_relationship',
    'guardian_contact',
    'guardian_address',
    'school_graduated',
    'degree_course',
    'notes',
  ]) {
    if (employeeNameCleanupBlank(keep[key]) && !employeeNameCleanupBlank(remove[key])) {
      data[key] = remove[key];
    }
  }
  final keepStatus = formatValue(keep['employment_status']).trim().toLowerCase();
  final removeStatus = formatValue(remove['employment_status']).trim();
  if ((keepStatus.isEmpty || keepStatus == '-' || keepStatus == 'inactive') && removeStatus.isNotEmpty && removeStatus != '-') {
    data['employment_status'] = remove['employment_status'];
  }
  data['updated_at'] = DateTime.now().toIso8601String();
  return data;
}

Future<void> employeeNameCleanupReassignLinks(Object? fromId, Object? toId) async {
  if (fromId == null || toId == null) return;
  for (final table in const [
    'employee_contracts',
    'employee_licenses',
    'employee_certificates',
    'evaluation_records',
    'employee_appointments',
    'ranking_applications',
  ]) {
    await db.from(table).update({'employee_id': toId}).eq('employee_id', fromId);
  }
}

Future<void> employeeNameCleanupApply(List<EmployeeNameCleanupAction> actions, List<Map<String, dynamic>> allRows) async {
  final removeIds = actions.map((a) => '${a.remove['id'] ?? ''}').where((id) => id.isNotEmpty).toSet();

  for (final action in actions) {
    final keepId = action.keep['id'];
    final removeId = action.remove['id'];
    if (keepId == null || removeId == null || '$keepId' == '$removeId') continue;
    await db.from('employees').update(employeeNameCleanupMergeData(action.keep, action.remove)).eq('id', keepId);
    await employeeNameCleanupReassignLinks(removeId, keepId);
    await db.from('employees').delete().eq('id', removeId);
  }

  for (final row in allRows) {
    final id = row['id'];
    if (id == null || removeIds.contains('$id')) continue;
    final upperName = employeeNameCleanupUpper(row['full_name']);
    if (upperName.isEmpty) continue;
    if (formatValue(row['full_name']) != upperName || formatValue(row['name_key']) != normalizeName(upperName)) {
      await db.from('employees').update({
        'full_name': upperName,
        'name_key': normalizeName(upperName),
        'updated_at': DateTime.now().toIso8601String(),
      }).eq('id', id);
    }
  }
}

Future<void> showEmployeeNameCleanup(BuildContext context, VoidCallback refresh) async {
  showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (_) => const AlertDialog(content: SizedBox(width: 260, child: Row(children: [CircularProgressIndicator(), SizedBox(width: 16), Text('Checking employee names...')]))),
  );

  late final List<Map<String, dynamic>> rows;
  try {
    rows = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  } catch (e) {
    if (context.mounted) Navigator.pop(context);
    if (context.mounted) showSnack(context, 'Name cleanup check failed: $e');
    return;
  }

  final renameCount = rows.where((row) {
    final upper = employeeNameCleanupUpper(row['full_name']);
    return upper.isNotEmpty && formatValue(row['full_name']) != upper;
  }).length;
  final actions = employeeNameCleanupFindDuplicates(rows);

  if (!context.mounted) return;
  Navigator.pop(context);

  final confirmed = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Fix Employee Names and Duplicates?'),
      content: SizedBox(
        width: 780,
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('This will uppercase $renameCount employee name${renameCount == 1 ? '' : 's'} and remove ${actions.length} duplicate${actions.length == 1 ? '' : 's'} by keeping the name with credentials such as LPT, RSW, RN, CPA, etc.', style: const TextStyle(color: _muted, fontWeight: FontWeight.w600)),
          const SizedBox(height: 14),
          if (actions.isEmpty)
            const Text('No credential-based duplicate names were found.', style: TextStyle(fontWeight: FontWeight.w800, color: _ink))
          else
            ConstrainedBox(
              constraints: const BoxConstraints(maxHeight: 420),
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: actions.length,
                separatorBuilder: (_, __) => const Divider(height: 18),
                itemBuilder: (_, i) {
                  final action = actions[i];
                  return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('KEEP: ${employeeNameCleanupUpper(action.keep['full_name'])}', style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF15803D))),
                    const SizedBox(height: 4),
                    Text('REMOVE: ${employeeNameCleanupUpper(action.remove['full_name'])}', style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFFB91C1C))),
                  ]);
                },
              ),
            ),
        ]),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton.icon(onPressed: () => Navigator.pop(context, true), icon: const Icon(Icons.cleaning_services_rounded), label: const Text('Apply Cleanup')),
      ],
    ),
  );

  if (confirmed != true) return;

  showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (_) => const AlertDialog(content: SizedBox(width: 260, child: Row(children: [CircularProgressIndicator(), SizedBox(width: 16), Text('Applying cleanup...')]))),
  );

  try {
    await employeeNameCleanupApply(actions, rows);
    if (context.mounted) Navigator.pop(context);
    refresh();
    if (context.mounted) showSnack(context, 'Employee names cleaned and duplicates removed.');
  } catch (e) {
    if (context.mounted) Navigator.pop(context);
    if (context.mounted) showSnack(context, 'Name cleanup failed: $e');
  }
}

'''

if 'class EmployeeNameCleanupAction' not in text:
    marker = 'class EmployeesPage extends StatefulWidget {'
    if marker not in text:
        raise SystemExit('EmployeesPage insertion point was not found.')
    text = text.replace(marker, helper + marker, 1)

if 'Fix Names & Duplicates' not in text:
    idx = text.find("label: const Text('Import Employee Info')")
    if idx == -1:
        raise SystemExit('Import Employee Info button was not found.')
    wrap_start = text.rfind('children: [', 0, idx)
    if wrap_start == -1:
        raise SystemExit('Employee buttons children list was not found.')
    insert_at = wrap_start + len('children: [')
    button = r'''
                  OutlinedButton.icon(
                    onPressed: () async {
                      await showEmployeeNameCleanup(context, refreshEmployees);
                      if (mounted) refreshEmployees();
                    },
                    icon: const Icon(Icons.text_fields_rounded),
                    label: const Text('Fix Names & Duplicates'),
                  ),
'''
    text = text[:insert_at] + button + text[insert_at:]

path.write_text(text, encoding='utf-8')
print('Employee uppercase and credential duplicate cleanup tool added to lib/main.dart')
