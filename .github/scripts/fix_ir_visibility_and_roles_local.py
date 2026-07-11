from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# Add lightweight role helpers. Role is read from user metadata first, then email.
# This keeps the current app simple and works with Supabase Auth users.
# -----------------------------------------------------------------------------
if 'String currentUserAccessRole()' not in text:
    marker = 'Future<void> logoutUser(BuildContext context) async {'
    helpers = r'''
String currentUserAccessRole() {
  final user = db.auth.currentUser;
  final metadata = user?.userMetadata ?? const <String, dynamic>{};
  final rawRole = '${metadata['role'] ?? metadata['access_role'] ?? ''}'
      .trim()
      .toLowerCase();
  final email = '${user?.email ?? ''}'.trim().toLowerCase();

  if (rawRole.contains('admin')) return 'admin';
  if (rawRole == 'ir' ||
      rawRole.contains('incident') ||
      rawRole.contains('incident_report')) {
    return 'ir';
  }
  if (rawRole.contains('hr')) return 'hr';

  if (email.contains('admin')) return 'admin';
  if (email.contains('incident') || email.contains('ir.')) return 'ir';
  return 'hr';
}

bool get currentUserIsAdmin => currentUserAccessRole() == 'admin';
bool get currentUserIsIncidentOnly => currentUserAccessRole() == 'ir';
bool get currentUserCanSeeIncidentReport =>
    currentUserIsAdmin || currentUserIsIncidentOnly;

'''
    if marker not in text:
        raise SystemExit('Could not find role helper insertion point.')
    text = text.replace(marker, helpers + marker, 1)

# -----------------------------------------------------------------------------
# Page list: add Incident Report after Ranking, but only for admin or IR-only.
# HR will not see IR. IR-only will see only IR.
# -----------------------------------------------------------------------------
old_pages = """    final pages = [
      DashboardPage(onNavigate: selectPage),
      const EmployeesPage(),
      const ContractsPage(),
      const CredentialsPage(),
      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
      const IncidentReportPage(),
      const ReportsPage(),
      const ResignedEmployeesPage(),
      const ArchivedPage(),
    ];"""
new_pages = """    final pages = currentUserIsIncidentOnly
        ? <Widget>[const IncidentReportPage()]
        : <Widget>[
            DashboardPage(onNavigate: selectPage),
            const EmployeesPage(),
            const ContractsPage(),
            const CredentialsPage(),
            const EvaluationsPage(),
            const AppointmentPage(),
            const RankingPage(),
            if (currentUserCanSeeIncidentReport) const IncidentReportPage(),
            const ReportsPage(),
            const ResignedEmployeesPage(),
            const ArchivedPage(),
          ];"""
if old_pages in text:
    text = text.replace(old_pages, new_pages, 1)
else:
    old_pages_without_ir = """    final pages = [
      DashboardPage(onNavigate: selectPage),
      const EmployeesPage(),
      const ContractsPage(),
      const CredentialsPage(),
      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
      const ReportsPage(),
      const ResignedEmployeesPage(),
      const ArchivedPage(),
    ];"""
    text = text.replace(old_pages_without_ir, new_pages, 1)

# -----------------------------------------------------------------------------
# Sidebar items: HR will not see IR; admin sees it; IR-only sees only IR.
# -----------------------------------------------------------------------------
old_items = """    const items = [
      NavItem('Dashboard', Icons.dashboard_rounded),
      NavItem('Employees', Icons.groups_rounded),
      NavItem('Contracts', Icons.assignment_rounded),
      NavItem('Credentials', Icons.badge_rounded),
      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Incident Report', Icons.report_problem_rounded),
      NavItem('Reports', Icons.summarize_rounded),
      NavItem('Resigned Employees', Icons.person_off_rounded),
      NavItem('Archived', Icons.archive_rounded),
    ];"""
new_items = """    final items = currentUserIsIncidentOnly
        ? const [
            NavItem('Incident Report', Icons.report_problem_rounded),
          ]
        : <NavItem>[
            const NavItem('Dashboard', Icons.dashboard_rounded),
            const NavItem('Employees', Icons.groups_rounded),
            const NavItem('Contracts', Icons.assignment_rounded),
            const NavItem('Credentials', Icons.badge_rounded),
            const NavItem('Evaluations', Icons.rate_review_rounded),
            const NavItem('Appointment', Icons.work_outline_rounded),
            const NavItem('Ranking', Icons.leaderboard_rounded),
            if (currentUserCanSeeIncidentReport)
              const NavItem('Incident Report', Icons.report_problem_rounded),
            const NavItem('Reports', Icons.summarize_rounded),
            const NavItem('Resigned Employees', Icons.person_off_rounded),
            const NavItem('Archived', Icons.archive_rounded),
          ];"""
if old_items in text:
    text = text.replace(old_items, new_items, 1)
else:
    old_items_without_ir = """    const items = [
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
    text = text.replace(old_items_without_ir, new_items, 1)

# Ensure IncidentReportPage is not accidentally duplicated in pages.
text = text.replace(
    """      const RankingPage(),
      const IncidentReportPage(),
      const IncidentReportPage(),""",
    """      const RankingPage(),
      const IncidentReportPage(),""",
)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. IR visibility and role rules may already be present.')
else:
    print('Applied IR visibility rules: admin + IR-only only; HR hidden.')
