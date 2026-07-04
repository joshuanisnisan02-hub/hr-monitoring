from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text


def find_function_end(source: str, start: int) -> int:
    brace = source.find('{', start)
    if brace < 0:
        raise SystemExit('Could not find opening brace.')
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                while end < len(source) and source[end] in ' \t\r\n':
                    end += 1
                return end
    raise SystemExit('Could not find closing brace.')


def remove_top_level(signature: str) -> None:
    global text
    while True:
        idx = text.find(signature)
        if idx < 0:
            return
        end = find_function_end(text, idx)
        text = text[:idx] + text[end:]

# Remove helper functions from earlier per-tab patch if the user already ran it locally.
for sig in [
    'String evaluationKindTitle(',
    'String evaluationRatingKeyForKind(',
    'String evaluationDescriptionKeyForKind(',
    'double evaluationMaxScore(',
    'String evaluationRatingLabel(',
    'double? evaluationScoreAsDouble(',
    'String evaluationScoreDescription(',
    'String overallEvaluationDescription(',
    'String evaluationScoreDisplay(',
    'Map<String, dynamic> recomputeEvaluationTotals(',
    'Widget evaluationFormulaNote(',
    'Widget evaluationRatingBox(',
    'Future<Map<String, dynamic>?> showEvaluationKindDialog(',
    'Future<Map<String, dynamic>?> showFullEvaluationDialog(',
    'Future<void> viewEvaluation(',
    'Future<void> editEvaluationForKind(',
    'Future<void> editFullEvaluation(',
]:
    remove_top_level(sig)

start = text.find('class EvaluationsPage extends')
end = text.find('class AppointmentPage extends', start)
if start < 0 or end < 0:
    raise SystemExit('Could not find EvaluationsPage block.')

