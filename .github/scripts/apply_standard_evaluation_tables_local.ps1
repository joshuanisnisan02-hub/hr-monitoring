$ErrorActionPreference = 'Stop'

$mainDart = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$text = [System.IO.File]::ReadAllText($mainDart)
$original = $text

$pattern = 'class EvaluationTypeTable extends StatelessWidget \{[\s\S]*?\r?\n\}\s*class AppointmentPage extends'
$replacement = @'
class EvaluationTypeTable extends StatefulWidget {
  final List<Map<String, dynamic>> rows;
  final String title;
  final String reportPeriod;
  final String ratingKey;
  final String descriptionKey;
  final EvaluationType type;
  final void Function(Map<String, dynamic> row) onEdit;
  final Future<void> Function(Map<String, dynamic> row) onDelete;

  const EvaluationTypeTable({
    super.key,
    required this.rows,
    required this.title,
    required this.reportPeriod,
    required this.ratingKey,
    required this.descriptionKey,
    required this.type,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  State<EvaluationTypeTable> createState() => _EvaluationTypeTableState();
}

class _EvaluationTypeTableState extends State<EvaluationTypeTable> {
  String sortKey = 'employee_name';
  bool sortAscending = true;

  static const double actionWidth = 112;

  List<GridCol> get columns => [
        const GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
        const GridCol('academic_year', 'A.Y.'),
        const GridCol('semester', 'Semester'),
        const GridCol('_evaluation_rating', 'Rating', isNumber: true),
        const GridCol('_evaluation_description', 'Description', flex: 2),
      ];

  String _description(Map<String, dynamic> row) {
    final existing = formatValueRaw(row[widget.descriptionKey]).trim();
    if (existing.isNotEmpty && existing != '-') return existing.toUpperCase();
    final rating = num.tryParse('${row[widget.ratingKey] ?? ''}');
    if (rating == null) {
      if (widget.type == EvaluationType.student) return 'FAILED';
      if (widget.type == EvaluationType.self) return 'UNSATISFACTORY';
      return 'UNACCEPTABLE';
    }
    switch (widget.type) {
      case EvaluationType.self:
        if (rating >= 4.5) return 'OUTSTANDING';
        if (rating >= 4.0) return 'VERY SATISFACTORY';
        if (rating >= 3.0) return 'SATISFACTORY';
        return 'UNSATISFACTORY';
      case EvaluationType.student:
        if (rating >= 4.2) return 'EXCELLENT';
        if (rating >= 3.4) return 'GOOD';
        if (rating >= 2.6) return 'FAIR';
        return 'FAILED';
      case EvaluationType.superior:
      case EvaluationType.peer:
        if (rating >= 85) return 'EXCEEDS EXPECTATION';
        if (rating >= 75) return 'MEETS EXPECTATION';
        return 'UNACCEPTABLE';
    }
  }

  List<Map<String, dynamic>> _tableRows() => widget.rows.map((row) {
        final out = Map<String, dynamic>.from(row);
        out['_evaluation_rating'] = row[widget.ratingKey];
        out['_evaluation_description'] = _description(row);
        return out;
      }).toList();

  Future<void> _confirmDelete(BuildContext context, Map<String, dynamic> row) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Delete Evaluation?'),
        content: Text('This will remove the evaluation record for ${formatValue(row['employee_name'])}.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton.tonal(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
        ],
      ),
    );
    if (ok != true) return;
    await widget.onDelete(row);
  }

  @override
  Widget build(BuildContext context) {
    final tableRows = _tableRows()..sort((a, b) => compareRows(a, b, sortKey, sortAscending));
    if (tableRows.isEmpty) return const EmptyBox();
    return Card(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: Column(children: [
          TableHeader(
            columns: columns,
            sortKey: sortKey,
            sortAscending: sortAscending,
            showActions: true,
            actionWidth: actionWidth,
            onSort: (key) => setState(() {
              if (sortKey == key) {
                sortAscending = !sortAscending;
              } else {
                sortKey = key;
                sortAscending = true;
              }
            }),
          ),
          const Divider(height: 1, color: _line),
          Expanded(
            child: ListView.separated(
              itemCount: tableRows.length,
              separatorBuilder: (_, __) => const Divider(height: 1, color: _line),
              itemBuilder: (_, i) => TableRowItem(
                row: tableRows[i],
                columns: columns,
                index: i,
                actionWidth: actionWidth,
                onEdit: () => widget.onEdit(tableRows[i]),
                onDelete: () => _confirmDelete(context, tableRows[i]),
              ),
            ),
          ),
        ]),
      ),
    );
  }
}

class AppointmentPage extends
'@

$text = [System.Text.RegularExpressions.Regex]::Replace($text, $pattern, $replacement, 1)

if ($text -ne $original) {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($mainDart, $text, $utf8NoBom)
  Write-Host 'Applied standard evaluation table styling to lib/main.dart.'
} else {
  Write-Host 'No changes applied. Evaluation table block was not found or already updated.'
}
