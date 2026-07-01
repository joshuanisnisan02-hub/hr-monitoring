from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

helper_marker = "class EmployeesPage extends StatefulWidget {"
helper_code = r'''
class EmployeeDuplicateFix {
  final Map<String, dynamic> keep;
  final Map<String, dynamic> remove;
  final String baseName;
  const EmployeeDuplicateFix({required this.keep, required this.remove, required this.baseName});
}

final RegExp _employeeCredentialSuffixRegex = RegExp(
  r'\b(LPT|CPA|RN|RCRIM|RSW|RL|RME|RCG|REA|REB|RPM|PTRP|RMT|RPH|RCE|REE|RMP|ARCH|CRIM)\b',
  caseSensitive: false,
);

String employeeDuplicateBaseKey(Object? value) {
  var text = formatValue(value).toUpperCase();
  text = text.replaceAll(_employeeCredentialSuffixRegex, ' ');
  text = text.replaceAll(RegExp(r'[^A-Z0-9 ]+'), ' ');
  text = text.replaceAll(RegExp(r'\s+'), ' ').trim();
  return text.toLowerCase();
}

bool employeeNameHasCredentialSuffix(Object? value) => _employeeCredentialSuffixRegex.hasMatch(formatValue(value));

int employeeDuplicateScore(Map<String, dynamic> row) {
  var score = 0;
  if (employeeNameHasCredentialSuffix(row['full_name'])) score += 10000;
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
    if (formatValue(row[key]).trim().isNotEmpty && formatValue(row[key]).trim() != '-') score += 1;
  }
  score += formatValue(row['full_name']).length;
  return score;
}

Future<List<EmployeeDuplicateFix>> findEmployeeDuplicateFixes() async {
  final rows = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final row in rows) {
    final key = employeeDuplicateBaseKey(row['full_name']);
    if (key.isEmpty) continue;
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }

  final fixes = <EmployeeDuplicateFix>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.length < 2) continue;
    list.sort((a, b) => employeeDuplicateScore(b).compareTo(employeeDuplicateScore(a)));
    final keep = list.first;
    final keepHasCredential = employeeNameHasCredentialSuffix(keep['full_name']);
    for (final remove in list.skip(1)) {
      final removeHasCredential = employeeNameHasCredentialSuffix(remove['full_name']);
      if (keepHasCredential && !removeHasCredential) {
        fixes.add(EmployeeDuplicateFix(keep: keep, remove: remove, baseName: entry.key));
      }
    }
  }
  return fixes;
}

Future<void> reassignEmployeeLinks(Object? fromId, Object? toId) async {
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

Future<void> applyEmployeeDuplicateFixes(List<EmployeeDuplicateFix> fixes) async {
  for (final fix in fixes) {
    final removeId = fix.remove['id'];
    final keepId = fix.keep['id'];
    if (removeId == null || keepId == null || '$removeId' == '$keepId') continue;
    await reassignEmployeeLinks(removeId, keepId);
    await db.from('employees').delete().eq('id', removeId);
  }
}

Future<void> showEmployeeDuplicateCleanup(BuildContext context) async {
  showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (_) => const AlertDialog(content: SizedBox(width: 240, child: Row(children: [CircularProgressIndicator(), SizedBox(width: 16), Text('Checking duplicates...')]))),
  );

  List<EmployeeDuplicateFix> fixes;
  try {
    fixes = await findEmployeeDuplicateFixes();
  } catch (e) {
    if (context.mounted) Navigator.pop(context);
    if (context.mounted) showInfo(context, 'Duplicate Check Failed', '$e');
    return;
  }

  if (!context.mounted) return;
  Navigator.pop(context);

  if (fixes.isEmpty) {
    showInfo(context, 'No Duplicates Found', 'No plain duplicate employee names were found where another record has a credential suffix like LPT, CPA, RN, etc.');
    return;
  }

  final confirmed = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Remove ${fixes.length} Plain Duplicate${fixes.length == 1 ? '' : 's'}?'),
      content: SizedBox(
        width: 760,
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('This will keep the richer/name-with-credential record and remove the plain duplicate. Linked records such as contracts, licenses, certificates, evaluations, appointments, and rankings will be moved to the kept employee before deleting.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600)),
          const SizedBox(height: 14),
          ConstrainedBox(
            constraints: const BoxConstraints(maxHeight: 420),
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: fixes.length,
              separatorBuilder: (_, __) => const Divider(height: 18),
              itemBuilder: (_, i) {
                final fix = fixes[i];
                return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('KEEP: ${formatValue(fix.keep['full_name'])}', style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF15803D))),
                  const SizedBox(height: 4),
                  Text('REMOVE: ${formatValue(fix.remove['full_name'])}', style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFFB91C1C))),
                ]);
              },
            ),
          ),
        ]),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton.icon(onPressed: () => Navigator.pop(context, true), icon: const Icon(Icons.cleaning_services_rounded), label: const Text('Remove Plain Duplicates')),
      ],
    ),
  );

  if (confirmed != true) return;

  showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (_) => const AlertDialog(content: SizedBox(width: 260, child: Row(children: [CircularProgressIndicator(), SizedBox(width: 16), Text('Cleaning duplicates...')]))),
  );

  try {
    await applyEmployeeDuplicateFixes(fixes);
    if (context.mounted) Navigator.pop(context);
    if (context.mounted) showInfo(context, 'Duplicates Removed', '${fixes.length} duplicate employee record${fixes.length == 1 ? '' : 's'} removed safely.');
  } catch (e) {
    if (context.mounted) Navigator.pop(context);
    if (context.mounted) showInfo(context, 'Cleanup Failed', '$e');
  }
}

'''

if 'class EmployeeDuplicateFix {' not in text:
    if helper_marker not in text:
        raise SystemExit('EmployeesPage insertion point was not found.')
    text = text.replace(helper_marker, helper_code + helper_marker, 1)

old_button = r'''                FilledButton.icon(
                  onPressed: () async {
                    await importEmployeeCsvInfo(context);
                    if (mounted) refreshEmployees();
                  },
                  icon: const Icon(Icons.upload_file_rounded),
                  label: const Text('Import Employee Info'),
                ),'''
new_buttons = r'''                Wrap(spacing: 10, runSpacing: 10, alignment: WrapAlignment.end, children: [
                  OutlinedButton.icon(
                    onPressed: () async {
                      await showEmployeeDuplicateCleanup(context);
                      if (mounted) refreshEmployees();
                    },
                    icon: const Icon(Icons.rule_rounded),
                    label: const Text('Check Duplicates'),
                  ),
                  FilledButton.icon(
                    onPressed: () async {
                      await importEmployeeCsvInfo(context);
                      if (mounted) refreshEmployees();
                    },
                    icon: const Icon(Icons.upload_file_rounded),
                    label: const Text('Import Employee Info'),
                  ),
                ]),'''

if old_button in text:
    text = text.replace(old_button, new_buttons, 1)
elif 'Check Duplicates' in text:
    pass
else:
    raise SystemExit('Import Employee Info button block was not found.')

path.write_text(text, encoding='utf-8')
print('Employee duplicate cleanup patch applied to lib/main.dart')
