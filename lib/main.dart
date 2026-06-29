import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment('SUPABASE_URL', defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co');
const publicClientKey = String.fromEnvironment('SUPABASE_PUBLIC_CLIENT_KEY');

const _primary = Color(0xFF2563EB);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF8FAFC);
const _surface = Color(0xFFFFFFFF);
const _soft = Color(0xFFF1F5F9);
const _line = Color(0xFFE2E8F0);
const _danger = Color(0xFFDC2626);
const _pageSize = 10;

SupabaseClient get db => Supabase.instance.client;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (publicClientKey.isNotEmpty) {
    await Supabase.initialize(url: projectUrl, anonKey: publicClientKey);
  }
  runApp(const HrApp());
}

class HrApp extends StatelessWidget {
  const HrApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'HR Monitoring',
        theme: ThemeData(
          useMaterial3: true,
          scaffoldBackgroundColor: _bg,
          colorScheme: ColorScheme.fromSeed(seedColor: _primary),
          fontFamily: 'Arial',
          cardTheme: CardThemeData(
            elevation: 0,
            color: _surface,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22), side: const BorderSide(color: _line)),
          ),
          filledButtonTheme: FilledButtonThemeData(
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF4B5FA7),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
            ),
          ),
          outlinedButtonTheme: OutlinedButtonThemeData(
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF4B5FA7),
              side: const BorderSide(color: Color(0xFFCBD5E1)),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: Colors.white,
            hintStyle: const TextStyle(color: _muted),
            labelStyle: const TextStyle(color: Color(0xFF1E40AF), fontWeight: FontWeight.w600),
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: _line)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: _line)),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: _primary, width: 1.6)),
          ),
        ),
        home: publicClientKey.isEmpty ? const SetupPage() : const ShellPage(),
      );
}

class SetupPage extends StatelessWidget {
  const SetupPage({super.key});
  @override
  Widget build(BuildContext context) => const Scaffold(
        body: Center(child: SizedBox(width: 720, child: Card(child: Padding(padding: EdgeInsets.all(28), child: Text('Start the app with your Supabase public client key using --dart-define.'))))),
      );
}

class ShellPage extends StatefulWidget {
  const ShellPage({super.key});
  @override
  State<ShellPage> createState() => _ShellPageState();
}

class _ShellPageState extends State<ShellPage> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardPage(onNavigate: (i) => setState(() => index = i)),
      const EmployeesPage(),
      const ContractsPage(),
      const CredentialsPage(),
      const EvaluationsPage(),
      const RankingPage(),
    ];
    return Scaffold(
      body: Row(children: [
        AppSidebar(selectedIndex: index, onChanged: (i) => setState(() => index = i)),
        const VerticalDivider(width: 1, color: _line),
        Expanded(child: pages[index]),
      ]),
    );
  }
}

class NavItem {
  final String label;
  final IconData icon;
  const NavItem(this.label, this.icon);
}

class AppSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;
  const AppSidebar({super.key, required this.selectedIndex, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    const items = [
      NavItem('Dashboard', Icons.dashboard_rounded),
      NavItem('Employees', Icons.groups_rounded),
      NavItem('Contracts', Icons.assignment_rounded),
      NavItem('Credentials', Icons.badge_rounded),
      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
    ];
    return Container(
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(18, 20, 18, 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(width: 44, height: 44, decoration: BoxDecoration(gradient: const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]), borderRadius: BorderRadius.circular(16), boxShadow: const [BoxShadow(color: Color(0x332563EB), blurRadius: 18, offset: Offset(0, 8))]), child: const Icon(Icons.school_rounded, color: Colors.white)),
          const SizedBox(width: 12),
          const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
        ]),
        const SizedBox(height: 7),
        const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
        const SizedBox(height: 30),
        for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
        const Spacer(),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
          child: const Text('Ranking ranks use the salary grade table. Choosing a rank can auto-fill the salary.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.35, fontWeight: FontWeight.w600)),
        ),
      ]),
    );
  }
}

class SidebarItem extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  const SidebarItem({super.key, required this.label, required this.icon, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 9),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 160),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            decoration: BoxDecoration(color: selected ? const Color(0xFFEFF6FF) : Colors.transparent, borderRadius: BorderRadius.circular(16), border: Border.all(color: selected ? const Color(0xFFDBEAFE) : Colors.transparent)),
            child: Row(children: [
              Icon(icon, color: selected ? _primary : const Color(0xFF64748B), size: 22),
              const SizedBox(width: 12),
              Text(label, style: TextStyle(fontWeight: selected ? FontWeight.w900 : FontWeight.w700, color: selected ? _primary : _ink)),
            ]),
          ),
        ),
      );
}

class PageFrame extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget child;
  const PageFrame({super.key, required this.title, required this.subtitle, required this.child});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(28, 24, 28, 28),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: const TextStyle(fontSize: 30, height: 1.08, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.7)),
          const SizedBox(height: 8),
          Text(subtitle, style: const TextStyle(color: Color(0xFF52637A), fontSize: 14, fontWeight: FontWeight.w500)),
          const SizedBox(height: 22),
          Expanded(child: child),
        ]),
      );
}

