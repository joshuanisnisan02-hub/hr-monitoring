from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

extra_helpers = r'''
List<String> summarySplitNames(Object? value) {
  final raw = formatValue(value).replaceAll('•', ',').replaceAll('\n', ',').replaceAll(';', ',');
  return raw.split(',').map((item) => item.trim()).where((item) => item.isNotEmpty && item != '-').toList();
}

String summaryUpperLabel(Object? value) => summaryGroupLabel(value).toUpperCase().replaceAll(RegExp(r'\s+'), ' ').trim();

void addOrderedGroupedSummary(List<Map<String, dynamic>> rows, String category, List<String> orderedLabels, Map<String, int> counts, {bool addTotal = false}) {
  final used = <String>{};
  var total = 0;
  for (final label in orderedLabels) {
    final key = summaryUpperLabel(label);
    final count = counts[key] ?? 0;
    used.add(key);
    total += count;
    addSummaryCount(rows, category, label, count);
  }
  final extras = counts.keys.where((key) => !used.contains(key)).toList()..sort();
  for (final key in extras) {
    final count = counts[key] ?? 0;
    total += count;
    addSummaryCount(rows, category, key, count);
  }
  if (addTotal) addSummaryCount(rows, category, 'TOTAL', total);
}

const summaryLicenseTypes = <String>[
  'LPT',
  'RCRIM',
  'RSW',
  'RN',
  'RL',
  'RME',
  'RCG',
  'REA',
  'REB',
  'CPA',
  'RPM',
];

const summaryNcTmTypes = <String>[
  'BEAUTY CARE NC II',
  'BOOKKEEPING NC III',
  'BPP NC II',
  'BPP NC III',
  'CAREGIVING NC II',
  'CHS NC II',
  'COOKERY NC II',
  'COOKERY NC III',
  'CSS NC II',
  'DRESSMAKING NC II',
  'DRIVING NC II',
  'EIM NCII',
  'EVENT MANAGEMENT NC III',
  'FBS NC II',
  'FBS NC III',
  'FP NC II',
  'HCS NC II',
  'HOUSEKEEPING NC II',
  'PEST MANAGEMENT NC II',
  'SMAW NC II',
  'TM II',
  'TM NC I',
  'MT NC II',
];

'''

if 'List<String> summarySplitNames(Object? value)' not in text:
    marker = "Future<List<dynamic>> loadHrSummaryReport() async {"
    if marker not in text:
        raise SystemExit('Could not find loadHrSummaryReport insertion point.')
    text = text.replace(marker, extra_helpers + marker, 1)

new_summary_function = r'''Future<List<dynamic>> loadHrSummaryReport() async {
  final employees = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rankings = (await loadRankings(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final licenses = (await loadLicenses(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final certificates = (await loadCertificates(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rows = <Map<String, dynamic>>[];

  var male = 0;
  var female = 0;
  for (final employee in employees) {
    final gender = summaryGenderLabel(employee['gender']);
    if (gender == 'Male') male++;
    if (gender == 'Female') female++;
  }
  addSummaryCount(rows, 'Gender', 'Total Female', female);
  addSummaryCount(rows, 'Gender', 'Total Male', male);
  addSummaryCount(rows, 'Gender', 'Total Gender (Female + Male)', female + male);

  final rankMembers = <String, Set<String>>{};
  for (final ranking in rankings) {
    final rank = summaryGroupLabel(
      emptyToNull(ranking['approved_rank_text']) ?? emptyToNull(ranking['applied_rank_text']) ?? emptyToNull(ranking['previous_rank_text']),
      emptyLabel: 'No Rank / Unspecified',
    );
    final employeeKey = '${ranking['employee_id'] ?? ranking['employee_name'] ?? ranking['id'] ?? ''}'.trim();
    if (employeeKey.isEmpty) continue;
    rankMembers.putIfAbsent(rank, () => <String>{}).add(employeeKey);
  }
  final rankCounts = <String, int>{for (final entry in rankMembers.entries) entry.key: entry.value.length};
  addGroupedSummary(rows, 'Ranks - Total Per Rank', rankCounts);

  final licenseCounts = <String, int>{};
  for (final license in licenses) {
    for (final name in summarySplitNames(license['license_name'])) {
      final key = summaryUpperLabel(name);
      if (key.isEmpty || key == 'UNSPECIFIED') continue;
      licenseCounts[key] = (licenseCounts[key] ?? 0) + 1;
    }
  }
  addOrderedGroupedSummary(rows, 'Type of License', summaryLicenseTypes, licenseCounts, addTotal: true);

  final ncTmCounts = <String, int>{};
  for (final cert in certificates) {
    for (final name in summarySplitNames(cert['certificate_name'])) {
      final key = summaryUpperLabel(name);
      if (key.isEmpty || key == 'UNSPECIFIED') continue;
      ncTmCounts[key] = (ncTmCounts[key] ?? 0) + 1;
    }
  }
  addOrderedGroupedSummary(rows, 'NC/TM', summaryNcTmTypes, ncTmCounts, addTotal: true);

  return rows;
}
'''

text, count = re.subn(r"Future<List<dynamic>> loadHrSummaryReport\(\) async \{.*?\n\}\n\nclass ReportConfig", new_summary_function + "\nclass ReportConfig", text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace loadHrSummaryReport function.')

text = text.replace("Print gender totals and ranking totals only.", "Print gender totals, ranking totals, license totals, and NC/TM totals.")
text = text.replace("Prints total Female, total Male, total Gender, and total employees per rank.", "Prints total Female, total Male, total Gender, total employees per rank, total per license type, and total per NC/TM.")

path.write_text(text, encoding='utf-8')
print('License and NC/TM summary reports patch applied to lib/main.dart')
