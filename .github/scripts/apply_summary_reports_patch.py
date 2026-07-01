from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

helper_marker = """class ReportConfig {
"""
helper_code = r'''
String summaryGroupLabel(Object? value, {String emptyLabel = 'Unspecified'}) {
  final text = formatValue(value).trim();
  if (text.isEmpty || text == '-' || text.toLowerCase() == 'null') return emptyLabel;
  return text;
}

String summaryGenderLabel(Object? value) {
  final text = summaryGroupLabel(value).toLowerCase();
  if (text == 'm' || text == 'male') return 'Male';
  if (text == 'f' || text == 'female') return 'Female';
  return 'Unspecified / Other';
}

String summaryEmployeeTypeLabel(Object? value) {
  final text = summaryGroupLabel(value).replaceAll('_', ' ').trim();
  if (text.isEmpty || text == 'Unspecified') return 'Unspecified';
  return text.split(RegExp(r'\s+')).map((part) => part.isEmpty ? part : '${part[0].toUpperCase()}${part.length > 1 ? part.substring(1).toLowerCase() : ''}').join(' ');
}

void addSummaryCount(List<Map<String, dynamic>> rows, String category, String item, int total) {
  rows.add({'category': category, 'item': item, 'total': total});
}

void addGroupedSummary(List<Map<String, dynamic>> rows, String category, Map<String, int> counts) {
  final entries = counts.entries.toList()..sort((a, b) => a.key.toLowerCase().compareTo(b.key.toLowerCase()));
  for (final entry in entries) {
    addSummaryCount(rows, category, entry.key, entry.value);
  }
}

Future<List<dynamic>> loadHrSummaryReport() async {
  final employees = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rankings = (await loadRankings(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rows = <Map<String, dynamic>>[];

  addSummaryCount(rows, 'Employees', 'Total Employees', employees.length);

  final genderCounts = <String, int>{};
  final typeCounts = <String, int>{};
  final statusCounts = <String, int>{};
  final teachingCounts = <String, int>{};
  for (final employee in employees) {
    final gender = summaryGenderLabel(employee['gender']);
    final type = summaryEmployeeTypeLabel(employee['employee_type']);
    final status = summaryEmployeeTypeLabel(employee['employment_status']);
    final teaching = summaryEmployeeTypeLabel(employee['teaching_status']);
    genderCounts[gender] = (genderCounts[gender] ?? 0) + 1;
    typeCounts[type] = (typeCounts[type] ?? 0) + 1;
    statusCounts[status] = (statusCounts[status] ?? 0) + 1;
    teachingCounts[teaching] = (teachingCounts[teaching] ?? 0) + 1;
  }
  addGroupedSummary(rows, 'Gender', genderCounts);
  addGroupedSummary(rows, 'Employee Type', typeCounts);
  addGroupedSummary(rows, 'Employment Status', statusCounts);
  addGroupedSummary(rows, 'Teaching Status', teachingCounts);

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
  addSummaryCount(rows, 'Ranking', 'Total Employees With Ranking Record', rankMembers.values.fold<Set<String>>(<String>{}, (set, ids) => set..addAll(ids)).length);
  addGroupedSummary(rows, 'Ranking Per Rank', rankCounts);

  return rows;
}

'''

if 'Future<List<dynamic>> loadHrSummaryReport()' not in text:
    if helper_marker not in text:
        raise SystemExit('ReportConfig insertion point was not found.')
    text = text.replace(helper_marker, helper_code + helper_marker, 1)

old_reports_start = """  List<ReportConfig> get reports => [
        ReportConfig('Employee Master List', () => loadEmployees(limit: 5000), const [
"""
new_reports_start = """  List<ReportConfig> get reports => [
        ReportConfig('HR Summary Report', () => loadHrSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'Item', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Employee Master List', () => loadEmployees(limit: 5000), const [
"""

if old_reports_start in text and "ReportConfig('HR Summary Report'" not in text:
    text = text.replace(old_reports_start, new_reports_start, 1)
elif "ReportConfig('HR Summary Report'" in text:
    print('HR Summary Report is already added.')
else:
    raise SystemExit('Reports list insertion point was not found.')

old_subtitle = "subtitle: 'Print reports per HR module.',"
new_subtitle = "subtitle: 'Print detailed reports and summary totals per HR module.'"
if old_subtitle in text:
    text = text.replace(old_subtitle, new_subtitle, 1)

old_help = "const Expanded(child: Text('Opens a print-ready A4 landscape report.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600))),"
new_help = "const Expanded(child: Text('Choose HR Summary Report for totals, or select a module report for detailed records. Opens a print-ready A4 landscape report.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600))),"
if old_help in text:
    text = text.replace(old_help, new_help, 1)

path.write_text(text, encoding='utf-8')
print('Summary reports patch applied to lib/main.dart')