class DashboardPage extends StatelessWidget {
  final ValueChanged<int> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle: 'At-a-glance summary of imported Excel records.',
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
                Wrap(spacing: 16, runSpacing: 16, children: cards.map((m) => MetricCard(m)).toList()),
                const SizedBox(height: 24),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  QuickCard('Manage Employees', Icons.people_alt_rounded, () => onNavigate(1)),
                  QuickCard('Manage Contracts', Icons.assignment_rounded, () => onNavigate(2)),
                  QuickCard('Manage Credentials', Icons.badge_rounded, () => onNavigate(3)),
                  QuickCard('Manage Ranking', Icons.leaderboard_rounded, () => onNavigate(5)),
                ]),
              ]),
            );
          },
        ),
      );
}

class Metric {
  final String title;
  final Object? value;
  final IconData icon;
  final Color bg;
  final Color fg;
  const Metric(this.title, this.value, this.icon, this.bg, this.fg);
}

class MetricCard extends StatelessWidget {
  final Metric metric;
  const MetricCard(this.metric, {super.key});
  @override
  Widget build(BuildContext context) => SizedBox(
        width: 255,
        height: 136,
        child: Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Container(width: 42, height: 42, decoration: BoxDecoration(color: metric.bg, borderRadius: BorderRadius.circular(14)), child: Icon(metric.icon, color: metric.fg)), const Spacer(), Text('${metric.value ?? 0}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.7))]),
          const Spacer(),
          Text(metric.title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)),
        ]))),
      );
}

class QuickCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  const QuickCard(this.title, this.icon, this.onTap, {super.key});
  @override
  Widget build(BuildContext context) => SizedBox(width: 250, child: Card(child: InkWell(borderRadius: BorderRadius.circular(22), onTap: onTap, child: Padding(padding: const EdgeInsets.all(18), child: Row(children: [Icon(icon, color: _primary), const SizedBox(width: 12), Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))), const Icon(Icons.chevron_right_rounded, color: _muted)])))));
}

class EmployeesPage extends StatelessWidget {
  const EmployeesPage({super.key});
  Future<List<dynamic>> load() => db.from('employees').select('id, full_name, appointment, designation, employee_type, employment_status, current_salary, license_summary').order('full_name').limit(1500);
  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Create, edit, delete, and search employee or faculty master records.',
        child: CrudTable(
          load: load,
          searchHint: 'Search employees, appointment, status, or license',
          addLabel: 'Add Employee',
          columns: const [GridCol('full_name', 'Employee Name', flex: 3, primary: true), GridCol('appointment', 'Appointment', flex: 2), GridCol('designation', 'Designation', flex: 2), GridCol('employee_type', 'Type', flex: 1), GridCol('employment_status', 'Status', flex: 1, isStatus: true), GridCol('current_salary', 'Salary', flex: 1, isMoney: true)],
          onAdd: (ctx, refresh) => editEmployee(ctx, null, refresh),
          onEdit: (ctx, row, refresh) => editEmployee(ctx, row, refresh),
          onDelete: (row) => db.from('employees').delete().eq('id', row['id']),
        ),
      );
}

class ContractsPage extends StatelessWidget {
  const ContractsPage({super.key});
  Future<List<dynamic>> load() => db.from('employee_contracts').select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, employees(full_name)').order('contract_end_date', ascending: true).limit(1500);
  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Contracts',
        subtitle: 'Manage contract records without breaking the Excel contract monitoring flow.',
        child: CrudTable(
          load: load,
          searchHint: 'Search employee, contract type, date, or status',
          addLabel: 'Add Contract',
          columns: const [GridCol('employee_name', 'Employee Name', flex: 3, primary: true), GridCol('contract_type', 'Contract Type', flex: 2), GridCol('status', 'Status', flex: 1, isStatus: true), GridCol('contract_start_date', 'Start', flex: 1), GridCol('duration_months', 'Months', flex: 1, isNumber: true), GridCol('contract_end_date', 'End', flex: 1)],
          onAdd: (ctx, refresh) => editContract(ctx, null, refresh),
          onEdit: (ctx, row, refresh) => editContract(ctx, row, refresh),
          onDelete: (row) => db.from('employee_contracts').delete().eq('id', row['id']),
        ),
      );
}

class CredentialsPage extends StatelessWidget {
  const CredentialsPage({super.key});
  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Credentials',
        subtitle: 'Manage licenses and national certificates linked to employee records.',
        child: DefaultTabController(length: 2, child: Column(children: const [Align(alignment: Alignment.centerLeft, child: SizedBox(width: 430, child: TabBar(tabs: [Tab(text: 'Licenses'), Tab(text: 'National Certificates')]))), SizedBox(height: 16), Expanded(child: TabBarView(children: [LicensesTab(), CertificatesTab()]))])),
      );
}

class LicensesTab extends StatelessWidget {
  const LicensesTab({super.key});
  Future<List<dynamic>> load() => db.from('employee_licenses').select('id, employee_id, license_name, license_number, issued_date, expiry_date, status, employees(full_name)').order('expiry_date').limit(1500);
  @override
  Widget build(BuildContext context) => CrudTable(
        load: load,
        searchHint: 'Search employee, license name, number, or status',
        addLabel: 'Add License',
        columns: const [GridCol('employee_name', 'Employee Name', flex: 3, primary: true), GridCol('license_name', 'License', flex: 2), GridCol('license_number', 'License No.', flex: 2), GridCol('issued_date', 'Issued', flex: 1), GridCol('expiry_date', 'Expiry', flex: 1), GridCol('status', 'Status', flex: 1, isStatus: true)],
        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onEdit: (ctx, row, refresh) => editLicense(ctx, row, refresh),
        onDelete: (row) => db.from('employee_licenses').delete().eq('id', row['id']),
      );
}

