$ErrorActionPreference = 'Stop'

$mainDart = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$text = [System.IO.File]::ReadAllText($mainDart)
$original = $text

# Make sure individual evaluation description fields are loaded from Supabase.
$loadPattern = "\.select\(\s*'id, employee_id, academic_year, semester, superior_rating, peer_rating, self_rating, student_rating, total_rating, total_description, employees\(full_name\)'\s*\)"
$loadReplacement = ".select('id, employee_id, academic_year, semester, superior_rating, superior_description, peer_rating, peer_description, self_rating, self_description, student_rating, student_description, total_rating, total_description, employees(full_name)')"
$text = [System.Text.RegularExpressions.Regex]::Replace($text, $loadPattern, $loadReplacement, 1)

# Replace only the current restored UI Evaluation page block.
$pagePattern = 'class EvaluationsPage extends StatelessWidget \{[\s\S]*?\r?\n\}\s*class AppointmentPage extends'
$pageReplacement = @'
class EvaluationsPage extends StatelessWidget {
  const EvaluationsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage faculty evaluation records by evaluation type.',
        child: const DefaultTabController(
          length: 4,
          child: Column(children: [
            Align(
              alignment: Alignment.centerLeft,
              child: SizedBox(
                width: 720,
                child: TabBar(
                  isScrollable: true,
                  tabs: [
                    Tab(text: 'Superior'),
                    Tab(text: 'Peer-to-Peer'),
                    Tab(text: 'Self'),
                    Tab(text: 'Student'),
                  ],
                ),
              ),
            ),
            SizedBox(height: 16),
            Expanded(
              child: TabBarView(children: [
                EvaluationTab(
                  title: 'Superior Evaluation',
                  ratingKey: 'superior_rating',
                  descriptionKey: 'superior_description',
                  kind: EvaluationKind.superior,
                ),
                EvaluationTab(
                  title: 'Peer-to-Peer Evaluation',
                  ratingKey: 'peer_rating',
                  descriptionKey: 'peer_description',
                  kind: EvaluationKind.peer,
                ),
                EvaluationTab(
                  title: 'Self Evaluation',
                  ratingKey: 'self_rating',
                  descriptionKey: 'self_description',
                  kind: EvaluationKind.self,
                ),
                EvaluationTab(
                  title: 'Student Evaluation',
                  ratingKey: 'student_rating',
                  descriptionKey: 'student_description',
                  kind: EvaluationKind.student,
                ),
              ]),
            ),
          ]),
        ),
      );
}

enum EvaluationKind { superior, peer, self, student }

class EvaluationTab extends StatelessWidget {
  final String title;
  final String ratingKey;
  final String descriptionKey;
  final EvaluationKind kind;

  const EvaluationTab({
    super.key,
    required this.title,
    required this.ratingKey,
    required this.descriptionKey,
    required this.kind,
  });

  Future<List<dynamic>> _loadRows() async {
    final rows = await activeOnlyRows(loadEvaluations(limit: 5000));
    return rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] = evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).toList();
  }

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => _loadRows(),
        searchHint: 'Search employee, academic year, semester, rating, or description',
        addLabel: 'Add Evaluation',
        reportTitle: '$title Report',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('academic_year', 'A.Y.'),
          GridCol('semester', 'Semester'),
          GridCol('evaluation_rating', 'Rating', isNumber: true),
          GridCol('evaluation_description', 'Description', flex: 2),
        ],
        onAdd: (ctx, refresh) => editEvaluation(ctx, null, refresh),
        onEdit: editEvaluation,
        onDelete: (row) => db.from('evaluation_records').delete().eq('id', row['id']),
      );
}

String evaluationDescription(Map<String, dynamic> row, EvaluationKind kind, String ratingKey, String descriptionKey) {
  final saved = formatValueRaw(row[descriptionKey]).trim();
  if (saved.isNotEmpty && saved != '-') return saved.toUpperCase();

  final total = formatValueRaw(row['total_description']).trim();
  if ((kind == EvaluationKind.student || kind == EvaluationKind.self) && total.isNotEmpty && total != '-') {
    return total.toUpperCase();
  }

  final rating = num.tryParse('${row[ratingKey] ?? ''}'.replaceAll(',', '').trim());
  if (rating == null) {
    if (kind == EvaluationKind.student) return 'FAILED';
    if (kind == EvaluationKind.self) return 'UNSATISFACTORY';
    return 'UNACCEPTABLE';
  }

  switch (kind) {
    case EvaluationKind.self:
      if (rating >= 4.5) return 'OUTSTANDING';
      if (rating >= 4.0) return 'VERY SATISFACTORY';
      if (rating >= 3.0) return 'SATISFACTORY';
      return 'UNSATISFACTORY';
    case EvaluationKind.student:
      if (rating >= 4.2) return 'EXCELLENT';
      if (rating >= 3.4) return 'GOOD';
      if (rating >= 2.6) return 'FAIR';
      return 'FAILED';
    case EvaluationKind.superior:
    case EvaluationKind.peer:
      if (rating >= 85) return 'EXCEEDS EXPECTATION';
      if (rating >= 75) return 'MEETS EXPECTATION';
      return 'UNACCEPTABLE';
  }
}

class AppointmentPage extends
'@

$text = [System.Text.RegularExpressions.Regex]::Replace($text, $pagePattern, $pageReplacement, 1)

# Extend Add/Edit Evaluation fields so descriptions can be maintained per tab.
$oldFields = @'
      const EditField('superior_rating', 'Superior Rating',
          kind: FieldKind.number),
      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),
      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),
      const EditField('student_rating', 'Student Rating',
          kind: FieldKind.number),
      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),
      const EditField('total_description', 'Description'),
'@

$newFields = @'
      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),
      const EditField('superior_description', 'Superior Description'),
      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),
      const EditField('peer_description', 'Peer-to-Peer Description'),
      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),
      const EditField('self_description', 'Self Description'),
      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),
      const EditField('student_description', 'Student Description'),
      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),
      const EditField('total_description', 'Overall Description'),
'@

$text = $text.Replace($oldFields, $newFields)

if ($text -eq $original) {
  Write-Host 'No changes applied. The Evaluation module may already be updated or the expected block was not found.'
  exit 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mainDart, $text, $utf8NoBom)
Write-Host 'Applied Evaluation tabs to the current restored UI in lib/main.dart.'
