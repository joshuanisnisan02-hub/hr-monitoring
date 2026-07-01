from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

changed = False

old_sidebar = """        const SizedBox(height: 30),
        for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
        const Spacer(),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
          child: const Text('Employee add flow now includes full profile, contract, and credential details.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.35, fontWeight: FontWeight.w600)),
        ),
"""
new_sidebar = """        const SizedBox(height: 30),
        Expanded(
          child: ListView(
            padding: EdgeInsets.zero,
            children: [
              for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
            ],
          ),
        ),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
          child: const Text('HR records and printable summaries.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.25, fontWeight: FontWeight.w600)),
        ),
"""
if old_sidebar in text:
    text = text.replace(old_sidebar, new_sidebar, 1)
    changed = True
elif "HR records and printable summaries." in text:
    pass
else:
    raise SystemExit('Sidebar overflow block was not found.')

new_summary_function = r'''Future<List<dynamic>> loadHrSummaryReport() async {
  final employees = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  final rankings = (await loadRankings(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
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

  return rows;
}
'''

if 'Future<List<dynamic>> loadHrSummaryReport() async {' in text:
    text, count = re.subn(r"Future<List<dynamic>> loadHrSummaryReport\(\) async \{.*?\n\}\n\nclass ReportConfig", new_summary_function + "\nclass ReportConfig", text, count=1, flags=re.S)
    if count == 0:
        raise SystemExit('Could not replace loadHrSummaryReport function.')
    changed = True
else:
    raise SystemExit('loadHrSummaryReport was not found. Run apply_summary_reports_patch.py first.')

new_reports_getter = r'''  List<ReportConfig> get reports => [
        ReportConfig('HR Summary Report', () => loadHrSummaryReport(), const [
          GridCol('category', 'Category', flex: 2),
          GridCol('item', 'Item', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
      ];
'''

text, count = re.subn(r"  List<ReportConfig> get reports => \[.*?\n      \];", new_reports_getter, text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace reports getter.')
changed = True

text = text.replace("subtitle: 'Print detailed reports and summary totals per HR module.',", "subtitle: 'Print gender totals and ranking totals only.',")
text = text.replace("Choose HR Summary Report for totals, or select a module report for detailed records. Opens a print-ready A4 landscape report.", "Prints total Female, total Male, total Gender, and total employees per rank.")

if changed:
    path.write_text(text, encoding='utf-8')
    print('Sidebar overflow and limited HR summary report patch applied to lib/main.dart')
else:
    print('No changes needed.')