class CertificatesTab extends StatelessWidget {
  const CertificatesTab({super.key});
  Future<List<dynamic>> load() => db.from('employee_certificates').select('id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, employees(full_name)').order('expiry_date').limit(1500);
  @override
  Widget build(BuildContext context) => CrudTable(
        load: load,
        searchHint: 'Search employee, certificate, number, or status',
        addLabel: 'Add Certificate',
        columns: const [GridCol('employee_name', 'Employee Name', flex: 3, primary: true), GridCol('certificate_name', 'Certificate', flex: 3), GridCol('certificate_type', 'Type', flex: 2), GridCol('certificate_number', 'Certificate No.', flex: 2), GridCol('expiry_date', 'Expiry', flex: 1), GridCol('status', 'Status', flex: 1, isStatus: true)],
        onAdd: (ctx, refresh) => editCertificate(ctx, null, refresh),
        onEdit: (ctx, row, refresh) => editCertificate(ctx, row, refresh),
        onDelete: (row) => db.from('employee_certificates').delete().eq('id', row['id']),
      );
}

class EvaluationsPage extends StatelessWidget {
  const EvaluationsPage({super.key});
  Future<List<dynamic>> load() => db.from('evaluation_records').select('id, employee_id, academic_year, semester, superior_rating, peer_rating, self_rating, student_rating, total_rating, total_description, employees(full_name)').order('academic_year').limit(1500);
  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage evaluation ratings by academic year and semester.',
        child: CrudTable(
          load: load,
          searchHint: 'Search employee, academic year, semester, or description',
          addLabel: 'Add Evaluation',
          columns: const [GridCol('employee_name', 'Employee Name', flex: 3, primary: true), GridCol('academic_year', 'A.Y.', flex: 1), GridCol('semester', 'Semester', flex: 1), GridCol('superior_rating', 'Superior', flex: 1, isNumber: true), GridCol('peer_rating', 'Peer', flex: 1, isNumber: true), GridCol('student_rating', 'Student', flex: 1, isNumber: true), GridCol('total_rating', 'Total', flex: 1, isNumber: true), GridCol('total_description', 'Description', flex: 2)],
          onAdd: (ctx, refresh) => editEvaluation(ctx, null, refresh),
          onEdit: (ctx, row, refresh) => editEvaluation(ctx, row, refresh),
          onDelete: (row) => db.from('evaluation_records').delete().eq('id', row['id']),
        ),
      );
}

class RankingPage extends StatelessWidget {
  const RankingPage({super.key});
  Future<List<dynamic>> load() => db.from('ranking_applications').select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, employees(full_name), ranking_cycles(name)').order('points_earned', ascending: false).limit(1500);
  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Ranking',
        subtitle: 'Manage faculty ranking applications. Rank dropdowns use the salary grade reference.',
        child: CrudTable(
          load: load,
          searchHint: 'Search employee, cycle, rank, or appointment',
          addLabel: 'Add Ranking',
          columns: const [GridCol('employee_name', 'Employee Name', flex: 3, primary: true), GridCol('cycle_name', 'Cycle', flex: 2), GridCol('previous_rank_text', 'Previous', flex: 2), GridCol('applied_rank_text', 'Applied', flex: 2), GridCol('points_earned', 'Points', flex: 1, isNumber: true), GridCol('approved_rank_text', 'Approved', flex: 2), GridCol('approved_salary', 'Salary', flex: 1, isMoney: true)],
          onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
          onEdit: (ctx, row, refresh) => editRanking(ctx, row, refresh),
          onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
        ),
      );
}

class GridCol {
  final String key;
  final String label;
  final int flex;
  final bool primary;
  final bool isStatus;
  final bool isMoney;
  final bool isNumber;
  const GridCol(this.key, this.label, {this.flex = 1, this.primary = false, this.isStatus = false, this.isMoney = false, this.isNumber = false});
}

typedef AddHandler = Future<void> Function(BuildContext context, VoidCallback refresh);
typedef EditHandler = Future<void> Function(BuildContext context, Map<String, dynamic> row, VoidCallback refresh);

class CrudTable extends StatefulWidget {
  final Future<List<dynamic>> Function() load;
  final String searchHint;
  final String addLabel;
  final List<GridCol> columns;
  final AddHandler onAdd;
  final EditHandler onEdit;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;
  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, required this.columns, required this.onAdd, required this.onEdit, required this.onDelete});
  @override
  State<CrudTable> createState() => _CrudTableState();
}

class _CrudTableState extends State<CrudTable> {
  late Future<List<dynamic>> future;
  String query = '';
  int page = 0;
  String? sortKey;
  bool sortAscending = true;

  @override
  void initState() {
    super.initState();
    future = widget.load();
    sortKey = widget.columns.first.key;
  }

  void refresh() => setState(() { future = widget.load(); page = 0; });
  void setSearch(String value) => setState(() { query = value; page = 0; });
  void setSort(String? value) => setState(() { sortKey = value ?? widget.columns.first.key; page = 0; });
  void toggleSortDirection() => setState(() { sortAscending = !sortAscending; page = 0; });

