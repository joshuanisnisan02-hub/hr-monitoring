from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

insert_before = "class ShellPage extends StatefulWidget {"
helper = r'''
class ModuleTarget {
  final int index;
  final String? filter;
  final int? reportIndex;
  const ModuleTarget(this.index, {this.filter, this.reportIndex});
}

class DashboardSnapshot {
  final Map<String, dynamic> counts;
  final int totalFemale;
  final int totalMale;
  final int totalGender;
  final int totalRanks;
  final int totalLicenseRecords;
  final int totalCertificateRecords;
  const DashboardSnapshot({required this.counts, required this.totalFemale, required this.totalMale, required this.totalGender, required this.totalRanks, required this.totalLicenseRecords, required this.totalCertificateRecords});
}

Future<DashboardSnapshot> loadDashboardSnapshot() async {
  final countRows = await db.from('hr_dashboard_counts').select();
  final counts = countRows.isNotEmpty ? Map<String, dynamic>.from(countRows.first as Map) : <String, dynamic>{};
  final employees = (await loadEmployees(limit: 5000)).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
  var female = 0;
  var male = 0;
  for (final employee in employees) {
    final gender = summaryGenderLabel(employee['gender']);
    if (gender == 'Female') female++;
    if (gender == 'Male') male++;
  }
  final rankings = await loadRankings(limit: 5000);
  final licenses = await loadLicenses(limit: 5000);
  final certificates = await loadCertificates(limit: 5000);
  return DashboardSnapshot(
    counts: counts,
    totalFemale: female,
    totalMale: male,
    totalGender: female + male,
    totalRanks: rankings.length,
    totalLicenseRecords: licenses.length,
    totalCertificateRecords: certificates.length,
  );
}

'''
if 'class ModuleTarget {' not in text:
    if insert_before not in text:
        raise SystemExit('ShellPage insertion point was not found.')
    text = text.replace(insert_before, helper + insert_before, 1)

old_shell_state = """class _ShellPageState extends State<ShellPage> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardPage(onNavigate: (i) => setState(() => index = i)),
      const EmployeesPage(),
      const ContractsPage(),
      const CredentialsPage(),
      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
    ];
"""
new_shell_state = """class _ShellPageState extends State<ShellPage> {
  int index = 0;
  String? moduleFilter;
  int? reportIndex;
  int routeToken = 0;

  void openModule(ModuleTarget target) => setState(() {
        index = target.index;
        moduleFilter = target.filter;
        reportIndex = target.reportIndex;
        routeToken++;
      });

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardPage(onNavigate: openModule),
      EmployeesPage(key: ValueKey('employees-$routeToken'), initialSearch: index == 1 ? moduleFilter : null),
      ContractsPage(key: ValueKey('contracts-$routeToken'), initialSearch: index == 2 ? moduleFilter : null),
      CredentialsPage(key: ValueKey('credentials-$routeToken'), initialSearch: index == 3 ? moduleFilter : null),
      EvaluationsPage(key: ValueKey('evaluations-$routeToken'), initialSearch: index == 4 ? moduleFilter : null),
      const AppointmentPage(),
      RankingPage(key: ValueKey('ranking-$routeToken'), initialSearch: index == 6 ? moduleFilter : null),
      ReportsPage(key: ValueKey('reports-$routeToken'), initialReportIndex: index == 7 ? reportIndex : null),
    ];
"""
if old_shell_state in text:
    text = text.replace(old_shell_state, new_shell_state, 1)
elif 'void openModule(ModuleTarget target)' in text:
    pass
else:
    raise SystemExit('ShellPage state block was not found. Please inspect ShellPage manually.')

old_nav_items = """      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
    ];
"""
new_nav_items = """      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Reports', Icons.summarize_rounded),
    ];
"""
if old_nav_items in text:
    text = text.replace(old_nav_items, new_nav_items, 1)

