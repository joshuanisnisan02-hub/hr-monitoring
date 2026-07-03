$ErrorActionPreference = 'Stop'

$mainDart = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$text = [System.IO.File]::ReadAllText($mainDart)
$original = $text

# Remove A.Y. and Semester from the Evaluation tab table only.
$text = $text.Replace(@'
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('academic_year', 'A.Y.'),
          GridCol('semester', 'Semester'),
          GridCol('evaluation_rating', 'Rating', isNumber: true),
          GridCol('evaluation_description', 'Description', flex: 2),
'@, @'
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('evaluation_rating', 'Rating', isNumber: true),
          GridCol('evaluation_description', 'Description', flex: 2),
'@)

# Replace the EvaluationTab loader so each employee appears only once per tab.
$oldLoader = @'
  Future<List<dynamic>> _loadRows() async {
    final rows = await activeOnlyRows(loadEvaluations(limit: 5000));
    return rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] = evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).toList();
  }
'@

$newLoader = @'
  Future<List<dynamic>> _loadRows() async {
    final rows = await activeOnlyRows(loadEvaluations(limit: 5000));
    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] = evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).toList();

    normalized.sort((a, b) {
      final ay = formatValue(b['academic_year']).compareTo(formatValue(a['academic_year']));
      if (ay != 0) return ay;
      final semester = formatValue(b['semester']).compareTo(formatValue(a['semester']));
      if (semester != 0) return semester;
      return formatValue(a['employee_name']).compareTo(formatValue(b['employee_name']));
    });

    final seen = <String>{};
    final unique = <Map<String, dynamic>>[];
    for (final row in normalized) {
      final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}'.trim().toLowerCase();
      if (key.isEmpty || !seen.add(key)) continue;
      unique.add(row);
    }
    return unique;
  }
'@

$text = $text.Replace($oldLoader, $newLoader)

# Make the duplicate prevention message clearer for Evaluation records.
$text = $text.Replace(
  "context, 'evaluation_records', data['employee_id'], 'evaluation'))",
  "context, 'evaluation_records', data['employee_id'], 'evaluation. This employee already has an evaluation record'))"
)

if ($text -eq $original) {
  Write-Host 'No changes applied. Make sure apply_evaluation_tabs_current_ui_local.ps1 has already been applied.'
  exit 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mainDart, $text, $utf8NoBom)
Write-Host 'Removed A.Y./Semester columns and made Evaluation tab employees unique.'