  @override
  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(
        future: future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
          if (snap.hasError) return ErrorBox('${snap.error}');
          final rows = snap.data?.cast<Map<String, dynamic>>() ?? [];
          final filtered = query.trim().isEmpty ? rows : rows.where((r) => searchableText(r).contains(query.toLowerCase())).toList();
          final activeSortKey = sortKey ?? widget.columns.first.key;
          final sorted = [...filtered]..sort((a, b) => compareRows(a, b, activeSortKey, sortAscending));
          final pageCount = sorted.isEmpty ? 1 : ((sorted.length - 1) ~/ _pageSize) + 1;
          final safePage = page.clamp(0, pageCount - 1).toInt();
          final startIndex = sorted.isEmpty ? 0 : safePage * _pageSize;
          final pageRows = sorted.skip(startIndex).take(_pageSize).toList();
          final endIndex = sorted.isEmpty ? 0 : startIndex + pageRows.length;
          return Column(children: [
            TableToolbar(total: rows.length, showing: sorted.length, hint: widget.searchHint, addLabel: widget.addLabel, columns: widget.columns, sortKey: activeSortKey, sortAscending: sortAscending, onSearch: setSearch, onRefresh: refresh, onAdd: () => widget.onAdd(context, refresh), onSortChanged: setSort, onToggleSortDirection: toggleSortDirection),
            const SizedBox(height: 14),
            Expanded(child: sorted.isEmpty ? const EmptyBox() : buildTable(pageRows, activeSortKey)),
            const SizedBox(height: 14),
            PaginationFooter(page: safePage, pageCount: pageCount, start: startIndex + 1, end: endIndex, total: sorted.length, onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null, onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null),
          ]);
        },
      );

  Widget buildTable(List<Map<String, dynamic>> rows, String activeSortKey) => Card(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: Column(children: [
            TableHeader(columns: widget.columns, sortKey: activeSortKey, sortAscending: sortAscending, onSort: (key) => setState(() { if (sortKey == key) { sortAscending = !sortAscending; } else { sortKey = key; sortAscending = true; } page = 0; })),
            const Divider(height: 1, color: _line),
            Expanded(child: ListView.separated(itemCount: rows.length, separatorBuilder: (_, __) => const Divider(height: 1, color: _line), itemBuilder: (_, i) => TableRowItem(row: rows[i], columns: widget.columns, index: i, onEdit: () => widget.onEdit(context, rows[i], refresh), onDelete: () => confirmDelete(context, rows[i])))),
          ]),
        ),
      );

  Future<void> confirmDelete(BuildContext context, Map<String, dynamic> row) async {
    final ok = await showDialog<bool>(context: context, builder: (_) => AlertDialog(title: const Text('Delete Record?'), content: Text('This will remove ${formatValue(valueFor(row, widget.columns.first.key))} from this module.'), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton.tonal(onPressed: () => Navigator.pop(context, true), child: const Text('Delete'))]));
    if (ok != true) return;
    try { await widget.onDelete(row); refresh(); if (mounted) showSnack(context, 'Record Deleted.'); } catch (e) { if (mounted) showSnack(context, 'Delete Failed: $e'); }
  }
}

class TableToolbar extends StatelessWidget {
  final int total;
  final int showing;
  final String hint;
  final String addLabel;
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final ValueChanged<String> onSearch;
  final VoidCallback onRefresh;
  final VoidCallback onAdd;
  final ValueChanged<String?> onSortChanged;
  final VoidCallback onToggleSortDirection;
  const TableToolbar({super.key, required this.total, required this.showing, required this.hint, required this.addLabel, required this.columns, required this.sortKey, required this.sortAscending, required this.onSearch, required this.onRefresh, required this.onAdd, required this.onSortChanged, required this.onToggleSortDirection});
  @override
  Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(12), child: LayoutBuilder(builder: (context, constraints) {
    final compact = constraints.maxWidth < 940;
    final search = SizedBox(width: compact ? constraints.maxWidth : 360, child: TextField(onChanged: onSearch, decoration: InputDecoration(prefixIcon: const Icon(Icons.search_rounded), hintText: hint, filled: true, fillColor: const Color(0xFFF8FAFC))));
    final sort = SizedBox(width: 188, child: DropdownButtonFormField<String>(value: sortKey, isExpanded: true, decoration: const InputDecoration(labelText: 'Sort By'), items: columns.map((c) => DropdownMenuItem(value: c.key, child: Text(c.label, overflow: TextOverflow.ellipsis))).toList(), onChanged: onSortChanged));
    final direction = OutlinedButton.icon(onPressed: onToggleSortDirection, icon: Icon(sortAscending ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded, size: 18), label: Text(sortAscending ? 'A-Z' : 'Z-A'));
    final count = Container(padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13), decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(999), border: Border.all(color: _line)), child: Row(mainAxisSize: MainAxisSize.min, children: [const Icon(Icons.table_rows_rounded, size: 18, color: Color(0xFF4B5FA7)), const SizedBox(width: 8), Text('$showing Of $total', style: const TextStyle(color: Color(0xFF475569), fontWeight: FontWeight.w800))]));
    final refresh = OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh_rounded), label: const Text('Refresh'));
    final add = FilledButton.icon(onPressed: onAdd, icon: const Icon(Icons.add_rounded), label: Text(addLabel));
    if (compact) return Wrap(spacing: 10, runSpacing: 10, crossAxisAlignment: WrapCrossAlignment.center, children: [search, sort, direction, count, refresh, add]);
    return Row(children: [Expanded(child: search), const SizedBox(width: 10), sort, const SizedBox(width: 10), direction, const SizedBox(width: 10), count, const SizedBox(width: 10), refresh, const SizedBox(width: 10), add]);
  })));
}

