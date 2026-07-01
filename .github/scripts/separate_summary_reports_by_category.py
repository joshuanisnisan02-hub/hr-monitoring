from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

new_functions = r'''Future<List<dynamic>> loadHrGenderSummaryReport() async {
  final employees = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
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
  return rows;
}

Future<List<dynamic>> loadRankSummaryReport() async {
  final rankings = (await loadRankings(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rows = <Map<String, dynamic>>[];
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
  return rows;
}

Future<List<dynamic>> loadLicenseTypeSummaryReport() async {
  final licenses = (await loadLicenses(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rows = <Map<String, dynamic>>[];
  final licenseCounts = <String, int>{};
  for (final license in licenses) {
    for (final name in summarySplitNames(license['license_name'])) {
      final key = summaryUpperLabel(name);
      if (key.isEmpty || key == 'UNSPECIFIED') continue;
      licenseCounts[key] = (licenseCounts[key] ?? 0) + 1;
    }
  }
  addOrderedGroupedSummary(rows, 'Type of License', summaryLicenseTypes, licenseCounts, addTotal: true);
  return rows;
}

Future<List<dynamic>> loadNcTmSummaryReport() async {
  final certificates = (await loadCertificates(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rows = <Map<String, dynamic>>[];
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

Future<List<dynamic>> loadHrSummaryReport() async {
  final rows = <Map<String, dynamic>>[];
  rows.addAll((await loadHrGenderSummaryReport()).cast<Map<String, dynamic>>());
  rows.addAll((await loadRankSummaryReport()).cast<Map<String, dynamic>>());
  rows.addAll((await loadLicenseTypeSummaryReport()).cast<Map<String, dynamic>>());
  rows.addAll((await loadNcTmSummaryReport()).cast<Map<String, dynamic>>());
  return rows;
}
'''

if 'Future<List<dynamic>> loadHrSummaryReport() async {' not in text:
    raise SystemExit('loadHrSummaryReport was not found. Run add_license_nc_tm_summary_reports.py first.')

text, count = re.subn(r"Future<List<dynamic>> loadHrSummaryReport\(\) async \{.*?\n\}\n\nclass ReportConfig", new_functions + "\nclass ReportConfig", text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace summary loader block.')

new_reports_getter = r'''  List<ReportConfig> get reports => [
        ReportConfig('Gender Summary Report', () => loadHrGenderSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'Item', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Ranks Summary Report', () => loadRankSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'Rank', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Type of License Summary Report', () => loadLicenseTypeSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'Type of License', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('NC/TM Summary Report', () => loadNcTmSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'NC/TM', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Complete HR Summary Report', () => loadHrSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'Item', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
      ];
'''

text, count = re.subn(r"  List<ReportConfig> get reports => \[.*?\n      \];", new_reports_getter, text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace reports getter.')

text = text.replace("subtitle: 'Print gender totals, ranking totals, license totals, and NC/TM totals.',", "subtitle: 'Print each summary category separately.' ,")
text = text.replace("subtitle: 'Print each summary category separately.' ,", "subtitle: 'Print each summary category separately.',")
text = text.replace("Prints total Female, total Male, total Gender, total employees per rank, total per license type, and total per NC/TM.", "Select one category, then print only that category. Use Complete HR Summary Report only when you need all totals together.")
text = text.replace("decoration: const InputDecoration(labelText: 'Report Type'),", "decoration: const InputDecoration(labelText: 'Summary Category'),")

path.write_text(text, encoding='utf-8')
print('Separate summary reports by category patch applied to lib/main.dart')
