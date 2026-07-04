from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text


def replace_between(start: str, end: str, replacement: str) -> None:
    global text
    a = text.find(start)
    if a < 0:
        raise SystemExit(f'Missing start marker: {start}')
    b = text.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f'Missing end marker: {end}')
    text = text[:a] + replacement + text[b:]


def insert_before(marker: str, value: str) -> None:
    global text
    if value.strip().split('\n')[0] in text:
        return
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f'Missing insert marker: {marker}')
    text = text[:idx] + value + text[idx:]

# -----------------------------------------------------------------------------
# Evaluation tab actions: add section-specific add/edit + view button.
# -----------------------------------------------------------------------------
text = text.replace(
    "searchHint:\n            'Search employee, academic year, semester, rating, or description',",
    "searchHint: 'Search employee, rating, or description',",
)
text = text.replace(
    """        onAdd: (ctx, refresh) => editEvaluation(ctx, null, refresh),
        onEdit: editEvaluation,""",
    """        onAdd: (ctx, refresh) => editEvaluationForKind(ctx, null, refresh, kind),
        onView: viewEvaluation,
        onEdit: (ctx, row, refresh) => editEvaluationForKind(ctx, row, refresh, kind),""",
    1,
)

# Make the tab sort independent of removed AY/Semester fields.
old_sort = r'''    normalized.sort((a, b) {
      final ay = formatValue(b['academic_year'])
          .compareTo(formatValue(a['academic_year']));
      if (ay != 0) return ay;
      final semester =
          formatValue(b['semester']).compareTo(formatValue(a['semester']));
      if (semester != 0) return semester;
      return formatValue(a['employee_name'])
          .compareTo(formatValue(b['employee_name']));
    });'''
new_sort = r'''    normalized.sort((a, b) => formatValue(a['employee_name'])
        .compareTo(formatValue(b['employee_name'])));'''
text = text.replace(old_sort, new_sort, 1)

