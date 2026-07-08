from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# 1) Uppercase outgoing data before saving.
# -----------------------------------------------------------------------------
if 'Map<String, dynamic> upperCaseDataMap' not in text:
    helper = r'''
bool shouldUpperCaseDataKey(String key) {
  final k = key.toLowerCase();
  if (k == 'id' || k == 'created_at' || k == 'updated_at') return false;
  if (k.endsWith('_id') || k == 'employee_id' || k == 'cycle_id') return false;
  if (k.contains('url') || k.contains('email')) return false;
  if (k.contains('date') || k == 'expiry_date' || k == 'issued_date') return false;
  return true;
}

dynamic upperCaseDataValue(String key, dynamic value) {
  if (value is String) {
    final clean = value.trim();
    if (clean.isEmpty) return clean;
    return shouldUpperCaseDataKey(key) ? clean.toUpperCase() : clean;
  }
  if (value is Map) {
    return upperCaseDataMap(Map<String, dynamic>.from(value));
  }
  if (value is List) {
    return value
        .map((item) => item is Map
            ? upperCaseDataMap(Map<String, dynamic>.from(item))
            : item)
        .toList();
  }
  return value;
}

Map<String, dynamic> upperCaseDataMap(Map<String, dynamic> data) {
  final out = <String, dynamic>{};
  data.forEach((key, value) {
    out[key] = upperCaseDataValue(key, value);
  });
  return out;
}

'''
    marker = 'final Map<String, List<dynamic>> _crudTableDataCache ='
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('Could not find helper insertion point.')
    text = text[:idx] + helper + text[idx:]

# saveRow: use uppercase map.
text = text.replace(
    """  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from(table).insert(data);
      showSnack(context, 'Record Added.');
    } else {
      await archiveOldContractBeforeUpdate(table, id);
      await db.from(table).update(data).eq('id', id);
      showSnack(context, 'Record Updated.');
    }""",
    """  try {
    final cleanData = upperCaseDataMap(data);
    cleanData.removeWhere((key, value) => key == 'id');
    cleanData['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from(table).insert(cleanData);
      showSnack(context, 'Record Added.');
    } else {
      await archiveOldContractBeforeUpdate(table, id);
      await db.from(table).update(cleanData).eq('id', id);
      showSnack(context, 'Record Updated.');
    }""",
    1,
)

# Credential record saves.
text = text.replace(
    '      final data = Map<String, dynamic>.from(record);\n      final id = data.remove(\'id\');',
    '      final data = upperCaseDataMap(Map<String, dynamic>.from(record));\n      final id = data.remove(\'id\');',
    1,
)

# Add employee full direct inserts.
text = text.replace('.insert(result.employee)', '.insert(upperCaseDataMap(result.employee))')
text = text.replace('...result.contract,', '...upperCaseDataMap(result.contract),')
text = text.replace('{...license, \'employee_id\': employeeId}', '{...upperCaseDataMap(license), \'employee_id\': employeeId}')
text = text.replace('{...certificate, \'employee_id\': employeeId}', '{...upperCaseDataMap(certificate), \'employee_id\': employeeId}')
text = text.replace('{...education, \'employee_id\': employeeId}', '{...upperCaseDataMap(education), \'employee_id\': employeeId}')

# -----------------------------------------------------------------------------
# 2) Load evaluation employee names from employees table and attach latest
#    contract type so part-time rules can be applied.
# -----------------------------------------------------------------------------
old_load = """Future<List<dynamic>> loadEvaluations({int limit = 1500}) => db
    .from('evaluation_records')
    .select(
        'id, employee_id, academic_year, semester, superior_rating, superior_description, peer_rating, peer_description, self_rating, self_description, student_rating, student_description, total_rating, total_description, employees(full_name)')
    .order('academic_year')
    .limit(limit);"""
new_load = r'''Future<List<dynamic>> loadEvaluations({int limit = 1500}) async {
  final rows = await db
      .from('evaluation_records')
      .select(
          'id, employee_id, academic_year, semester, superior_rating, superior_description, peer_rating, peer_description, self_rating, self_description, student_rating, student_description, total_rating, total_description, employees(full_name)')
      .order('academic_year')
      .limit(limit);

  final contractByEmployee = <String, Map<String, dynamic>>{};
  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, contract_type, contract_start_date, id')
        .order('contract_start_date', ascending: false)
        .limit(5000);
    for (final item in contracts) {
      final contract = Map<String, dynamic>.from(item as Map);
      final employeeId = '${contract['employee_id'] ?? ''}'.trim();
      if (employeeId.isEmpty || contractByEmployee.containsKey(employeeId)) continue;
      contractByEmployee[employeeId] = contract;
    }
  } catch (_) {}

  return rows.map((item) {
    final row = Map<String, dynamic>.from(item as Map);
    if (row['employees'] is Map) {
      row['employee_name'] =
          formatValue((row['employees'] as Map)['full_name']).toUpperCase();
    }
    final employeeId = '${row['employee_id'] ?? ''}'.trim();
    final contract = contractByEmployee[employeeId];
    if (contract != null) {
      row['contract_type'] = contract['contract_type'];
      row['latest_contract_type'] = contract['contract_type'];
    }
    return row;
  }).toList();
}

Future<Set<String>> loadLatestPartTimeEmployeeIds() async {
  final ids = <String>{};
  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, contract_type, contract_start_date, id')
        .order('contract_start_date', ascending: false)
        .limit(5000);
    final seen = <String>{};
    for (final item in contracts) {
      final contract = Map<String, dynamic>.from(item as Map);
      final employeeId = '${contract['employee_id'] ?? ''}'.trim();
      if (employeeId.isEmpty || !seen.add(employeeId)) continue;
      if (isPartTimeContractType(contract['contract_type'])) ids.add(employeeId);
    }
  } catch (_) {}
  return ids;
}

bool isPartTimeContractType(Object? value) {
  final text = formatValue(value)
      .toLowerCase()
      .replaceAll('_', '-')
      .replaceAll(RegExp(r'\s+'), '-');
  return text.contains('part-time') || text.contains('parttime');
}

bool isPartTimeEvaluationRow(Map<String, dynamic> row) {
  return isPartTimeContractType(row['contract_type']) ||
      isPartTimeContractType(row['latest_contract_type']) ||
      isPartTimeContractType(row['employee_type']);
}
'''
if old_load in text:
    text = text.replace(old_load, new_load, 1)