class TableHeader extends StatelessWidget {
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final ValueChanged<String> onSort;
  const TableHeader({super.key, required this.columns, required this.sortKey, required this.sortAscending, required this.onSort});
  @override
  Widget build(BuildContext context) => Container(color: const Color(0xFFF8FAFC), padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14), child: Row(children: [for (final col in columns) Expanded(flex: col.flex, child: InkWell(borderRadius: BorderRadius.circular(10), onTap: () => onSort(col.key), child: Padding(padding: const EdgeInsets.only(right: 10), child: Row(children: [Expanded(child: Text(col.label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 13))), if (sortKey == col.key) Icon(sortAscending ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded, size: 15, color: _primary)]))))), const SizedBox(width: 96, child: Text('Actions', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 13)))]));
}

class TableRowItem extends StatelessWidget {
  final Map<String, dynamic> row;
  final List<GridCol> columns;
  final int index;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  const TableRowItem({super.key, required this.row, required this.columns, required this.index, required this.onEdit, required this.onDelete});
  @override
  Widget build(BuildContext context) => Container(color: index.isEven ? Colors.white : const Color(0xFFFBFDFF), padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12), constraints: const BoxConstraints(minHeight: 62), child: Row(crossAxisAlignment: CrossAxisAlignment.center, children: [for (final col in columns) Expanded(flex: col.flex, child: Padding(padding: const EdgeInsets.only(right: 10), child: tableCell(col, valueFor(row, col.key)))), SizedBox(width: 96, child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_rounded, color: _primary, size: 20)), IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline_rounded, color: _danger, size: 20))]))]));
}

Widget tableCell(GridCol col, Object? raw) {
  if (col.isStatus) return Align(alignment: Alignment.centerLeft, child: StatusChip(formatValue(raw)));
  final text = col.isMoney ? formatMoney(raw) : col.isNumber ? formatNumber(raw) : formatValue(raw);
  return Tooltip(message: text, waitDuration: const Duration(milliseconds: 600), child: Text(text, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(fontWeight: col.primary ? FontWeight.w800 : FontWeight.w500, color: _ink, fontSize: 13, height: 1.25)));
}

class PaginationFooter extends StatelessWidget {
  final int page;
  final int pageCount;
  final int start;
  final int end;
  final int total;
  final VoidCallback? onPrevious;
  final VoidCallback? onNext;
  const PaginationFooter({super.key, required this.page, required this.pageCount, required this.start, required this.end, required this.total, this.onPrevious, this.onNext});
  @override
  Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10), child: Row(children: [Expanded(child: Text(total == 0 ? 'No Records' : 'Showing $start-$end Of $total - Page ${page + 1} Of $pageCount - 10 Per Page', style: const TextStyle(color: _muted, fontWeight: FontWeight.w800))), OutlinedButton.icon(onPressed: onPrevious, icon: const Icon(Icons.chevron_left_rounded), label: const Text('Previous')), const SizedBox(width: 8), FilledButton.icon(onPressed: onNext, icon: const Icon(Icons.chevron_right_rounded), label: const Text('Next'))])));
}

class StatusChip extends StatelessWidget {
  final String label;
  const StatusChip(this.label, {super.key});
  @override
  Widget build(BuildContext context) {
    final v = label.toLowerCase();
    Color bg = const Color(0xFFF1F5F9), fg = _ink;
    if (v.contains('active') || v.contains('ongoing') || v.contains('on-going')) { bg = const Color(0xFFDCFCE7); fg = const Color(0xFF166534); }
    if (v.contains('renewal') || v.contains('due')) { bg = const Color(0xFFFEF3C7); fg = const Color(0xFF92400E); }
    if (v.contains('expired') || v.contains('inactive') || v.contains('separated')) { bg = const Color(0xFFFEE2E2); fg = const Color(0xFF991B1B); }
    return Container(padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7), decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)), child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(color: fg, fontSize: 12, fontWeight: FontWeight.w900)));
  }
}

class ErrorBox extends StatelessWidget {
  final String message;
  const ErrorBox(this.message, {super.key});
  @override
  Widget build(BuildContext context) => Card(color: const Color(0xFFFFF7ED), child: Padding(padding: const EdgeInsets.all(18), child: Text('Unable To Load Records: $message', style: const TextStyle(color: Color(0xFF9A3412)))));
}

