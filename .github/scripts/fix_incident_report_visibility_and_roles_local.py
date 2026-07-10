from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Add role helpers.
if 'enum AppUserRole' not in text:
    marker = 'class ShellPage extends StatefulWidget {'
    helpers = r'''
enum AppUserRole { admin, hr, ir }

String currentUserEmail() => db.auth.currentUser?.email?.trim().toLowerCase() ?? '';

Future<AppUserRole> loadCurrentUserRole() async {
  final email = currentUserEmail();
  if (email.isEmpty) return AppUserRole.hr;
  try {
    final rows = await db
        .from('app_user_roles')
        .select('role')
        .eq('email', email)
        .limit(1);
    if (rows is List && rows.isNotEmpty) {
      final role = '${(rows.first as Map)['role'] ?? ''}'.trim().toLowerCase();
      if (role == 'admin') return AppUserRole.admin;
      if (role == 'ir') return AppUserRole.ir;
      return AppUserRole.hr;
    }
  } catch (_) {}
  if (email.contains('admin')) return AppUserRole.admin;
  if (email.contains('ir')) return AppUserRole.ir;
  return AppUserRole.hr;
}

bool canSeeIncidentReport(AppUserRole role) =>
    role == AppUserRole.admin || role == AppUserRole.ir;

'''
    if marker not in text:
        raise SystemExit('Could not find ShellPage insertion point.')
    text = text.replace(marker, helpers + marker, 1)