elif 'Future<Set<String>> loadLatestPartTimeEmployeeIds()' not in text:
    marker = 'Future<List<dynamic>> loadRankings({int limit = 1500})'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('Could not find loadEvaluations replacement point.')
    text = text[:idx] + new_load + text[idx:]

# -----------------------------------------------------------------------------
# 3) Part-time employees should not have Superior or Peer-to-Peer evaluations.
# -----------------------------------------------------------------------------
# Filter part-time employees out of Superior and Peer tab rows.
text = text.replace(
    """    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] =
          evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).toList();""",
    """    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] =
          evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).where((row) {
      if ((kind == EvaluationKind.superior || kind == EvaluationKind.peer) &&
          isPartTimeEvaluationRow(row)) {
        return false;
      }
      return true;
    }).toList();""",
    1,
)

# Recompute totals without superior/peer for part-time employees.
text = text.replace(
    """Map<String, dynamic> recomputeEvaluationTotals(Map<String, dynamic> row) {
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
}""",
    """Map<String, dynamic> recomputeEvaluationTotals(Map<String, dynamic> row) {
  final data = Map<String, dynamic>.from(row);
  final isPartTime = isPartTimeEvaluationRow(data);
  if (isPartTime) {
    data['superior_rating'] = null;
    data['superior_description'] = null;
    data['peer_rating'] = null;
    data['peer_description'] = null;
  }
  final parts = <double>[];
  void addPart(String key, double max) {
    final score = evaluationScoreAsDouble(data[key]);
    if (score != null) parts.add((score / max) * 100);
  }

  if (!isPartTime) {
    addPart('superior_rating', 100);
    addPart('peer_rating', 100);
  }
  addPart('self_rating', 5);
  addPart('student_rating', 5);

  if (parts.isNotEmpty) {
    final total = parts.reduce((a, b) => a + b) / parts.length;
    data['total_rating'] = double.parse(total.toStringAsFixed(2));
    data['total_description'] = overallEvaluationDescription(total);
  }
  return data;
}""",
    1,
)

# showFullEvaluationDialog: load part-time employees and hide superior/peer.
text = text.replace(
    """  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial['employee_id']?.toString();""",
    """  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial['employee_id']?.toString();
  final partTimeEmployeeIds = await loadLatestPartTimeEmployeeIds();
  bool selectedEmployeeIsPartTime() =>
      employeeId != null && partTimeEmployeeIds.contains(employeeId);""",
    1,
)

text = text.replace(
    """  void recomputeAll() {
    superiorDesc.text =
        evaluationScoreDescription(EvaluationKind.superior, superior.text);
    peerDesc.text = evaluationScoreDescription(EvaluationKind.peer, peer.text);
    selfDesc.text =
        evaluationScoreDescription(EvaluationKind.self, selfRating.text);
    studentDesc.text =
        evaluationScoreDescription(EvaluationKind.student, student.text);
    final computed = recomputeEvaluationTotals({
      'superior_rating': superior.text,
      'peer_rating': peer.text,
      'self_rating': selfRating.text,
      'student_rating': student.text,
    });
    total.text = evaluationScoreDisplay(computed['total_rating']);
    overall.text = formatValue(computed['total_description']);
  }""",
    """  void recomputeAll() {
    final isPartTimeEmployee = selectedEmployeeIsPartTime();
    if (isPartTimeEmployee) {
      superior.clear();
      superiorDesc.clear();
      peer.clear();
      peerDesc.clear();
    } else {
      superiorDesc.text =
          evaluationScoreDescription(EvaluationKind.superior, superior.text);
      peerDesc.text = evaluationScoreDescription(EvaluationKind.peer, peer.text);
    }
    selfDesc.text =
        evaluationScoreDescription(EvaluationKind.self, selfRating.text);
    studentDesc.text =
        evaluationScoreDescription(EvaluationKind.student, student.text);
    final computed = recomputeEvaluationTotals({
      'contract_type': isPartTimeEmployee ? 'PART-TIME' : '',
      'superior_rating': superior.text,
      'peer_rating': peer.text,
      'self_rating': selfRating.text,
      'student_rating': student.text,
    });
    total.text = evaluationScoreDisplay(computed['total_rating']);
    overall.text = formatValue(computed['total_description']);
  }""",
    1,
)