# Add initialSearch to pages.
replacements = {
"class ContractsPage extends StatelessWidget {\n  const ContractsPage({super.key});": "class ContractsPage extends StatelessWidget {\n  final String? initialSearch;\n  const ContractsPage({super.key, this.initialSearch});",
"class CredentialsPage extends StatelessWidget {\n  const CredentialsPage({super.key});": "class CredentialsPage extends StatelessWidget {\n  final String? initialSearch;\n  const CredentialsPage({super.key, this.initialSearch});",
"class EvaluationsPage extends StatelessWidget {\n  const EvaluationsPage({super.key});": "class EvaluationsPage extends StatelessWidget {\n  final String? initialSearch;\n  const EvaluationsPage({super.key, this.initialSearch});",
"class RankingPage extends StatefulWidget {\n  const RankingPage({super.key});": "class RankingPage extends StatefulWidget {\n  final String? initialSearch;\n  const RankingPage({super.key, this.initialSearch});",
"class ReportsPage extends StatefulWidget {\n  const ReportsPage({super.key});": "class ReportsPage extends StatefulWidget {\n  final int? initialReportIndex;\n  const ReportsPage({super.key, this.initialReportIndex});",
}
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new, 1)

# EmployeesPage already stateful from prior patch; add field if not present.
if "class EmployeesPage extends StatefulWidget {\n  const EmployeesPage({super.key});" in text:
    text = text.replace("class EmployeesPage extends StatefulWidget {\n  const EmployeesPage({super.key});", "class EmployeesPage extends StatefulWidget {\n  final String? initialSearch;\n  const EmployeesPage({super.key, this.initialSearch});", 1)

# Add initialSearch to CrudTable calls in main modules.
call_replacements = {
"searchHint: 'Search employee, bio number, gender, education, status, or date hired',\n              addLabel: 'Add Employee',": "searchHint: 'Search employee, bio number, gender, education, status, or date hired',\n              initialSearch: widget.initialSearch ?? '',\n              addLabel: 'Add Employee',",
"searchHint: 'Search employee, contract type, date, or status',\n          addLabel: 'Add Contract',": "searchHint: 'Search employee, contract type, date, or status',\n          initialSearch: initialSearch ?? '',\n          addLabel: 'Add Contract',",
"searchHint: 'Search employee, license, certificate, expiry, or status',\n          addLabel: 'Add Credential',": "searchHint: 'Search employee, license, certificate, expiry, or status',\n          initialSearch: initialSearch ?? '',\n          addLabel: 'Add Credential',",
"searchHint: 'Search employee, academic year, semester, rating, or description',\n          addLabel: 'Add Evaluation',": "searchHint: 'Search employee, academic year, semester, rating, or description',\n          initialSearch: initialSearch ?? '',\n          addLabel: 'Add Evaluation',",
"searchHint: 'Search employee, appointment, rank, salary, or points',\n": "searchHint: 'Search employee, appointment, rank, salary, or points',\n              initialSearch: widget.initialSearch ?? '',\n",
}
for old, new in call_replacements.items():
    if old in text and new not in text:
        text = text.replace(old, new, 1)

# CrudTable props.
if "final String searchHint;\n  final String addLabel;" in text:
    text = text.replace("final String searchHint;\n  final String addLabel;", "final String searchHint;\n  final String initialSearch;\n  final String addLabel;", 1)
if "required this.load, required this.searchHint, required this.addLabel" in text:
    text = text.replace("required this.load, required this.searchHint, required this.addLabel", "required this.load, required this.searchHint, this.initialSearch = '', required this.addLabel", 1)
if "String query = '';" in text:
    text = text.replace("String query = '';", "String query = '';", 1)
if "future = widget.load();\n    sortKey = widget.columns.first.key;" in text:
    text = text.replace("future = widget.load();\n    sortKey = widget.columns.first.key;", "future = widget.load();\n    query = widget.initialSearch;\n    sortKey = widget.columns.first.key;", 1)
if "void refresh() => setState(() {" in text and "didUpdateWidget(covariant CrudTable oldWidget)" not in text:
    text = text.replace("  void refresh() => setState(() {", "  @override\n  void didUpdateWidget(covariant CrudTable oldWidget) {\n    super.didUpdateWidget(oldWidget);\n    if (oldWidget.initialSearch != widget.initialSearch) {\n      query = widget.initialSearch;\n      page = 0;\n    }\n  }\n\n  void refresh() => setState(() {", 1)

# TableToolbar needs initialText and controller to show prefilled search.
if "final String hint;\n  final String addLabel;" in text:
    text = text.replace("final String hint;\n  final String addLabel;", "final String hint;\n  final String initialText;\n  final String addLabel;", 1)
