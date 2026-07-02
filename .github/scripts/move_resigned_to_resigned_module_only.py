from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# ------------------------------------------------------------
# 0) Safety repair from previous broad Align/textAlign patches.
# ------------------------------------------------------------
for name in [
    'textAlign',
    'alignment',
    'mainAxisAlignment',
    'crossAxisAlignment',
    'verticalDirection',
    'textDirection',
    'clipBehavior',
]:
    text = text.replace(f'{name}(', f'{name}:')

text = text.replace('textAlign( TextAlign.', 'textAlign: TextAlign.')
text = text.replace('mainAxisAlignment( MainAxisAlignment.', 'mainAxisAlignment: MainAxisAlignment.')
text = text.replace('crossAxisAlignment( CrossAxisAlignment.', 'crossAxisAlignment: CrossAxisAlignment.')
text = text.replace('alignment( Alignment.', 'alignment: Alignment.')
text = text.replace('Align:\n', 'Align(\n')
text = text.replace('              Align:\n', '              Align(\n')

# ------------------------------------------------------------
# Helper utilities.
# Resigned employees are hidden from all normal modules and dropdowns.
# The Resigned Employees module loads them separately.
# ------------------------------------------------------------
helper_marker = 'Future<List<dynamic>> loadAppointments({int limit = 5000})'
helper_code = r'''
bool isResignedText(Object? value) {
  final text = '${value ?? ''}'.toLowerCase();
  return text.contains('resign');
}

bool rowHasResignedStatus(Map<String, dynamic> row) {
  return isResignedText(row['employment_status']) ||
      isResignedText(row['employee_status']) ||
      isResignedText(row['status']) ||
      isResignedText(row['latest_status']) ||
      isResignedText(row['contract_status']);
}

Future<Set<String>> loadResignedEmployeeIdSet() async {
  final ids = <String>{};

  try {
    final employees = await db
        .from('employees')
        .select('id, employment_status, employee_status, status, latest_status')
        .limit(5000);
    for (final item in employees) {
      final row = Map<String, dynamic>.from(item as Map);
      if (rowHasResignedStatus(row)) ids.add('${row['id']}');
    }
  } catch (_) {}

  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, status')
        .limit(5000);
    for (final item in contracts) {
      final row = Map<String, dynamic>.from(item as Map);
      if (isResignedText(row['status'])) ids.add('${row['employee_id']}');
    }
  } catch (_) {}

  ids.removeWhere((value) => value.trim().isEmpty || value == 'null');
  return ids;
}

String rowEmployeeId(Map<String, dynamic> row) {
  final raw = row['employee_id'] ?? row['id'];
  return '${raw ?? ''}'.trim();
}

Future<List<dynamic>> activeOnlyRows(Future<List<dynamic>> source) async {
  final rows = await source;
  final resignedIds = await loadResignedEmployeeIdSet();
  return rows.where((item) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final id = rowEmployeeId(row);
    if (id.isNotEmpty && resignedIds.contains(id)) return false;
    if (rowHasResignedStatus(row)) return false;
    return true;
  }).toList();
}

Future<List<dynamic>> loadActiveEmployees({int limit = 5000}) =>
    activeOnlyRows(loadEmployees(limit: limit));

Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {
  final resignedIds = await loadResignedEmployeeIdSet();
  final employees = await loadEmployees(limit: limit);
  final rows = employees
      .map((item) => normalizeRow(Map<String, dynamic>.from(item as Map)))
      .where((row) {
    final id = '${row['id'] ?? ''}'.trim();
    return (id.isNotEmpty && resignedIds.contains(id)) || rowHasResignedStatus(row);
  }).toList();
  rows.sort((a, b) => formatValue(a['full_name']).compareTo(formatValue(b['full_name'])));
  return rows;
}

'''
if 'Future<Set<String>> loadResignedEmployeeIdSet()' not in text:
    pos = text.find(helper_marker)
    if pos == -1:
        raise SystemExit('Could not find loader helper insertion point.')
    # Insert before loadAppointments so helpers are close to loaders.
    text = text[:pos] + helper_code + text[pos:]