# -----------------------------------------------------------------------------
# Add helper functions and custom section modal before the old editEvaluation.
# -----------------------------------------------------------------------------
helpers = r'''
String evaluationKindTitle(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 'Superior Evaluation',
      EvaluationKind.peer => 'Peer-to-Peer Evaluation',
      EvaluationKind.self => 'Self Evaluation',
      EvaluationKind.student => 'Student Evaluation',
    };

String evaluationRatingKeyForKind(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 'superior_rating',
      EvaluationKind.peer => 'peer_rating',
      EvaluationKind.self => 'self_rating',
      EvaluationKind.student => 'student_rating',
    };

String evaluationDescriptionKeyForKind(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 'superior_description',
      EvaluationKind.peer => 'peer_description',
      EvaluationKind.self => 'self_description',
      EvaluationKind.student => 'student_description',
    };

double evaluationMaxScore(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 100,
      EvaluationKind.peer => 100,
      EvaluationKind.self => 5,
      EvaluationKind.student => 5,
    };

String evaluationRatingLabel(EvaluationKind kind) =>
    '${evaluationKindTitle(kind)} Rating (out of ${evaluationMaxScore(kind).toStringAsFixed(0)})';

double? evaluationScoreAsDouble(Object? value) {
  final text = formatValue(value).replaceAll(',', '').trim();
  if (text.isEmpty || text == '-') return null;
  return double.tryParse(text);
}

String evaluationScoreDescription(EvaluationKind kind, Object? value) {
  final score = evaluationScoreAsDouble(value);
  if (score == null) return '';
  switch (kind) {
    case EvaluationKind.superior:
    case EvaluationKind.peer:
      if (score >= 85) return 'EXCEEDS EXPECTATION';
      if (score >= 75) return 'MEETS EXPECTATION';
      return 'UNACCEPTABLE';
    case EvaluationKind.self:
      if (score >= 4.50) return 'OUTSTANDING';
      if (score >= 4.00) return 'VERY SATISFACTORY';
      if (score >= 3.00) return 'SATISFACTORY';
      return 'UNSATISFACTORY';
    case EvaluationKind.student:
      if (score >= 4.25) return 'EXCELLENT';
      if (score >= 3.75) return 'GOOD';
      if (score >= 3.00) return 'SATISFACTORY';
      return 'NEEDS IMPROVEMENT';
  }
}

String overallEvaluationDescription(Object? value) {
  final score = evaluationScoreAsDouble(value);
  if (score == null) return '';
  if (score >= 85) return 'EXCEEDS EXPECTATION';
  if (score >= 75) return 'MEETS EXPECTATION';
  return 'UNACCEPTABLE';
}

String evaluationScoreDisplay(Object? value) {
  final score = evaluationScoreAsDouble(value);
  if (score == null) return '-';
  final fixed = score.toStringAsFixed(2);
  return fixed.replaceFirst(RegExp(r'\.00$'), '').replaceFirst(RegExp(r'0$'), '');
}

Map<String, dynamic> recomputeEvaluationTotals(Map<String, dynamic> row) {
  final data = Map<String, dynamic>.from(row);
  final parts = <double>[];
  void addPart(String key, double max) {
    final score = evaluationScoreAsDouble(data[key]);
    if (score != null) parts.add((score / max) * 100);
  }

  addPart('superior_rating', 100);
  addPart('peer_rating', 100);
  addPart('self_rating', 5);
  addPart('student_rating', 5);

  if (parts.isNotEmpty) {
    final total = parts.reduce((a, b) => a + b) / parts.length;
    data['total_rating'] = double.parse(total.toStringAsFixed(2));
    data['total_description'] = overallEvaluationDescription(total);
  }
  return data;
}

Widget evaluationFormulaNote() => SizedBox(
      width: 728,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
            color: const Color(0xFFEFF6FF),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFBFDBFE))),
        child: const Text(
          'Suggested total: convert each category to percent, then average them. Formula: Superior% + Peer% + Self x 20 + Student x 20, divided by the number of available categories. Overall description uses the 100-point result.',
          style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w700),
        ),
      ),
    );

Future<Map<String, dynamic>?> showEvaluationKindDialog(
    BuildContext context,
    Map<String, dynamic>? row,
    List<EditOption> employees,
    EvaluationKind kind) async {
  final isAdd = row == null;
  final formKey = GlobalKey<FormState>();
  final ratingKey = evaluationRatingKeyForKind(kind);
  final descriptionKey = evaluationDescriptionKeyForKind(kind);
  final maxScore = evaluationMaxScore(kind);
  String? employeeId = isAdd ? null : row?['employee_id']?.toString();
  final rating = TextEditingController(text: formatEditValue(row?[ratingKey]));
  final description = TextEditingController(
      text: formatEditValue(row?[descriptionKey]).isEmpty
          ? evaluationScoreDescription(kind, row?[ratingKey])
          : formatEditValue(row?[descriptionKey]));

  void recomputeDescription() {
    description.text = evaluationScoreDescription(kind, rating.text);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add ${evaluationKindTitle(kind)}' : 'Edit ${evaluationKindTitle(kind)}'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                if (isAdd)
                  employeeAutocompleteField(
                    employees: employees,
                    employeeId: employeeId,
                    width: 728,
                    onEmployeeChanged: (value) =>
                        setDialogState(() => employeeId = value),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(row)),
                const SizedBox(height: 16),
                DialogSectionTitle(evaluationKindTitle(kind)),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: rating,
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                      decoration: InputDecoration(
                        labelText: evaluationRatingLabel(kind),
                        helperText: 'Maximum score: ${maxScore.toStringAsFixed(0)}',
                      ),
                      validator: (value) {
                        final score = double.tryParse('${value ?? ''}'.trim());
                        if (score == null) return 'Required';
                        if (score < 0 || score > maxScore) {
                          return 'Enter 0 to ${maxScore.toStringAsFixed(0)}';
                        }
                        return null;
                      },
                      onChanged: (_) => setDialogState(recomputeDescription),
                    ),
                  ),
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: description,
                      readOnly: true,
                      decoration: const InputDecoration(
                        labelText: 'Description',
                        suffixIcon: Icon(Icons.auto_fix_high_rounded),
                      ),
                      validator: (value) => value == null || value.trim().isEmpty
                          ? 'Enter a valid rating first'
                          : null,
                    ),
                  ),
                ]),
                const SizedBox(height: 16),
                evaluationFormulaNote(),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              recomputeDescription();
              if (!formKey.currentState!.validate()) return;
              final out = <String, dynamic>{
                if (isAdd) 'employee_id': employeeId,
                ratingKey: double.tryParse(rating.text.trim()),
                descriptionKey: description.text.trim(),
              }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty);
              Navigator.pop(context, out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  rating.dispose();
  description.dispose();
  return result;
}

Future<void> viewEvaluation(BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final total = recomputeEvaluationTotals(normalized);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Evaluation Details - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 850,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Wrap(spacing: 10, runSpacing: 10, children: [
              DetailTile('Employee Name', formatValue(normalized['employee_name'])),
              DetailTile('Superior Rating / 100', evaluationScoreDisplay(normalized['superior_rating'])),
              DetailTile('Superior Description', evaluationScoreDescription(EvaluationKind.superior, normalized['superior_rating'])),
              DetailTile('Peer-to-Peer Rating / 100', evaluationScoreDisplay(normalized['peer_rating'])),
              DetailTile('Peer-to-Peer Description', evaluationScoreDescription(EvaluationKind.peer, normalized['peer_rating'])),
              DetailTile('Self Rating / 5', evaluationScoreDisplay(normalized['self_rating'])),
              DetailTile('Self Description', evaluationScoreDescription(EvaluationKind.self, normalized['self_rating'])),
              DetailTile('Student Rating / 5', evaluationScoreDisplay(normalized['student_rating'])),
              DetailTile('Student Description', evaluationScoreDescription(EvaluationKind.student, normalized['student_rating'])),
              DetailTile('Total Rating / 100', evaluationScoreDisplay(total['total_rating'])),
              DetailTile('Overall Description', formatValue(total['total_description'])),
            ]),
            const SizedBox(height: 14),
            evaluationFormulaNote(),
          ]),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
      ],
    ),
  );
}

Future<void> editEvaluationForKind(BuildContext context,
    Map<String, dynamic>? row, VoidCallback refresh, EvaluationKind kind) async {
  final isAdd = row == null;
  final data = await showEvaluationKindDialog(
      context, row == null ? null : normalizeRow(row),
      isAdd ? await employeeOptions() : const <EditOption>[], kind);
  if (data == null) return;

  try {
    if (isAdd) {
      final employeeId = data['employee_id'];
      final existingRows = await db
          .from('evaluation_records')
          .select()
          .eq('employee_id', employeeId)
          .limit(1);
      if (existingRows is List && existingRows.isNotEmpty) {
        final existing = normalizeRow(Map<String, dynamic>.from(existingRows.first as Map));
        final merged = recomputeEvaluationTotals({...existing, ...data});
        merged.remove('id');
        await db
            .from('evaluation_records')
            .update(merged)
            .eq('id', existing['id']);
      } else {
        final merged = recomputeEvaluationTotals(data);
        await db.from('evaluation_records').insert(merged);
      }
    } else {
      final merged = recomputeEvaluationTotals({...normalizeRow(row), ...data});
      merged.remove('id');
      await db.from('evaluation_records').update(merged).eq('id', row['id']);
    }
    refresh();
    if (context.mounted) showSnack(context, '${evaluationKindTitle(kind)} saved.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Evaluation Failed: $e');
  }
}

'''

if 'Future<void> editEvaluationForKind(' not in text:
    insert_before('Future<void> editEvaluation(', helpers)

# Remove the old all-fields Add/Edit Evaluation function.
if 'Future<void> editEvaluation(BuildContext context, Map<String, dynamic>? row,' in text:
    replace_between('Future<void> editEvaluation(BuildContext context, Map<String, dynamic>? row,',
                    'Future<void> approveRanking(',
                    '')

if text == original:
    print('No changes applied. Evaluation section modal/view patch may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Applied Evaluation per-tab add/edit modal, auto descriptions, total formula, and View button.')
