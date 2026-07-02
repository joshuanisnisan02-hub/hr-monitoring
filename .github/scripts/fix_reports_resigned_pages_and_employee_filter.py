from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# ------------------------------------------------------------
# 1) Fix ShellPage page list length so Reports and Resigned Employees do not crash.
# ------------------------------------------------------------
shell_start = text.find('class _ShellPageState extends State<ShellPage>')
nav_start = text.find('class NavItem', shell_start)
if shell_start == -1 or nav_start == -1:
    raise SystemExit('ShellPage block not found.')

shell = text[shell_start:nav_start]
if 'const ReportsPage(),' not in shell:
    shell = shell.replace('      const RankingPage(),', '      const RankingPage(),\n      const ReportsPage(),', 1)
if 'const ResignedEmployeesPage(),' not in shell:
    shell = shell.replace('      const ReportsPage(),', '      const ReportsPage(),\n      const ResignedEmployeesPage(),', 1)

# Clamp selected index defensively, so future sidebar/page mismatches never show red crash screen.
if 'final safeIndex = index.clamp(0, pages.length - 1).toInt();' not in shell:
    shell = shell.replace('    return Scaffold(', '    final safeIndex = index.clamp(0, pages.length - 1).toInt();\n    return Scaffold(', 1)
    shell = shell.replace('Expanded(child: pages[index])', 'Expanded(child: pages[safeIndex])', 1)

text = text[:shell_start] + shell + text[nav_start:]

# ------------------------------------------------------------
# 2) Make Employees module hide resigned employees for ALL gender filters.
# ------------------------------------------------------------
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')
emp = text[emp_start:emp_end]

# Replace _loadEmployees body robustly.
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
    if method_end == -1:
        raise SystemExit('Could not find _loadEmployees end.')
    new_method = r'''  Future<List<dynamic>> _loadEmployees() async {
    final rows = await loadEmployees();
    return rows.where((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      if (isResignedEmployeeRow(row)) return false;
      return _matchesGenderFilter(row);
    }).toList();
  }'''
    emp = emp[:method_start] + new_method + emp[method_end:]

# Make sure the status helper exists inside employee state.
if 'bool isResignedEmployeeRow(Map<String, dynamic> row)' not in emp:
    insert_at = emp.find('  @override\n  Widget build')
    if insert_at == -1:
        raise SystemExit('Could not find Employee build marker for helper insertion.')
    helper = r'''
  bool isResignedEmployeeRow(Map<String, dynamic> row) {
    final values = [row['employment_status'], row['employee_status'], row['status'], row['latest_status'], row['contract_status']];
    return values.any((value) => formatValue(value).toLowerCase().contains('resign'));
  }

'''
    emp = emp[:insert_at] + helper + emp[insert_at:]

text = text[:emp_start] + emp + text[emp_end:]

# ------------------------------------------------------------
# 3) Add resigned employees loader if missing.
# ------------------------------------------------------------
if 'Future<List<dynamic>> loadResignedEmployees' not in text:
    marker = 'Future<List<dynamic>> loadLicenses({int limit = 1500})'
    if marker not in text:
        raise SystemExit('Loader insertion point not found.')
    loader = r'''
Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {
  final employees = await loadEmployees(limit: limit);
  final employeeRows = employees.map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();

  final resignedIds = <String>{};
  try {
    final contracts = await loadContracts(limit: limit);
    for (final item in contracts) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      final status = formatValue(row['status']).toLowerCase();
      if (status.contains('resign')) resignedIds.add('${row['employee_id']}');
    }
  } catch (_) {}

  return employeeRows.where((row) {
    final status = formatValue(row['employment_status']).toLowerCase();
    return status.contains('resign') || resignedIds.contains('${row['id']}');
  }).toList()
    ..sort((a, b) => formatValue(a['full_name']).compareTo(formatValue(b['full_name'])));
}

'''
    text = text.replace(marker, loader + marker, 1)