text = text.replace(
    """                        onEmployeeChanged: (value) =>
                            setDialogState(() => employeeId = value),""",
    """                        onEmployeeChanged: (value) => setDialogState(() {
                          employeeId = value;
                          recomputeAll();
                        }),""",
    1,
)

text = text.replace(
    """                    const SizedBox(height: 16),
                    const DialogSectionTitle('Superior Evaluation'),
                    evaluationRatingBox(EvaluationKind.superior, superior,
                        superiorDesc, recomputeAll, setDialogState),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Peer-to-Peer Evaluation'),
                    evaluationRatingBox(EvaluationKind.peer, peer, peerDesc,
                        recomputeAll, setDialogState),
                    const SizedBox(height: 16),""",
    """                    const SizedBox(height: 16),
                    if (selectedEmployeeIsPartTime())
                      Container(
                        width: 728,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: Color(0xFFBFDBFE)),
                        ),
                        child: const Text(
                          'PART-TIME EMPLOYEES USE SELF AND STUDENT EVALUATIONS ONLY.',
                          style: TextStyle(
                              color: Color(0xFF1E3A8A),
                              fontWeight: FontWeight.w900),
                        ),
                      )
                    else ...[
                      const DialogSectionTitle('Superior Evaluation'),
                      evaluationRatingBox(EvaluationKind.superior, superior,
                          superiorDesc, recomputeAll, setDialogState),
                      const SizedBox(height: 16),
                      const DialogSectionTitle('Peer-to-Peer Evaluation'),
                      evaluationRatingBox(EvaluationKind.peer, peer, peerDesc,
                          recomputeAll, setDialogState),
                      const SizedBox(height: 16),
                    ],""",
    1,
)

text = text.replace(
    """              final out = <String, dynamic>{
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
              }..removeWhere((_, value) =>
                  value == null || value.toString().trim().isEmpty);""",
    """              final isPartTimeEmployee = selectedEmployeeIsPartTime();
              final out = <String, dynamic>{
                if (isAdd) 'employee_id': employeeId,
                'contract_type': isPartTimeEmployee ? 'PART-TIME' : null,
                'superior_rating': isPartTimeEmployee
                    ? null
                    : double.tryParse(superior.text.trim()),
                'superior_description':
                    isPartTimeEmployee ? null : superiorDesc.text.trim(),
                'peer_rating':
                    isPartTimeEmployee ? null : double.tryParse(peer.text.trim()),
                'peer_description': isPartTimeEmployee ? null : peerDesc.text.trim(),
                'self_rating': double.tryParse(selfRating.text.trim()),
                'self_description': selfDesc.text.trim(),
                'student_rating': double.tryParse(student.text.trim()),
                'student_description': studentDesc.text.trim(),
                'total_rating': double.tryParse(total.text.trim()),
                'total_description': overall.text.trim(),
              }..removeWhere((_, value) =>
                  value != null && value.toString().trim().isEmpty);""",
    1,
)

# Prevent editing Superior/Peer rows for part-time if somehow reached.
text = text.replace(
    """Future<void> editEvaluationForKind(BuildContext context,
    Map<String, dynamic> row, VoidCallback refresh, EvaluationKind kind) async {
  final data = await showEvaluationKindOnlyDialog(context, row, kind);""",
    """Future<void> editEvaluationForKind(BuildContext context,
    Map<String, dynamic> row, VoidCallback refresh, EvaluationKind kind) async {
  if ((kind == EvaluationKind.superior || kind == EvaluationKind.peer) &&
      isPartTimeEvaluationRow(normalizeRow(row))) {
    showSnack(context,
        'PART-TIME EMPLOYEES DO NOT HAVE SUPERIOR OR PEER-TO-PEER EVALUATION.');
    return;
  }
  final data = await showEvaluationKindOnlyDialog(context, row, kind);""",
    1,
)

# Evaluation direct saves should also uppercase descriptions.
text = text.replace(
    "final merged = recomputeEvaluationTotals({...normalizeRow(row), ...data});",
    "final merged = upperCaseDataMap(recomputeEvaluationTotals({...normalizeRow(row), ...data}));",
)
text = text.replace(
    "final merged = recomputeEvaluationTotals({...existing, ...data});",
    "final merged = upperCaseDataMap(recomputeEvaluationTotals({...existing, ...data}));",
)
text = text.replace(
    ".insert(recomputeEvaluationTotals(data))",
    ".insert(upperCaseDataMap(recomputeEvaluationTotals(data)))",
)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Uppercase and part-time evaluation rules may already be present.')
else:
    print('Applied uppercase saves, employee-fetched evaluation names, and part-time evaluation rules.')