# Replace ShellPage state class with role-aware pages/sidebar.
start = text.find('class _ShellPageState extends State<ShellPage> {')
end = text.find('class NavItem {', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate _ShellPageState block.')
new_shell_state = r'''class _ShellPageState extends State<ShellPage> {
  int index = 0;
  final Set<int> visitedPages = {0};
  AppUserRole? role;
  bool loadingRole = true;

  @override
  void initState() {
    super.initState();
    loadCurrentUserRole().then((value) {
      if (!mounted) return;
      setState(() {
        role = value;
        loadingRole = false;
      });
    });
  }

  void selectPage(int nextIndex) {
    setState(() {
      index = nextIndex;
      visitedPages.add(nextIndex);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (loadingRole) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final currentRole = role ?? AppUserRole.hr;
    final pages = currentRole == AppUserRole.ir
        ? <Widget>[const IncidentReportPage()]
        : <Widget>[
            DashboardPage(onNavigate: selectPage),
            const EmployeesPage(),
            const ContractsPage(),
            const CredentialsPage(),
            const EvaluationsPage(),
            const AppointmentPage(),
            const RankingPage(),
            if (canSeeIncidentReport(currentRole)) const IncidentReportPage(),
            const ReportsPage(),
            const ResignedEmployeesPage(),
            const ArchivedPage(),
          ];
    final safeIndex = index.clamp(0, pages.length - 1).toInt();
    visitedPages.add(safeIndex);
    return Scaffold(
      body: Row(children: [
        AppSidebar(
            selectedIndex: safeIndex, onChanged: selectPage, role: currentRole),
        const SizedBox.shrink(),
        Expanded(
          child: IndexedStack(
            index: safeIndex,
            children: [
              for (var i = 0; i < pages.length; i++)
                visitedPages.contains(i) ? pages[i] : const SizedBox.shrink(),
            ],
          ),
        ),
      ]),
    );
  }
}

'''
text = text[:start] + new_shell_state + text[end:]

# Update AppSidebar constructor and item list.
text = text.replace(
    """class AppSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  const AppSidebar(
      {super.key, required this.selectedIndex, required this.onChanged});""",
    """class AppSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;
  final AppUserRole role;

  const AppSidebar(
      {super.key,
      required this.selectedIndex,
      required this.onChanged,
      required this.role});""",
    1,
)

old_items = """    const items = [
      NavItem('Dashboard', Icons.dashboard_rounded),
      NavItem('Employees', Icons.groups_rounded),
      NavItem('Contracts', Icons.assignment_rounded),
      NavItem('Credentials', Icons.badge_rounded),
      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Reports', Icons.summarize_rounded),
      NavItem('Resigned Employees', Icons.person_off_rounded),
      NavItem('Archived', Icons.archive_rounded),
    ];"""
new_items = """    final items = role == AppUserRole.ir
        ? const [
            NavItem('Incident Report', Icons.report_problem_rounded),
          ]
        : [
            const NavItem('Dashboard', Icons.dashboard_rounded),
            const NavItem('Employees', Icons.groups_rounded),
            const NavItem('Contracts', Icons.assignment_rounded),
            const NavItem('Credentials', Icons.badge_rounded),
            const NavItem('Evaluations', Icons.rate_review_rounded),
            const NavItem('Appointment', Icons.work_outline_rounded),
            const NavItem('Ranking', Icons.leaderboard_rounded),
            if (canSeeIncidentReport(role))
              const NavItem('Incident Report', Icons.report_problem_rounded),
            const NavItem('Reports', Icons.summarize_rounded),
            const NavItem('Resigned Employees', Icons.person_off_rounded),
            const NavItem('Archived', Icons.archive_rounded),
          ];"""
if old_items in text:
    text = text.replace(old_items, new_items, 1)
else:
    text = text.replace("""    const items = [""", """    final items = role == AppUserRole.ir
        ? const [
            NavItem('Incident Report', Icons.report_problem_rounded),
          ]
        : [""", 1)
    text = text.replace("""      NavItem('Archived', Icons.archive_rounded),
    ];""", """      if (canSeeIncidentReport(role))
        const NavItem('Incident Report', Icons.report_problem_rounded),
      const NavItem('Archived', Icons.archive_rounded),
    ];""", 1)

# Make sure IR module exists in code even if the previous script was not run locally.
if 'class IncidentReportPage' not in text:
    marker = 'class ReportsPage extends StatelessWidget'
    module = r'''
class IncidentReportPage extends StatelessWidget {
  const IncidentReportPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Incident Report',
        subtitle:
            'Track employee IR, NTE, explanation deadline, NOD, and received dates.',
        child: CrudTable(
          load: () => activeOnlyRows(loadIncidentReports()),
          searchHint: 'Search employee, IR, NTE, explanation, or NOD',
          addLabel: 'Add Incident Report',
          reportTitle: 'Incident Report',
          archiveTableName: 'incident_reports',
          archiveModuleName: 'Incident Report',
          columns: const [
            GridCol('employee_name', 'Employee', flex: 3, primary: true),
            GridCol('ir', 'IR', flex: 2),
            GridCol('date_submitted', 'Date Submitted', flex: 2),
            GridCol('nte_date_received', 'NTE Date Received', flex: 2),
            GridCol('explanation_date_submitted',
                'Explanation Date Submitted',
                flex: 2),
            GridCol('nod', 'NOD', flex: 2),
            GridCol('date_received', 'Date Received', flex: 2),
          ],
          onAdd: (ctx, refresh) => editIncidentReport(ctx, null, refresh),
          onView: viewIncidentReport,
          onEdit: editIncidentReport,
          onDelete: (row) =>
              db.from('incident_reports').delete().eq('id', row['id']),
        ),
      );
}

String? incidentReportComputedExplanationDate(String nteText) {
  final parsed = parseFlexibleDate(nteText);
  if (parsed == null) return null;
  return DateFormat('yyyy-MM-dd').format(parsed.add(const Duration(days: 3)));
}

Future<void> editIncidentReport(BuildContext context,
    Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final source = normalizeRow(row ?? {});
  final fields = <EditField>[
    if (isAdd)
      EditField('employee_id', 'Employee',
          kind: FieldKind.dropdown,
          required: true,
          options: await employeeOptions()),
    const EditField('ir', 'IR', required: true),
    const EditField('date_submitted', 'Date Submitted',
        kind: FieldKind.date, required: true),
    const EditField('nte_date_received', 'NTE Date Received',
        kind: FieldKind.date, required: true),
    const EditField('nod', 'NOD'),
    const EditField('date_received', 'Date Received', kind: FieldKind.date),
  ];
  final data = await showRecordDialog(
      context, isAdd ? 'Add Incident Report' : 'Edit Incident Report', fields, source,
      readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(source));
  if (data == null) return;
  data['explanation_date_submitted'] =
      incidentReportComputedExplanationDate('${data['nte_date_received'] ?? ''}');
  await saveRow(context, 'incident_reports', isAdd ? null : source['id'], data, refresh);
}

Future<void> viewIncidentReport(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title:
          Text('Incident Report - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Incident Report Information', normalized, const {
              'Employee': 'employee_name',
              'IR': 'ir',
              'Date Submitted': 'date_submitted',
              'NTE Date Received': 'nte_date_received',
              'Explanation Date Submitted': 'explanation_date_submitted',
              'NOD': 'nod',
              'Date Received': 'date_received',
            }),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close')),
      ],
    ),
  );
}

'''
    if marker not in text:
        raise SystemExit('Could not find ReportsPage insertion point.')
    text = text.replace(marker, module + marker, 1)

if 'Future<List<dynamic>> loadIncidentReports' not in text:
    marker = 'Future<List<dynamic>> loadRankings({int limit = 1500})'
    loader = """Future<List<dynamic>> loadIncidentReports({int limit = 1500}) => db
    .from('incident_reports')
    .select(
        'id, employee_id, ir, date_submitted, nte_date_received, explanation_date_submitted, nod, date_received, employees(full_name)')
    .order('date_submitted', ascending: false)
    .limit(limit);

"""
    text = text.replace(marker, loader + marker, 1)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. IR visibility and roles may already be present.')
else:
    print('Applied IR visibility and role-based access: admin sees IR, HR hides IR, IR role sees IR only.')