# ------------------------------------------------------------
# 4) Add ReportsPage if missing. Uses current dashboard counts and card-like UI.
# ------------------------------------------------------------
if 'class ReportsPage extends' not in text:
    marker = 'class RankFilterAutocompleteBox'
    if marker not in text:
        raise SystemExit('Reports page insertion marker not found.')
    reports_page = r'''
class ReportsPage extends StatelessWidget {
  const ReportsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Reports',
        subtitle: 'Print and review HR monitoring summary totals.',
        child: FutureBuilder<List<dynamic>>(
          future: db.from('hr_dashboard_counts').select(),
          builder: (_, snap) {
            if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snap.hasError) return ErrorBox('${snap.error}');
            final row = snap.data?.isNotEmpty == true ? snap.data!.first as Map<String, dynamic> : <String, dynamic>{};
            final cards = [
              Metric('Active Employees', row['active_employees'], Icons.people_alt_rounded, const Color(0xFFEFF6FF), const Color(0xFF1D4ED8)),
              Metric('Active Faculty', row['active_faculty'], Icons.school_rounded, const Color(0xFFF0FDF4), const Color(0xFF15803D)),
              Metric('For Renewal', row['contracts_for_renewal'], Icons.schedule_rounded, const Color(0xFFFFFBEB), const Color(0xFFB45309)),
              Metric('Expired Contracts', row['expired_contracts'], Icons.warning_amber_rounded, const Color(0xFFFEF2F2), const Color(0xFFB91C1C)),
              Metric('Licenses Due', row['licenses_due'], Icons.badge_rounded, const Color(0xFFF5F3FF), const Color(0xFF6D28D9)),
              Metric('Certificates Due', row['certificates_due'], Icons.workspace_premium_rounded, const Color(0xFFECFEFF), const Color(0xFF0E7490)),
              Metric('Ranking Records', row['ranking_applications'], Icons.leaderboard_rounded, const Color(0xFFF8FAFC), _ink),
            ];
            return SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Row(children: [
                      FilledButton.icon(
                        onPressed: () {
                          final columns = const [GridCol('title', 'Summary', flex: 3, primary: true), GridCol('value', 'Total', isNumber: true)];
                          final rows = cards.map((m) => {'title': m.title, 'value': m.value ?? 0}).toList();
                          final markup = buildPrintableReportHtml('HR Monitoring Summary Report', columns, rows);
                          final blob = html.Blob([markup], 'text/html');
                          final url = html.Url.createObjectUrlFromBlob(blob);
                          html.window.open(url, '_blank');
                        },
                        icon: const Icon(Icons.print_rounded),
                        label: const Text('Print Report'),
                      ),
                      const SizedBox(width: 14),
                      const Expanded(child: Text('Review report totals, then print a clean summary report.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700))),
                    ]),
                  ),
                ),
                const SizedBox(height: 18),
                Wrap(spacing: 16, runSpacing: 16, children: cards.map((m) => MetricCard(m)).toList()),
              ]),
            );
          },
        ),
      );
}

'''
    text = text.replace(marker, reports_page + marker, 1)

# ------------------------------------------------------------
# 5) Add ResignedEmployeesPage if missing.
# ------------------------------------------------------------
if 'class ResignedEmployeesPage extends' not in text:
    marker = 'class ReportsPage extends'
    if marker not in text:
        marker = 'class RankFilterAutocompleteBox'
    if marker not in text:
        raise SystemExit('Resigned page insertion marker not found.')
    page = r'''
class ResignedEmployeesPage extends StatelessWidget {
  const ResignedEmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Resigned Employees',
        subtitle: 'Employees marked as resigned are separated from the active Employees table.',
        child: CrudTable(
          load: () => loadResignedEmployees(),
          searchHint: 'Search resigned employee, bio number, type, date, or status',
          addLabel: 'Add Employee',
          allowAdd: false,
          reportTitle: 'Resigned Employees Report',
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('employee_type', 'Type'),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onView: viewEmployee,
          onEdit: editEmployee,
          showDelete: false,
          onDelete: (row) async {},
        ),
      );
}

'''
    text = text.replace(marker, page + marker, 1)

path.write_text(text, encoding='utf-8')
print('Fixed Reports/Resigned navigation pages and hid resigned employees from Employees.')