class EmptyBox extends StatelessWidget {
  const EmptyBox({super.key});
  @override
  Widget build(BuildContext context) => const Card(child: Center(child: Padding(padding: EdgeInsets.all(34), child: Text('No Matching Records Found.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700)))));
}

enum FieldKind { text, number, integer, date, dropdown, multiline }

class EditOption {
  final String value;
  final String label;
  final num? salary;
  const EditOption(this.value, this.label, {this.salary});
}

class EditField {
  final String key;
  final String label;
  final FieldKind kind;
  final bool required;
  final List<EditOption> options;
  final int lines;
  const EditField(this.key, this.label, {this.kind = FieldKind.text, this.required = false, this.options = const [], this.lines = 1});
}

Future<Map<String, dynamic>?> showRecordDialog(BuildContext context, String title, List<EditField> fields, Map<String, dynamic>? initial) async {
  final formKey = GlobalKey<FormState>();
  final controllers = <String, TextEditingController>{};
  final selected = <String, String?>{};
  for (final f in fields) {
    final raw = initial?[f.key]?.toString();
    if (f.kind == FieldKind.dropdown) {
      final exists = raw != null && f.options.any((o) => o.value == raw);
      selected[f.key] = exists ? raw : (f.options.isNotEmpty ? f.options.first.value : null);
    } else {
      controllers[f.key] = TextEditingController(text: formatEditValue(initial?[f.key]));
    }
  }
  final result = await showDialog<Map<String, dynamic>>(context: context, builder: (_) => StatefulBuilder(builder: (context, setDialogState) => AlertDialog(title: Text(title), content: SizedBox(width: 760, child: Form(key: formKey, child: SingleChildScrollView(child: Wrap(spacing: 14, runSpacing: 14, children: fields.map((f) {
    final width = f.kind == FieldKind.multiline ? 728.0 : 354.0;
    if (f.kind == FieldKind.dropdown) {
      return SizedBox(width: width, child: DropdownButtonFormField<String>(value: selected[f.key], isExpanded: true, decoration: InputDecoration(labelText: f.label), items: f.options.map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(), validator: (_) => f.required && (selected[f.key] == null || selected[f.key]!.isEmpty) ? 'Required' : null, onChanged: (v) => setDialogState(() => selected[f.key] = v)));
    }
    return SizedBox(width: width, child: TextFormField(controller: controllers[f.key], maxLines: f.kind == FieldKind.multiline ? f.lines : 1, keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer ? TextInputType.number : TextInputType.text, decoration: InputDecoration(labelText: f.label, hintText: f.kind == FieldKind.date ? 'YYYY-MM-DD' : null), validator: (v) => f.required && (v == null || v.trim().isEmpty) ? 'Required' : null));
  }).toList()))), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () { if (!formKey.currentState!.validate()) return; final out = <String, dynamic>{}; for (final f in fields) { if (f.kind == FieldKind.dropdown) { out[f.key] = emptyToNull(selected[f.key]); } else { out[f.key] = parseFieldValue(controllers[f.key]!.text, f.kind); } } Navigator.pop(context, out); }, child: const Text('Save'))])));
  for (final c in controllers.values) { c.dispose(); }
  return result;
}

Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(2000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['name']))).toList();
}

Future<List<EditOption>> rankOptions() async {
  final rows = await db.from('ranks').select('name, default_salary, salary_grade, point_bracket, rank_group').order('sort_order').order('name').limit(500);
  return rows.map<EditOption>((r) {
    final name = formatValue(r['name']);
    final salary = num.tryParse('${r['default_salary'] ?? ''}');
    final sg = r['salary_grade'] == null ? '' : ' - SG ${r['salary_grade']}';
    final pay = salary == null ? '' : ' - ${formatMoney(salary)}';
    return EditOption(name, '$name$sg$pay', salary: salary);
  }).toList();
}

Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showRecordDialog(context, row == null ? 'Add Employee' : 'Edit Employee', const [EditField('full_name', 'Full Name', required: true), EditField('appointment', 'Appointment'), EditField('designation', 'Designation'), EditField('employee_type', 'Employee Type', kind: FieldKind.dropdown, options: [EditOption('full_time', 'Full Time'), EditOption('probationary', 'Probationary'), EditOption('part_time', 'Part Time'), EditOption('staff', 'Staff'), EditOption('faculty_staff', 'Faculty / Staff')]), EditField('employment_status', 'Employment Status', kind: FieldKind.dropdown, options: [EditOption('active', 'Active'), EditOption('inactive', 'Inactive'), EditOption('separated', 'Separated')]), EditField('current_salary', 'Current Salary', kind: FieldKind.number), EditField('license_summary', 'License Summary')], row);
  if (data == null) return;
  data['name_key'] = normalizeName(data['full_name']?.toString() ?? '');
  await saveRow(context, 'employees', row?['id'], data, refresh);
}

Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add Contract' : 'Edit Contract', [EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees), const EditField('contract_type', 'Contract Type'), const EditField('contract_start_date', 'Start Date', kind: FieldKind.date), const EditField('duration_months', 'Duration In Months', kind: FieldKind.integer), const EditField('contract_end_date', 'End Date', kind: FieldKind.date), const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')])], row);
  if (data == null) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}

Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add License' : 'Edit License', [EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees), const EditField('license_name', 'License Name', required: true), const EditField('license_number', 'License Number'), const EditField('issued_date', 'Issued Date', kind: FieldKind.date), const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date), const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')])], row);
  if (data == null) return;
  await saveRow(context, 'employee_licenses', row?['id'], data, refresh);
}

Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add Certificate' : 'Edit Certificate', [EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees), const EditField('certificate_type', 'Certificate Type'), const EditField('certificate_name', 'Certificate Name', required: true), const EditField('certificate_number', 'Certificate Number'), const EditField('issued_date', 'Issued Date', kind: FieldKind.date), const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date), const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')])], row);
  if (data == null) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row?['id'], data, refresh);
}