if "required this.total, required this.showing, required this.hint, required this.addLabel" in text:
    text = text.replace("required this.total, required this.showing, required this.hint, required this.addLabel", "required this.total, required this.showing, required this.hint, this.initialText = '', required this.addLabel", 1)
if "hint: widget.searchHint,\n" in text and "initialText: query," not in text:
    text = text.replace("hint: widget.searchHint,\n", "hint: widget.searchHint,\n              initialText: query,\n", 1)
old_search = "child: TextField(onChanged: onSearch, decoration: InputDecoration(prefixIcon: const Icon(Icons.search_rounded), hintText: hint, filled: true, fillColor: const Color(0xFFF8FAFC))),"
new_search = "child: TextField(controller: TextEditingController(text: initialText)..selection = TextSelection.collapsed(offset: initialText.length), onChanged: onSearch, decoration: InputDecoration(prefixIcon: const Icon(Icons.search_rounded), hintText: hint, filled: true, fillColor: const Color(0xFFF8FAFC))),"
if old_search in text:
    text = text.replace(old_search, new_search, 1)

# Reports initial index.
if "int selected = 0;" in text:
    text = text.replace("int selected = 0;", "late int selected;", 1)
if "class _ReportsPageState extends State<ReportsPage> {\n  late int selected;" in text and "void initState()" not in text[text.find("class _ReportsPageState"):text.find("List<ReportConfig> get reports", text.find("class _ReportsPageState"))]:
    text = text.replace("class _ReportsPageState extends State<ReportsPage> {\n  late int selected;\n", "class _ReportsPageState extends State<ReportsPage> {\n  late int selected;\n\n  @override\n  void initState() {\n    super.initState();\n    selected = widget.initialReportIndex ?? 0;\n  }\n", 1)

# Replace DashboardPage implementation block.
start = text.find('class DashboardPage extends StatelessWidget {')
end = text.find('class Metric {', start)
if start == -1 or end == -1:
    raise SystemExit('DashboardPage block not found.')
new_dashboard = r'''class DashboardPage extends StatelessWidget {
  final ValueChanged<ModuleTarget> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle: 'At-a-glance summary of HR monitoring records. Click a card to open the related module/report.',
        child: FutureBuilder<DashboardSnapshot>(
          future: loadDashboardSnapshot(),
          builder: (_, snap) {
            if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snap.hasError) return ErrorBox('${snap.error}');
            final data = snap.data ?? const DashboardSnapshot(counts: {}, totalFemale: 0, totalMale: 0, totalGender: 0, totalRanks: 0, totalLicenseRecords: 0, totalCertificateRecords: 0);
            final row = data.counts;
            final cards = [
              Metric('Active Employees', row['active_employees'], Icons.people_alt_rounded, const Color(0xFFEFF6FF), const Color(0xFF1D4ED8), target: const ModuleTarget(1, filter: 'active')),
              Metric('Active Faculty', row['active_faculty'], Icons.school_rounded, const Color(0xFFF0FDF4), const Color(0xFF15803D), target: const ModuleTarget(1, filter: 'faculty')),
              Metric('For Renewal', row['contracts_for_renewal'], Icons.schedule_rounded, const Color(0xFFFFFBEB), const Color(0xFFB45309), target: const ModuleTarget(2, filter: 'For Renewal')),
              Metric('Expired Contracts', row['expired_contracts'], Icons.warning_amber_rounded, const Color(0xFFFEF2F2), const Color(0xFFB91C1C), target: const ModuleTarget(2, filter: 'Expired')),
              Metric('Licenses Due', row['licenses_due'], Icons.badge_rounded, const Color(0xFFF5F3FF), const Color(0xFF6D28D9), target: const ModuleTarget(3, filter: 'For Renewal')),
              Metric('Certificates Due', row['certificates_due'], Icons.workspace_premium_rounded, const Color(0xFFECFEFF), const Color(0xFF0E7490), target: const ModuleTarget(3, filter: 'For Renewal')),
              Metric('Ranking Records', row['ranking_applications'], Icons.leaderboard_rounded, const Color(0xFFF8FAFC), _ink, target: const ModuleTarget(6)),
            ];
            final reportCards = [
              Metric('Total Female', data.totalFemale, Icons.female_rounded, const Color(0xFFFDF2F8), const Color(0xFFBE185D), target: const ModuleTarget(7, reportIndex: 0)),
              Metric('Total Male', data.totalMale, Icons.male_rounded, const Color(0xFFEFF6FF), const Color(0xFF1D4ED8), target: const ModuleTarget(7, reportIndex: 0)),
              Metric('Total Gender', data.totalGender, Icons.wc_rounded, const Color(0xFFF8FAFC), _ink, target: const ModuleTarget(7, reportIndex: 0)),
              Metric('Rank Summary', data.totalRanks, Icons.leaderboard_rounded, const Color(0xFFF0FDF4), const Color(0xFF15803D), target: const ModuleTarget(7, reportIndex: 1)),
              Metric('License Summary', data.totalLicenseRecords, Icons.badge_rounded, const Color(0xFFFFFBEB), const Color(0xFFB45309), target: const ModuleTarget(7, reportIndex: 2)),
              Metric('NC/TM Summary', data.totalCertificateRecords, Icons.workspace_premium_rounded, const Color(0xFFECFEFF), const Color(0xFF0E7490), target: const ModuleTarget(7, reportIndex: 3)),
            ];
            return SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Module Status', style: TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 16)),
                const SizedBox(height: 12),
                Wrap(spacing: 16, runSpacing: 16, children: cards.map((m) => MetricCard(m, onTap: m.target == null ? null : () => onNavigate(m.target!))).toList()),
                const SizedBox(height: 24),
                const Text('Report Totals', style: TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 16)),
                const SizedBox(height: 12),
                Wrap(spacing: 16, runSpacing: 16, children: reportCards.map((m) => MetricCard(m, onTap: m.target == null ? null : () => onNavigate(m.target!))).toList()),
                const SizedBox(height: 24),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  QuickCard('Manage Employees', Icons.people_alt_rounded, () => onNavigate(const ModuleTarget(1))),
                  QuickCard('Manage Contracts', Icons.assignment_rounded, () => onNavigate(const ModuleTarget(2))),
                  QuickCard('Manage Credentials', Icons.badge_rounded, () => onNavigate(const ModuleTarget(3))),
                  QuickCard('Open Reports', Icons.summarize_rounded, () => onNavigate(const ModuleTarget(7))),
                ]),
              ]),
            );
          },
        ),
      );
}

'''
text = text[:start] + new_dashboard + text[end:]