# If a previous loadResignedEmployees function exists before/after helpers, replace duplicates by keeping the helper version.
first = text.find('Future<List<dynamic>> loadResignedEmployees({int limit = 5000})')
if first != -1:
    second = text.find('Future<List<dynamic>> loadResignedEmployees({int limit = 5000})', first + 1)
    if second != -1:
        brace = text.find('{', second)
        depth = 0
        end = -1
        for i in range(brace, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end != -1:
            text = text[:second] + text[end:]

# ------------------------------------------------------------
# employeeOptions(): dropdowns must exclude resigned employees.
# ------------------------------------------------------------
def replace_function(src: str, signature: str, new_body: str) -> str:
    start = src.find(signature)
    if start == -1:
        return src
    brace = src.find('{', start)
    if brace == -1:
        return src
    depth = 0
    end = -1
    quote = None
    escape = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end == -1:
        return src
    return src[:start] + new_body.strip() + src[end:]

employee_options_body = r'''
Future<List<EditOption>> employeeOptions() async {
  final rows = await loadActiveEmployees(limit: 5000);
  final options = rows.map((item) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    return EditOption('${row['id']}', formatValue(row['full_name']));
  }).where((option) => option.value.trim().isNotEmpty && option.label != '-').toList();
  options.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return uniqueOptions(options);
}
'''
if 'Future<List<EditOption>> employeeOptions()' in text:
    text = replace_function(text, 'Future<List<EditOption>> employeeOptions()', employee_options_body)
else:
    insert = text.find('List<EditField> employeeEditFields()')
    if insert != -1:
        text = text[:insert] + employee_options_body + '\n' + text[insert:]

# ------------------------------------------------------------
# Employees page: hide resigned even when Gender filter is All.
# ------------------------------------------------------------
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start != -1 and emp_end != -1:
    emp = text[emp_start:emp_end]
    method_start = emp.find('  Future<List<dynamic>> _loadEmployees() async {')
    if method_start != -1:
        brace = emp.find('{', method_start)
        depth = 0
        method_end = -1
        for i in range(brace, len(emp)):
            if emp[i] == '{':
                depth += 1
            elif emp[i] == '}':
                depth -= 1
                if depth == 0:
                    method_end = i + 1
                    break
        if method_end != -1:
            new_method = r'''  Future<List<dynamic>> _loadEmployees() async {
    final rows = await loadActiveEmployees(limit: 5000);
    if (genderFilter == 'All') return rows;
    return rows
        .where((item) => _matchesGenderFilter(
            normalizeRow(Map<String, dynamic>.from(item as Map))))
        .toList();
  }'''
            emp = emp[:method_start] + new_method + emp[method_end:]
    text = text[:emp_start] + emp + text[emp_end:]

# ------------------------------------------------------------
# Normal modules: hide resigned rows.
# ------------------------------------------------------------
replacements = {
    'load: () => loadContracts(),': 'load: () => activeOnlyRows(loadContracts()),',
    'load: () => loadLicensesGrouped(),': 'load: () => activeOnlyRows(loadLicensesGrouped()),',
    'load: () => loadCertificates(),': 'load: () => activeOnlyRows(loadCertificates()),',
    'load: () => loadEvaluations(),': 'load: () => activeOnlyRows(loadEvaluations()),',
    'load: () => loadAppointments(),': 'load: () => activeOnlyRows(loadAppointments()),',
    "ReportConfig(\n            'Employee Master List', () => loadEmployees(limit: 5000),": "ReportConfig(\n            'Employee Master List', () => loadActiveEmployees(limit: 5000),",
    "ReportConfig('Contract Monitoring Report',\n            () => loadContracts(limit: 5000),": "ReportConfig('Contract Monitoring Report',\n            () => activeOnlyRows(loadContracts(limit: 5000)),",
    "ReportConfig('License Report', () => loadLicenses(limit: 5000),": "ReportConfig('License Report', () => activeOnlyRows(loadLicenses(limit: 5000)),",
    "ReportConfig('Certificates Report',\n            () => loadCertificates(limit: 5000),": "ReportConfig('Certificates Report',\n            () => activeOnlyRows(loadCertificates(limit: 5000)),",
    "ReportConfig('Evaluation Report',\n            () => loadEvaluations(limit: 5000),": "ReportConfig('Evaluation Report',\n            () => activeOnlyRows(loadEvaluations(limit: 5000)),",
    "ReportConfig('Ranking Report', () => loadRankings(limit: 5000),": "ReportConfig('Ranking Report', () => activeOnlyRows(loadRankings(limit: 5000)),",
}
for old, new in replacements.items():
    text = text.replace(old, new)

# Ranking page custom loader.
text = text.replace('final rows = await loadRankings(limit: 5000);', 'final rows = await activeOnlyRows(loadRankings(limit: 5000));')

# Do not filter the Resigned Employees module itself.
text = text.replace('load: () => activeOnlyRows(loadResignedEmployees()),', 'load: () => loadResignedEmployees(),')

# ------------------------------------------------------------
# Table row count and syntax cleanup retained from previous requests.
# ------------------------------------------------------------
text = text.replace('padding: const EdgeInsets.fromLTRB(28, 24, 28, 28),', 'padding: const EdgeInsets.fromLTRB(28, 18, 28, 18),')
text = text.replace('const SizedBox(height: 22),\n          Expanded(child: child),', 'const SizedBox(height: 14),\n          Expanded(child: child),')
text = text.replace('constraints: const BoxConstraints(minHeight: 50),', 'constraints: const BoxConstraints(minHeight: 42),')
text = text.replace('constraints: const BoxConstraints(minHeight: 46),', 'constraints: const BoxConstraints(minHeight: 42),')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 7),')
text = text.replace('final tableHeight = availableHeight < 820 ? 820.0 : availableHeight;', 'final tableHeight = availableHeight;')

path.write_text(text, encoding='utf-8')
print('Resigned employees are now excluded from normal modules/dropdowns and shown only in Resigned Employees.')