Future<void> editEvaluation(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add Evaluation' : 'Edit Evaluation', [EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees), const EditField('academic_year', 'Academic Year', required: true), const EditField('semester', 'Semester', required: true), const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number), const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number), const EditField('self_rating', 'Self Rating', kind: FieldKind.number), const EditField('student_rating', 'Student Rating', kind: FieldKind.number), const EditField('total_rating', 'Total Rating', kind: FieldKind.number), const EditField('total_description', 'Total Description', kind: FieldKind.multiline, lines: 3)], row);
  if (data == null) return;
  await saveRow(context, 'evaluation_records', row?['id'], data, refresh);
}

Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final cycles = await cycleOptions();
  final ranks = await rankOptions();
  final data = await showRankingDialog(context, row == null ? 'Add Ranking Record' : 'Edit Ranking Record', employees, cycles, ranks, row);
  if (data == null) return;
  await saveRow(context, 'ranking_applications', row?['id'], data, refresh);
}

Future<Map<String, dynamic>?> showRankingDialog(BuildContext context, String title, List<EditOption> employees, List<EditOption> cycles, List<EditOption> ranks, Map<String, dynamic>? initial) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId = initial?['employee_id']?.toString();
  String? cycleId = initial?['cycle_id']?.toString();
  String? previousRank = normalizedRankValue(initial?['previous_rank_text']);
  String? appliedRank = normalizedRankValue(initial?['applied_rank_text']);
  String? approvedRank = normalizedRankValue(initial?['approved_rank_text']);
  final appointment = TextEditingController(text: formatEditValue(initial?['appointment']));
  final previousSalary = TextEditingController(text: formatEditValue(initial?['previous_salary']));
  final appliedSalary = TextEditingController(text: formatEditValue(initial?['applied_salary']));
  final approvedSalary = TextEditingController(text: formatEditValue(initial?['approved_salary']));
  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));
  final rankChoices = withBlankAndExisting(ranks, [previousRank, appliedRank, approvedRank]);

  void applySalary(String? rank, TextEditingController target) {
    final selected = ranks.where((r) => r.value.toLowerCase() == (rank ?? '').toLowerCase()).toList();
    if (selected.isNotEmpty && selected.first.salary != null) target.text = selected.first.salary!.toStringAsFixed(2);
  }

  Widget selectBox(String label, String? value, List<EditOption> options, bool required, ValueChanged<String?> onChanged) => SizedBox(
        width: 354,
        child: DropdownButtonFormField<String>(
          value: value != null && options.any((o) => o.value == value) ? value : (required && options.isNotEmpty ? options.first.value : ''),
          isExpanded: true,
          decoration: InputDecoration(labelText: label),
          items: options.map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
          validator: (_) => required && (value == null || value.isEmpty) ? 'Required' : null,
          onChanged: onChanged,
        ),
      );

  Widget textBox(String label, TextEditingController controller, {FieldKind kind = FieldKind.text}) => SizedBox(
        width: 354,
        child: TextFormField(controller: controller, keyboardType: kind == FieldKind.number ? TextInputType.number : TextInputType.text, decoration: InputDecoration(labelText: label)),
      );

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(builder: (context, setDialogState) => AlertDialog(
          title: Text(title),
          content: SizedBox(
            width: 760,
            child: Form(
              key: formKey,
              child: SingleChildScrollView(
                child: Wrap(spacing: 14, runSpacing: 14, children: [
                  selectBox('Employee', employeeId, employees, true, (v) => setDialogState(() => employeeId = v)),
                  selectBox('Ranking Cycle', cycleId, cycles, true, (v) => setDialogState(() => cycleId = v)),
                  textBox('Appointment', appointment),
                  const SizedBox(width: 354),
                  selectBox('Previous Rank', previousRank, rankChoices, false, (v) => setDialogState(() { previousRank = emptyToNull(v); applySalary(previousRank, previousSalary); })),
                  textBox('Previous Salary', previousSalary, kind: FieldKind.number),
                  selectBox('Applied Rank', appliedRank, rankChoices, false, (v) => setDialogState(() { appliedRank = emptyToNull(v); applySalary(appliedRank, appliedSalary); })),
                  textBox('Applied Salary', appliedSalary, kind: FieldKind.number),
                  textBox('Points Earned', points, kind: FieldKind.number),
                  const SizedBox(width: 354),
                  selectBox('Approved Rank', approvedRank, rankChoices, false, (v) => setDialogState(() { approvedRank = emptyToNull(v); applySalary(approvedRank, approvedSalary); })),
                  textBox('Approved Salary (Auto)', approvedSalary, kind: FieldKind.number),
                  SizedBox(width: 728, child: Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)), child: const Text('Tip: Selecting Previous, Applied, or Approved Rank automatically fills the matching salary using the Salary Grade For Faculty And Staff reference.', style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)))),
                ]),
              ),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            FilledButton(onPressed: () {
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, {
                'employee_id': emptyToNull(employeeId),
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text.trim()),
                'previous_rank_text': emptyToNull(previousRank),
                'previous_salary': num.tryParse(previousSalary.text.trim()),
                'applied_rank_text': emptyToNull(appliedRank),
                'applied_salary': num.tryParse(appliedSalary.text.trim()),
                'points_earned': num.tryParse(points.text.trim()),
                'approved_rank_text': emptyToNull(approvedRank),
                'approved_salary': num.tryParse(approvedSalary.text.trim()),
              });
            }, child: const Text('Save')),
          ],
        )),
  );
  for (final c in [appointment, previousSalary, appliedSalary, approvedSalary, points]) { c.dispose(); }
  return result;
}

