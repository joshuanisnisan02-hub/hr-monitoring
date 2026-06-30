from pathlib import Path
import textwrap

p = Path('lib/main.dart')
s = p.read_text()

# Remove Reports page from shell pages and sidebar navigation.
s = s.replace("      const RankingPage(),\n      const ReportsPage(),", "      const RankingPage(),", 1)
s = s.replace("      NavItem('Ranking', Icons.leaderboard_rounded),\n      NavItem('Reports', Icons.print_rounded),", "      NavItem('Ranking', Icons.leaderboard_rounded),", 1)
s = s.replace("                  QuickCard('Print Reports', Icons.print_rounded, () => onNavigate(6)),\n", "", 1)

# Add print support to CrudTable.
s = s.replace(
    """  final ViewHandler? onView;
  final bool showDelete;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, this.allowAdd = true, required this.columns, this.onAdd, required this.onEdit, this.onView, this.showDelete = true, required this.onDelete});""",
    """  final ViewHandler? onView;
  final bool showDelete;
  final String? reportTitle;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, this.allowAdd = true, required this.columns, this.onAdd, required this.onEdit, this.onView, this.showDelete = true, this.reportTitle, required this.onDelete});""",
    1,
)

# Add a print helper inside _CrudTableState.
if 'void printRows(List<Map<String, dynamic>> rows)' not in s:
    s = s.replace(
        """  void refresh() => setState(() {
        future = widget.load();
        page = 0;
      });
""",
        """  void refresh() => setState(() {
        future = widget.load();
        page = 0;
      });

  void printRows(List<Map<String, dynamic>> rows) {
    final baseTitle = widget.reportTitle ?? (widget.addLabel.toLowerCase().startsWith('add ') ? '${widget.addLabel.substring(4)} Report' : '${widget.addLabel} Report');
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final markup = buildPrintableReportHtml(baseTitle, widget.columns, rows);
      final blob = html.Blob([markup], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      if (printWindow != null) {
        printWindow.location.href = url;
      } else {
        html.window.open(url, '_blank');
      }
    } catch (e) {
      if (mounted) showSnack(context, 'Print Failed: $e');
    }
  }
""",
        1,
    )

# Pass onPrint into the table toolbar.
s = s.replace(
    """              onRefresh: refresh,
              onAdd: widget.onAdd == null ? null : () => widget.onAdd!(context, refresh),""",
    """              onRefresh: refresh,
              onPrint: () => printRows(sorted),
              onAdd: widget.onAdd == null ? null : () => widget.onAdd!(context, refresh),""",
    1,
)

# Add onPrint field to TableToolbar.
s = s.replace(
    """  final VoidCallback onRefresh;
  final VoidCallback? onAdd;""",
    """  final VoidCallback onRefresh;
  final VoidCallback onPrint;
  final VoidCallback? onAdd;""",
    1,
)
s = s.replace(
    """const TableToolbar({super.key, required this.total, required this.showing, required this.hint, required this.addLabel, required this.allowAdd, required this.columns, required this.sortKey, required this.sortAscending, required this.onSearch, required this.onRefresh, required this.onAdd, required this.onSortChanged, required this.onToggleSortDirection});""",
    """const TableToolbar({super.key, required this.total, required this.showing, required this.hint, required this.addLabel, required this.allowAdd, required this.columns, required this.sortKey, required this.sortAscending, required this.onSearch, required this.onRefresh, required this.onPrint, required this.onAdd, required this.onSortChanged, required this.onToggleSortDirection});""",
    1,
)

# Insert Print button inside every CrudTable toolbar.
s = s.replace(
    """              OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh_rounded), label: const Text('Refresh')),
            ];""",
    """              OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh_rounded), label: const Text('Refresh')),
              FilledButton.tonalIcon(onPressed: onPrint, icon: const Icon(Icons.print_rounded), label: const Text('Print')),
            ];""",
    1,
)

# Replace RankingPage with a stateful page that has All / Full-time / Probationary filters.
ranking_block = textwrap.dedent(r'''
class RankingPage extends StatefulWidget {
  const RankingPage({super.key});

  @override
  State<RankingPage> createState() => _RankingPageState();
}

class _RankingPageState extends State<RankingPage> {
  String filter = 'All';

  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final text = '${row['appointment'] ?? ''}'.toLowerCase().replaceAll('_', ' ').replaceAll('-', ' ');
    final isFullTime = text.contains('full') && text.contains('time');
    final isProbationary = text.contains('probationary');
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }

  Future<List<dynamic>> _loadRankings() async {
    final rows = await loadRankings(limit: 5000);
    return rows.where((item) => _matchesRankingFilter(normalizeRow(Map<String, dynamic>.from(item as Map)), filter)).toList();
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Ranking',
        subtitle: 'Manage faculty ranking applications following the Excel ranking summary layout.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                const Text('Filter:', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 12),
                for (final item in const ['All', 'Full-time', 'Probationary']) ...[
                  ChoiceChip(
                    label: Text(item == 'All' ? 'All (Full-time + Probationary)' : item),
                    selected: filter == item,
                    onSelected: (_) => setState(() => filter = item),
                  ),
                  const SizedBox(width: 8),
                ],
              ]),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey(filter),
              load: () => _loadRankings(),
              searchHint: 'Search employee, appointment, rank, salary, or points',
              addLabel: 'Add Ranking',
              reportTitle: 'Ranking Report - ${filter == 'All' ? 'Full-time and Probationary' : filter}',
              columns: const [
                GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
                GridCol('appointment', 'Appointment', flex: 2),
                GridCol('previous_rank_text', 'Previous Rank', flex: 2),
                GridCol('previous_salary', 'Basic Salary', isMoney: true),
                GridCol('applied_rank_text', 'Rank Applied', flex: 2),
                GridCol('applied_salary', 'Basic Salary Adjustment', flex: 2, isMoney: true),
                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
              ],
              onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
              onView: viewRanking,
              onEdit: editRanking,
              showDelete: false,
              onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}
''').strip()
start = s.find('class RankingPage extends StatelessWidget')
end = s.find('\n\nclass GridCol', start)
if start == -1 or end == -1:
    raise SystemExit('RankingPage block not found')
s = s[:start] + ranking_block + s[end:]

p.write_text(s)
