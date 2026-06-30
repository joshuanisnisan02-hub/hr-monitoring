from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Add optional approve action to CrudTable.
s = s.replace(
    """  final ViewHandler? onView;
  final bool showDelete;
  final String? reportTitle;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, this.allowAdd = true, required this.columns, this.onAdd, required this.onEdit, this.onView, this.showDelete = true, this.reportTitle, required this.onDelete});""",
    """  final ViewHandler? onView;
  final EditHandler? onApprove;
  final bool showDelete;
  final String? reportTitle;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, this.allowAdd = true, required this.columns, this.onAdd, required this.onEdit, this.onView, this.onApprove, this.showDelete = true, this.reportTitle, required this.onDelete});""",
    1,
)

# Add action width helper.
if 'double get actionWidth' not in s:
    s = s.replace(
        """  void printRows(List<Map<String, dynamic>> rows) {
    final baseTitle = widget.reportTitle ?? (widget.addLabel.toLowerCase().startsWith('add ') ? '${widget.addLabel.substring(4)} Report' : '${widget.addLabel} Report');""",
        """  double get actionWidth {
    var count = 1; // Edit button
    if (widget.onView != null) count++;
    if (widget.onApprove != null) count++;
    if (widget.showDelete) count++;
    return (count * 46).toDouble();
  }

  void printRows(List<Map<String, dynamic>> rows) {
    final baseTitle = widget.reportTitle ?? (widget.addLabel.toLowerCase().startsWith('add ') ? '${widget.addLabel.substring(4)} Report' : '${widget.addLabel} Report');""",
        1,
    )

# Use actionWidth helper in table header and row.
s = s.replace("actionWidth: widget.onView == null ? (widget.showDelete ? 96 : 52) : (widget.showDelete ? 142 : 100)", "actionWidth: actionWidth")
s = s.replace("actionWidth: widget.onView == null ? (widget.showDelete ? 96 : 52) : (widget.showDelete ? 142 : 100),", "actionWidth: actionWidth,")

# Pass approve callback to rows.
s = s.replace(
    """                  onView: widget.onView == null ? null : () => widget.onView!(context, rows[i]),
                  onEdit: () => widget.onEdit(context, rows[i], refresh),
                  onDelete: widget.showDelete ? () => confirmDelete(context, rows[i]) : null,""",
    """                  onView: widget.onView == null ? null : () => widget.onView!(context, rows[i]),
                  onEdit: () => widget.onEdit(context, rows[i], refresh),
                  onApprove: widget.onApprove == null ? null : () => widget.onApprove!(context, rows[i], refresh),
                  onDelete: widget.showDelete ? () => confirmDelete(context, rows[i]) : null,""",
    1,
)

# Add approve to TableRowItem.
s = s.replace(
    """  final VoidCallback? onView;
  final VoidCallback onEdit;
  final VoidCallback? onDelete;

  const TableRowItem({super.key, required this.row, required this.columns, required this.index, required this.actionWidth, this.onView, required this.onEdit, this.onDelete});""",
    """  final VoidCallback? onView;
  final VoidCallback onEdit;
  final VoidCallback? onApprove;
  final VoidCallback? onDelete;

  const TableRowItem({super.key, required this.row, required this.columns, required this.index, required this.actionWidth, this.onView, required this.onEdit, this.onApprove, this.onDelete});""",
    1,
)
s = s.replace(
    """              if (onView != null) IconButton(tooltip: 'View', onPressed: onView, icon: const Icon(Icons.visibility_rounded, color: Color(0xFF0E7490), size: 20)),
              IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_rounded, color: _primary, size: 20)),
              if (onDelete != null) IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline_rounded, color: _danger, size: 20)),""",
    """              if (onView != null) IconButton(tooltip: 'View', onPressed: onView, icon: const Icon(Icons.visibility_rounded, color: Color(0xFF0E7490), size: 20)),
              IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_rounded, color: _primary, size: 20)),
              if (onApprove != null) IconButton(tooltip: 'Approve Applied Rank', onPressed: onApprove, icon: const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 20)),
              if (onDelete != null) IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline_rounded, color: _danger, size: 20)),""",
    1,
)

# Add approve callback to Ranking table only.
s = s.replace(
    """              onView: viewRanking,
              onEdit: editRanking,
              showDelete: false,""",
    """              onView: viewRanking,
              onEdit: editRanking,
              onApprove: approveRanking,
              showDelete: false,""",
    1,
)

# Add approveRanking function before editRanking.
if 'Future<void> approveRanking(BuildContext context, Map<String, dynamic> row, VoidCallback refresh)' not in s:
    approve_fn = """
Future<void> approveRanking(BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final appliedRank = emptyToNull(row['applied_rank_text']);
  final appliedSalary = row['applied_salary'];
  if (appliedRank == null && appliedSalary == null) {
    showSnack(context, 'No applied rank to approve.');
    return;
  }
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Approve Applied Rank?'),
      content: Text('This will approve ${formatValue(row['applied_rank_text'])} for ${formatValue(valueFor(row, 'employee_name'))}.'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Approve')),
      ],
    ),
  );
  if (ok != true) return;
  try {
    await db.from('ranking_applications').update({
      'approved_rank_text': row['applied_rank_text'],
      'approved_salary': row['applied_salary'],
      'updated_at': DateTime.now().toIso8601String(),
    }).eq('id', row['id']);
    showSnack(context, 'Applied rank approved.');
    refresh();
  } catch (e) {
    showSnack(context, 'Approval failed: $e');
  }
}

"""
    s = s.replace("Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {", approve_fn + "Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {", 1)

# Remove approved fields from Add/Edit Ranking modal.
s = s.replace("""  final approvedRank = TextEditingController(text: formatEditValue(initial?['approved_rank_text']));
  final approvedSalary = TextEditingController(text: formatMoneyEdit(initial?['approved_salary']));
""", "", 1)
s = s.replace("""                rankTextBox('Approved Rank', approvedRank, () => pickRank(approvedRank, approvedSalary)),
                textBox('Approved Salary', approvedSalary, kind: FieldKind.number),
""", "", 1)
s = s.replace("""                'approved_rank_text': emptyToNull(approvedRank.text),
                'approved_salary': parseMoneyInput(approvedSalary.text),
""", "", 1)
s = s.replace("""  for (final c in [appointment, previousRank, previousSalary, appliedRank, appliedSalary, points, approvedRank, approvedSalary]) {""", """  for (final c in [appointment, previousRank, previousSalary, appliedRank, appliedSalary, points]) {""", 1)
s = s.replace(
    """Employee name is locked here. Type ranks manually or use Pick to auto-fill salary.""",
    """Employee name is locked here. Use the table Approve button to approve the applied rank.""",
    1,
)

p.write_text(s)
