from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

canonical_block = r'''Future<List<dynamic>> loadHrGenderSummaryReport() async {
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
  final rankRefs = await rankOptions();
  final rankings = (await loadRankings(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rows = <Map<String, dynamic>>[];
  final orderedRanks = <String>[];
  final rankCounts = <String, int>{};

  for (final option in uniqueOptions(rankRefs)) {
    final label = summaryGroupLabel(option.value, emptyLabel: '').trim();
    if (label.isEmpty || rankCounts.containsKey(label)) continue;
    orderedRanks.add(label);
    rankCounts[label] = 0;
  }

  for (final ranking in rankings) {
    final rank = summaryGroupLabel(
      emptyToNull(ranking['approved_rank_text']) ?? emptyToNull(ranking['applied_rank_text']) ?? emptyToNull(ranking['previous_rank_text']),
      emptyLabel: 'No Rank / Unspecified',
    );
    final employeeKey = '${ranking['employee_id'] ?? ranking['employee_name'] ?? ranking['id'] ?? ''}'.trim();
    if (employeeKey.isEmpty) continue;
    rankCounts[rank] = (rankCounts[rank] ?? 0) + 1;
    if (!orderedRanks.contains(rank)) orderedRanks.add(rank);
  }

  for (final rank in orderedRanks) {
    addSummaryCount(rows, 'Ranks - Total Per Rank', rank, rankCounts[rank] ?? 0);
  }
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

start = text.find('Future<List<dynamic>> loadHrGenderSummaryReport() async')
end_marker = 'class ReportConfig'
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit('Could not find summary loader block to clean.')

text = text[:start] + canonical_block + text[end:]

# Enforce two-column separate category reports.
reports_getter = r'''  List<ReportConfig> get reports => [
        ReportConfig('Gender Summary Report', () => loadHrGenderSummaryReport(), const [
          GridCol('item', 'Gender', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Ranks Summary Report', () => loadRankSummaryReport(), const [
          GridCol('item', 'Rank', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Type of License Summary Report', () => loadLicenseTypeSummaryReport(), const [
          GridCol('item', 'Type of License', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('NC/TM Summary Report', () => loadNcTmSummaryReport(), const [
          GridCol('item', 'NC/TM', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
      ];
'''
text, count = re.subn(r"  List<ReportConfig> get reports => \[.*?\n      \];", reports_getter, text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace reports getter.')

path.write_text(text, encoding='utf-8')
print('Duplicate summary loader functions fixed in lib/main.dart')