replacement = r'''
class EvaluationsPage extends StatefulWidget {
  const EvaluationsPage({super.key});

  @override
  State<EvaluationsPage> createState() => _EvaluationsPageState();
}

class _EvaluationsPageState extends State<EvaluationsPage> {
  int refreshSeed = 0;

  void refreshEvaluations() => setState(() => refreshSeed++);

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage faculty evaluation records by evaluation type.',
        child: DefaultTabController(
          length: 4,
          child: Column(children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(children: [
                  Expanded(
                    child: Text(
                      'Use one Add Evaluation form to encode Superior, Peer-to-Peer, Self, and Student ratings together.',
                      style: const TextStyle(
                          color: _muted, fontWeight: FontWeight.w700),
                    ),
                  ),
                  FilledButton.icon(
                    onPressed: () =>
                        editFullEvaluation(context, null, refreshEvaluations),
                    icon: const Icon(Icons.add_rounded),
                    label: const Text('Add Evaluation'),
                  ),
                ]),
              ),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerLeft,
              child: SizedBox(
                width: 720,
                child: TabBar(
                  isScrollable: true,
                  tabs: const [
                    Tab(text: 'Superior'),
                    Tab(text: 'Peer-to-Peer'),
                    Tab(text: 'Self'),
                    Tab(text: 'Student'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: TabBarView(children: [
                EvaluationTab(
                  key: ValueKey('superior-$refreshSeed'),
                  title: 'Superior Evaluation',
                  ratingKey: 'superior_rating',
                  descriptionKey: 'superior_description',
                  kind: EvaluationKind.superior,
                ),
                EvaluationTab(
                  key: ValueKey('peer-$refreshSeed'),
                  title: 'Peer-to-Peer Evaluation',
                  ratingKey: 'peer_rating',
                  descriptionKey: 'peer_description',
                  kind: EvaluationKind.peer,
                ),
                EvaluationTab(
                  key: ValueKey('self-$refreshSeed'),
                  title: 'Self Evaluation',
                  ratingKey: 'self_rating',
                  descriptionKey: 'self_description',
                  kind: EvaluationKind.self,
                ),
                EvaluationTab(
                  key: ValueKey('student-$refreshSeed'),
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
    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] =
          evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).toList();

    normalized.sort((a, b) => formatValue(a['employee_name'])
        .compareTo(formatValue(b['employee_name'])));

    final seen = <String>{};
    final unique = <Map<String, dynamic>>[];
    for (final row in normalized) {
      final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}'
          .trim()
          .toLowerCase();
      if (key.isEmpty || !seen.add(key)) continue;
      unique.add(row);
    }
    return unique;
  }

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => _loadRows(),
        searchHint: 'Search employee, rating, or description',
        addLabel: 'Add Evaluation',
        allowAdd: false,
        reportTitle: '$title Report',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('evaluation_rating', 'Rating', isNumber: true),
          GridCol('evaluation_description', 'Description', flex: 2),
        ],
        onView: viewEvaluation,
        onEdit: editFullEvaluation,
        onDelete: (row) =>
            db.from('evaluation_records').delete().eq('id', row['id']),
      );
}

String evaluationDescription(Map<String, dynamic> row, EvaluationKind kind,
    String ratingKey, String descriptionKey) {
  final saved = formatValueRaw(row[descriptionKey]).trim();
  if (saved.isNotEmpty && saved != '-') return saved.toUpperCase();
  return evaluationScoreDescription(kind, row[ratingKey]).toUpperCase();
}

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
          'Total Rating = average of all converted category percentages. Superior and Peer are already out of 100. Self and Student are converted to percent by multiplying by 20. Overall Description is based on the 100-point total.',
          style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w700),
        ),
      ),
    );

Widget evaluationRatingBox(
  EvaluationKind kind,
  TextEditingController rating,
  TextEditingController description,
  VoidCallback recompute,
  StateSetter setDialogState,
) {
  final maxScore = evaluationMaxScore(kind);
  return Wrap(spacing: 14, runSpacing: 14, children: [
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: rating,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText:
              '${evaluationKindTitle(kind)} Rating (out of ${maxScore.toStringAsFixed(0)})',
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
        onChanged: (_) => setDialogState(recompute),
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
  ]);
}

Future<Map<String, dynamic>?> showFullEvaluationDialog(
    BuildContext context, Map<String, dynamic>? row, List<EditOption> employees) async {
  final isAdd = row == null;
  final initial = normalizeRow(row ?? {});
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial['employee_id']?.toString();
  final superior = TextEditingController(text: formatEditValue(initial['superior_rating']));
  final superiorDesc = TextEditingController(text: formatEditValue(initial['superior_description']));
  final peer = TextEditingController(text: formatEditValue(initial['peer_rating']));
  final peerDesc = TextEditingController(text: formatEditValue(initial['peer_description']));
  final selfRating = TextEditingController(text: formatEditValue(initial['self_rating']));
  final selfDesc = TextEditingController(text: formatEditValue(initial['self_description']));
  final student = TextEditingController(text: formatEditValue(initial['student_rating']));
  final studentDesc = TextEditingController(text: formatEditValue(initial['student_description']));
  final total = TextEditingController(text: formatEditValue(initial['total_rating']));
  final overall = TextEditingController(text: formatEditValue(initial['total_description']));

  void recomputeAll() {
    superiorDesc.text = evaluationScoreDescription(EvaluationKind.superior, superior.text);
    peerDesc.text = evaluationScoreDescription(EvaluationKind.peer, peer.text);
    selfDesc.text = evaluationScoreDescription(EvaluationKind.self, selfRating.text);
    studentDesc.text = evaluationScoreDescription(EvaluationKind.student, student.text);
    final computed = recomputeEvaluationTotals({
      'superior_rating': superior.text,
      'peer_rating': peer.text,
      'self_rating': selfRating.text,
      'student_rating': student.text,
    });
    total.text = evaluationScoreDisplay(computed['total_rating']);
    overall.text = formatValue(computed['total_description']);
  }

  recomputeAll();

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Evaluation' : 'Edit Evaluation'),
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
                  ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                const SizedBox(height: 16),
                const DialogSectionTitle('Superior Evaluation'),
                evaluationRatingBox(EvaluationKind.superior, superior, superiorDesc,
                    recomputeAll, setDialogState),
                const SizedBox(height: 16),
                const DialogSectionTitle('Peer-to-Peer Evaluation'),
                evaluationRatingBox(
                    EvaluationKind.peer, peer, peerDesc, recomputeAll, setDialogState),
                const SizedBox(height: 16),
                const DialogSectionTitle('Self Evaluation'),
                evaluationRatingBox(EvaluationKind.self, selfRating, selfDesc,
                    recomputeAll, setDialogState),
                const SizedBox(height: 16),
                const DialogSectionTitle('Student Evaluation'),
                evaluationRatingBox(EvaluationKind.student, student, studentDesc,
                    recomputeAll, setDialogState),
                const SizedBox(height: 16),
                const DialogSectionTitle('Total / Overall'),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: total,
                      readOnly: true,
                      decoration: const InputDecoration(labelText: 'Total Rating (out of 100)'),
                    ),
                  ),
                  SizedBox(
                    width: 354,
                    child: TextFormField(
                      controller: overall,
                      readOnly: true,
                      decoration: const InputDecoration(labelText: 'Overall Description'),
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
              recomputeAll();
              if (!formKey.currentState!.validate()) return;
              final out = <String, dynamic>{
                if (isAdd) 'employee_id': employeeId,
                'superior_rating': double.tryParse(superior.text.trim()),
                'superior_description': superiorDesc.text.trim(),
                'peer_rating': double.tryParse(peer.text.trim()),
                'peer_description': peerDesc.text.trim(),
                'self_rating': double.tryParse(selfRating.text.trim()),
                'self_description': selfDesc.text.trim(),
                'student_rating': double.tryParse(student.text.trim()),
                'student_description': studentDesc.text.trim(),
                'total_rating': double.tryParse(total.text.trim()),
                'total_description': overall.text.trim(),
              }..removeWhere((_, value) => value == null || value.toString().trim().isEmpty);
              Navigator.pop(context, out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final controller in [
    superior,
    superiorDesc,
    peer,
    peerDesc,
    selfRating,
    selfDesc,
    student,
    studentDesc,
    total,
    overall,
  ]) {
    controller.dispose();
  }
  return result;
}

Future<void> viewEvaluation(BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final computed = recomputeEvaluationTotals(normalized);
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
              DetailTile('Total Rating / 100', evaluationScoreDisplay(computed['total_rating'])),
              DetailTile('Overall Description', formatValue(computed['total_description'])),
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

Future<void> editFullEvaluation(
    BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showFullEvaluationDialog(
      context, row, isAdd ? await employeeOptions() : const <EditOption>[]);
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
        await db.from('evaluation_records').update(merged).eq('id', existing['id']);
      } else {
        await db.from('evaluation_records').insert(recomputeEvaluationTotals(data));
      }
    } else {
      final merged = recomputeEvaluationTotals({...normalizeRow(row), ...data});
      merged.remove('id');
      await db.from('evaluation_records').update(merged).eq('id', row['id']);
    }
    refresh();
    if (context.mounted) showSnack(context, 'Evaluation saved.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Evaluation Failed: $e');
  }
}

'''

text = text[:start] + replacement + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied single whole Add Evaluation button and disabled per-tab add buttons.')