# Metric and MetricCard update.
old_metric = """class Metric {
  final String title;
  final Object? value;
  final IconData icon;
  final Color bg;
  final Color fg;
  const Metric(this.title, this.value, this.icon, this.bg, this.fg);
}
"""
new_metric = """class Metric {
  final String title;
  final Object? value;
  final IconData icon;
  final Color bg;
  final Color fg;
  final ModuleTarget? target;
  const Metric(this.title, this.value, this.icon, this.bg, this.fg, {this.target});
}
"""
if old_metric in text:
    text = text.replace(old_metric, new_metric, 1)

old_metric_card = r'''class MetricCard extends StatelessWidget {
  final Metric metric;
  const MetricCard(this.metric, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 255,
        height: 136,
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Container(width: 42, height: 42, decoration: BoxDecoration(color: metric.bg, borderRadius: BorderRadius.circular(14)), child: Icon(metric.icon, color: metric.fg)),
                const Spacer(),
                Text('${metric.value ?? 0}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.7)),
              ]),
              const Spacer(),
              Text(metric.title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)),
            ]),
          ),
        ),
      );
}
'''
new_metric_card = r'''class MetricCard extends StatelessWidget {
  final Metric metric;
  final VoidCallback? onTap;
  const MetricCard(this.metric, {super.key, this.onTap});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 255,
        height: 136,
        child: Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(22),
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  Container(width: 42, height: 42, decoration: BoxDecoration(color: metric.bg, borderRadius: BorderRadius.circular(14)), child: Icon(metric.icon, color: metric.fg)),
                  const Spacer(),
                  Text('${metric.value ?? 0}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.7)),
                ]),
                const Spacer(),
                Row(children: [
                  Expanded(child: Text(metric.title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                  if (onTap != null) const Icon(Icons.chevron_right_rounded, color: _muted),
                ]),
              ]),
            ),
          ),
        ),
      );
}
'''
if old_metric_card in text:
    text = text.replace(old_metric_card, new_metric_card, 1)

path.write_text(text, encoding='utf-8')
print('Clickable dashboard filters patch applied to lib/main.dart')
