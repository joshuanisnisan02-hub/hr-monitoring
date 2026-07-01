from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# 1) Add dashboard navigation/data helper classes before ShellPage.
helper_marker = 'class ShellPage extends StatefulWidget {'
helper_code = r'''
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
    if helper_marker not in text:
        raise SystemExit('ShellPage marker not found.')
    text = text.replace(helper_marker, helper_code + helper_marker, 1)

# 2) Replace ShellPage state completely so it supports module targets and report targets.
shell_start = text.find('class _ShellPageState extends State<ShellPage> {')
shell_end = text.find('\nclass NavItem', shell_start)
if shell_start == -1 or shell_end == -1:
    raise SystemExit('ShellPage state block was not found. Please send the ShellPage lines for manual patching.')
new_shell = r'''class _ShellPageState extends State<ShellPage> {
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
    return Scaffold(
      body: Row(children: [
        AppSidebar(selectedIndex: index, onChanged: (i) => setState(() {
          index = i;
          moduleFilter = null;
          reportIndex = null;
          routeToken++;
        })),
        const VerticalDivider(width: 1, color: _line),
        Expanded(child: pages[index]),
      ]),
    );
  }
}
'''
text = text[:shell_start] + new_shell + text[shell_end:]

# 3) Ensure Reports exists in sidebar and make sidebar scrollable to avoid overlap.
items_start = text.find('    const items = [')
items_end = text.find('    ];', items_start)
if items_start != -1 and items_end != -1:
    items_end += len('    ];')
    items_block = r'''    const items = [
      NavItem('Dashboard', Icons.dashboard_rounded),
      NavItem('Employees', Icons.groups_rounded),
      NavItem('Contracts', Icons.assignment_rounded),
      NavItem('Credentials', Icons.badge_rounded),
      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Reports', Icons.summarize_rounded),
    ];'''
    text = text[:items_start] + items_block + text[items_end:]

sidebar_old = r'''        const SizedBox(height: 30),
        for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
        const Spacer(),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
          child: const Text('Employee add flow now includes full profile, contract, and credential details.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.35, fontWeight: FontWeight.w600)),
        ),'''
sidebar_new = r'''        const SizedBox(height: 30),
        Expanded(
          child: ListView(
            padding: EdgeInsets.zero,
            children: [
              for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
            ],
          ),
        ),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
          child: const Text('HR records and printable summaries.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.25, fontWeight: FontWeight.w600)),
        ),'''
if sidebar_old in text:
    text = text.replace(sidebar_old, sidebar_new, 1)

# 4) Add initialSearch / initialReportIndex fields to page classes.
class_replacements = [
    (r"class EmployeesPage extends StatefulWidget \{\n\s*const EmployeesPage\(\{super.key\}\);", "class EmployeesPage extends StatefulWidget {\n  final String? initialSearch;\n  const EmployeesPage({super.key, this.initialSearch});"),
    (r"class ContractsPage extends StatelessWidget \{\n\s*const ContractsPage\(\{super.key\}\);", "class ContractsPage extends StatelessWidget {\n  final String? initialSearch;\n  const ContractsPage({super.key, this.initialSearch});"),
    (r"class CredentialsPage extends StatelessWidget \{\n\s*const CredentialsPage\(\{super.key\}\);", "class CredentialsPage extends StatelessWidget {\n  final String? initialSearch;\n  const CredentialsPage({super.key, this.initialSearch});"),
    (r"class EvaluationsPage extends StatelessWidget \{\n\s*const EvaluationsPage\(\{super.key\}\);", "class EvaluationsPage extends StatelessWidget {\n  final String? initialSearch;\n  const EvaluationsPage({super.key, this.initialSearch});"),
    (r"class RankingPage extends StatefulWidget \{\n\s*const RankingPage\(\{super.key\}\);", "class RankingPage extends StatefulWidget {\n  final String? initialSearch;\n  const RankingPage({super.key, this.initialSearch});"),
    (r"class ReportsPage extends StatefulWidget \{\n\s*const ReportsPage\(\{super.key\}\);", "class ReportsPage extends StatefulWidget {\n  final int? initialReportIndex;\n  const ReportsPage({super.key, this.initialReportIndex});"),
]
for pattern, replacement in class_replacements:
    text = re.sub(pattern, replacement, text, count=1)

# 5) Add initialSearch support to CrudTable itself.
if 'final String initialSearch;' not in text:
    text = text.replace('final String searchHint;\n  final String addLabel;', 'final String searchHint;\n  final String initialSearch;\n  final String addLabel;', 1)
    text = text.replace('required this.load, required this.searchHint, required this.addLabel', 'required this.load, required this.searchHint, this.initialSearch = \'\', required this.addLabel', 1)
if 'query = widget.initialSearch;' not in text:
    text = text.replace('future = widget.load();\n    sortKey = widget.columns.first.key;', 'future = widget.load();\n    query = widget.initialSearch;\n    sortKey = widget.columns.first.key;', 1)
if 'didUpdateWidget(covariant CrudTable oldWidget)' not in text:
    text = text.replace('  void refresh() => setState(() {', "  @override\n  void didUpdateWidget(covariant CrudTable oldWidget) {\n    super.didUpdateWidget(oldWidget);\n    if (oldWidget.initialSearch != widget.initialSearch) {\n      query = widget.initialSearch;\n      page = 0;\n    }\n  }\n\n  void refresh() => setState(() {", 1)

# 6) Pass initialSearch to CrudTable calls where possible. Safe idempotent replacements.
crud_replacements = [
    ("searchHint: 'Search employee, bio number, gender, education, status, or date hired',\n              addLabel: 'Add Employee',", "searchHint: 'Search employee, bio number, gender, education, status, or date hired',\n              initialSearch: widget.initialSearch ?? '',\n              addLabel: 'Add Employee',"),
    ("searchHint: 'Search employee, contract type, date, or status',\n          addLabel: 'Add Contract',", "searchHint: 'Search employee, contract type, date, or status',\n          initialSearch: initialSearch ?? '',\n          addLabel: 'Add Contract',"),
    ("searchHint: 'Search employee, license, certificate, expiry, or status',\n          addLabel: 'Add Credential',", "searchHint: 'Search employee, license, certificate, expiry, or status',\n          initialSearch: initialSearch ?? '',\n          addLabel: 'Add Credential',"),
    ("searchHint: 'Search employee, academic year, semester, rating, or description',\n          addLabel: 'Add Evaluation',", "searchHint: 'Search employee, academic year, semester, rating, or description',\n          initialSearch: initialSearch ?? '',\n          addLabel: 'Add Evaluation',"),
    ("searchHint: 'Search employee, appointment, rank, salary, or points',\n", "searchHint: 'Search employee, appointment, rank, salary, or points',\n              initialSearch: widget.initialSearch ?? '',\n"),
]
for old, new in crud_replacements:
    if old in text and new not in text:
        text = text.replace(old, new, 1)

# 7) Keep Reports selected index aligned with dashboard report card target.
reports_state_start = text.find('class _ReportsPageState extends State<ReportsPage> {')
reports_getter_start = text.find('  List<ReportConfig> get reports =>', reports_state_start)
if reports_state_start != -1 and reports_getter_start != -1:
    reports_prefix = text[reports_state_start:reports_getter_start]
    reports_prefix = re.sub(r'\n\s*int selected = 0;\n', '\n  late int selected;\n', reports_prefix)
    if 'void initState()' not in reports_prefix:
        reports_prefix = reports_prefix.replace('  late int selected;\n', "  late int selected;\n\n  @override\n  void initState() {\n    super.initState();\n    selected = widget.initialReportIndex ?? 0;\n  }\n")
    text = text[:reports_state_start] + reports_prefix + text[reports_getter_start:]

# 8) Replace DashboardPage block.
dash_start = text.find('class DashboardPage extends StatelessWidget {')
dash_end = text.find('\nclass Metric {', dash_start)
if dash_start == -1 or dash_end == -1:
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
text = text[:dash_start] + new_dashboard + text[dash_end:]

# 9) Replace Metric / MetricCard.
metric_start = text.find('class Metric {')
metric_card_start = text.find('class MetricCard', metric_start)
if metric_start != -1 and metric_card_start != -1:
    new_metric = r'''class Metric {
  final String title;
  final Object? value;
  final IconData icon;
  final Color bg;
  final Color fg;
  final ModuleTarget? target;
  const Metric(this.title, this.value, this.icon, this.bg, this.fg, {this.target});
}

'''
    text = text[:metric_start] + new_metric + text[metric_card_start:]

metric_card_start = text.find('class MetricCard')
quick_card_start = text.find('class QuickCard', metric_card_start)
if metric_card_start == -1 or quick_card_start == -1:
    raise SystemExit('MetricCard block not found.')
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
text = text[:metric_card_start] + new_metric_card + text[quick_card_start:]

path.write_text(text, encoding='utf-8')
print('Clickable dashboard filters v2 patch applied to lib/main.dart')
