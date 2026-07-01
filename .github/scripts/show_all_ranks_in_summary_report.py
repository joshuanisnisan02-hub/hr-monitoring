from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

new_rank_function = r'''Future<List<dynamic>> loadRankSummaryReport() async {
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
'''

if 'Future<List<dynamic>> loadRankSummaryReport() async {' not in text:
    raise SystemExit('loadRankSummaryReport was not found. Run separate_summary_reports_by_category.py first.')

text, count = re.subn(r"Future<List<dynamic>> loadRankSummaryReport\(\) async \{.*?\n\}\n\nFuture<List<dynamic>> loadLicenseTypeSummaryReport", new_rank_function + "\nFuture<List<dynamic>> loadLicenseTypeSummaryReport", text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace loadRankSummaryReport function.')

path.write_text(text, encoding='utf-8')
print('All ranks summary report patch applied to lib/main.dart')