List<EditOption> withBlankAndExisting(List<EditOption> base, List<String?> existing) {
  final out = <EditOption>[const EditOption('', '-')];
  out.addAll(base);
  for (final value in existing) {
    if (value != null && value.trim().isNotEmpty && !out.any((o) => o.value.toLowerCase() == value.toLowerCase())) out.add(EditOption(value, value));
  }
  return out;
}

String? normalizedRankValue(Object? value) {
  final v = formatValue(value);
  return v == '-' ? null : v;
}

Future<void> saveRow(BuildContext context, String table, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) { await db.from(table).insert(data); showSnack(context, 'Record Added.'); } else { await db.from(table).update(data).eq('id', id); showSnack(context, 'Record Updated.'); }
    refresh();
  } catch (e) { showSnack(context, 'Save Failed: $e'); }
}

Object? parseFieldValue(String text, FieldKind kind) {
  final t = text.trim();
  if (t.isEmpty) return null;
  if (kind == FieldKind.number) return num.tryParse(t);
  if (kind == FieldKind.integer) return int.tryParse(t);
  return t;
}

String? emptyToNull(String? value) => value == null || value.trim().isEmpty ? null : value.trim();
void showSnack(BuildContext context, String message) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));

Object? valueFor(Map<String, dynamic> row, String key) {
  if (key == 'employee_name') return row['employees'] is Map ? row['employees']['full_name'] : null;
  if (key == 'cycle_name') return row['ranking_cycles'] is Map ? row['ranking_cycles']['name'] : null;
  return row[key];
}

int compareRows(Map<String, dynamic> a, Map<String, dynamic> b, String key, bool ascending) {
  final result = compareValues(valueFor(a, key), valueFor(b, key));
  return ascending ? result : -result;
}

int compareValues(Object? a, Object? b) {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  final na = num.tryParse(a.toString());
  final nb = num.tryParse(b.toString());
  if (na != null && nb != null) return na.compareTo(nb);
  final da = DateTime.tryParse(a.toString());
  final dbb = DateTime.tryParse(b.toString());
  if (da != null && dbb != null) return da.compareTo(dbb);
  return formatValue(a).toLowerCase().compareTo(formatValue(b).toLowerCase());
}

String searchableText(Map<String, dynamic> row) {
  final values = <String>[];
  void walk(Object? v) { if (v == null) return; if (v is Map) { for (final x in v.values) { walk(x); } } else { values.add(formatValue(v).toLowerCase()); } }
  walk(row);
  return values.join(' ');
}

String formatEditValue(Object? value) {
  if (value == null) return '';
  final text = value.toString();
  return text == 'null' ? '' : text;
}

String normalizeName(String value) => value.trim().replaceAll(RegExp(r'\s+'), ' ').toUpperCase();

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString().trim();
  if (text.isEmpty || text.toLowerCase() == 'null') return '-';
  final date = DateTime.tryParse(text);
  if (date != null && text.contains('-')) return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  return toTitleCase(text.replaceAll('_', ' ').replaceAll(RegExp(r'\s+'), ' '));
}

String toTitleCase(String input) {
  final acronyms = <String, String>{'LPT': 'LPT', 'MAED': 'MAED', 'MAT': 'MAT', 'MA': 'MA', 'MBA': 'MBA', 'MIT': 'MIT', 'PHD': 'PhD', 'NC': 'NC', 'PRC': 'PRC', 'HR': 'HR', 'MIS': 'MIS', 'OAA': 'OAA', 'OSA': 'OSA', 'TESDA': 'TESDA', 'CBIT': 'CBIT', 'CRIM': 'CRIM', 'CSSH': 'CSSH', 'GAD': 'GAD', 'SDS': 'SDS', 'BPE': 'BPE', 'MSCRIM': 'MSCRIM', 'RCRIM': 'RCRIM'};
  return input.split(' ').map((word) { if (word.isEmpty) return word; final clean = word.replaceAll(RegExp(r'[^A-Za-z0-9]'), '').toUpperCase(); if (acronyms.containsKey(clean)) return word.toUpperCase().replaceFirst(clean, acronyms[clean]!); if (RegExp(r'^[IVXLCM]+$').hasMatch(clean)) return word.toUpperCase(); return word.split('-').map(capitalizeWord).join('-'); }).join(' ');
}

String capitalizeWord(String word) {
  if (word.isEmpty) return word;
  if (word.length == 1) return word.toUpperCase();
  return word[0].toUpperCase() + word.substring(1).toLowerCase();
}

String formatNumber(Object? value) {
  final n = num.tryParse(value?.toString() ?? '');
  if (n == null) return '-';
  return n % 1 == 0 ? n.toInt().toString() : n.toStringAsFixed(2);
}

String formatMoney(Object? value) {
  final n = num.tryParse(value?.toString() ?? '');
  if (n == null) return '-';
  final s = n.toStringAsFixed(2).split('.');
  final whole = s.first.replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',');
  return 'PHP $whole.${s.last}';
}
