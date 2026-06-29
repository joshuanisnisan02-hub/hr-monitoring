// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment(
  'SUPABASE_URL',
  defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co',
);
const publicClientKey = String.fromEnvironment('SUPABASE_PUBLIC_CLIENT_KEY');

const _primary = Color(0xFF2563EB);
const _accent = Color(0xFF4B5FA7);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF8FAFC);
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
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HR Monitoring',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: _bg,
        colorScheme: ColorScheme.fromSeed(seedColor: _primary),
        fontFamily: 'Arial',
        cardTheme: CardThemeData(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
            side: const BorderSide(color: _line),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: _accent,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: _accent,
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
}

class SetupPage extends StatelessWidget {
  const SetupPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: SizedBox(
          width: 720,
          child: Card(
            child: Padding(
              padding: EdgeInsets.all(28),
              child: Text('Start the app with your Supabase public client key using --dart-define.'),
            ),
          ),
        ),
      ),
    );
  }
}

class NavItem {
  final String label;
  final IconData icon;
  const NavItem(this.label, this.icon);
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
      const ReportsPage(),
    ];

    return Scaffold(
      body: Row(
        children: [
          AppSidebar(selectedIndex: index, onChanged: (i) => setState(() => index = i)),
          const VerticalDivider(width: 1, color: _line),
          Expanded(child: pages[index]),
        ],
      ),
    );
  }
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
      NavItem('Reports', Icons.print_rounded),
    ];

    return Container(
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(18, 20, 18, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [BoxShadow(color: Color(0x332563EB), blurRadius: 18, offset: Offset(0, 8))],
                ),
                child: const Icon(Icons.school_rounded, color: Colors.white),
              ),
              const SizedBox(width: 12),
              const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
            ],
          ),
          const SizedBox(height: 7),
          const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 30),
          for (var i = 0; i < items.length; i++)
            SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
            child: const Text(
              'Duplicate linked employee records are prevented when adding module records.',
              style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.35, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
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
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
          decoration: BoxDecoration(
            color: selected ? const Color(0xFFEFF6FF) : Colors.transparent,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: selected ? const Color(0xFFDBEAFE) : Colors.transparent),
          ),
          child: Row(
            children: [
              Icon(icon, color: selected ? _primary : const Color(0xFF64748B), size: 22),
              const SizedBox(width: 12),
              Text(label, style: TextStyle(fontWeight: selected ? FontWeight.w900 : FontWeight.w700, color: selected ? _primary : _ink)),
            ],
          ),
        ),
      ),
    );
  }
}

class PageFrame extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget child;

  const PageFrame({super.key, required this.title, required this.subtitle, required this.child});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(28, 24, 28, 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 30, height: 1.08, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.7)),
          const SizedBox(height: 8),
          Text(subtitle, style: const TextStyle(color: Color(0xFF52637A), fontSize: 14, fontWeight: FontWeight.w500)),
          const SizedBox(height: 22),
          Expanded(child: child),
        ],
      ),
    );
  }
}

Future<List<dynamic>> loadEmployees({int limit = 1500}) => db.from('employees').select('id, full_name, appointment, designation, employee_type, employment_status, current_salary, license_summary').order('full_name').limit(limit);
Future<List<dynamic>> loadContracts({int limit = 1500}) => db.from('employee_contracts').select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, employees(full_name)').order('contract_end_date', ascending: true).limit(limit);
Future<List<dynamic>> loadLicenses({int limit = 1500}) => db.from('employee_licenses').select('id, employee_id, license_name, license_number, issued_date, expiry_date, status, employees(full_name)').order('expiry_date').limit(limit);
Future<List<dynamic>> loadCertificates({int limit = 1500}) => db.from('employee_certificates').select('id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, employees(full_name)').order('expiry_date').limit(limit);
Future<List<dynamic>> loadEvaluations({int limit = 1500}) => db.from('evaluation_records').select('id, employee_id, academic_year, semester, superior_rating, peer_rating, self_rating, student_rating, total_rating, total_description, employees(full_name)').order('academic_year').limit(limit);
Future<List<dynamic>> loadRankings({int limit = 1500}) => db.from('ranking_applications').select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, employees(full_name), ranking_cycles(name)').order('points_earned', ascending: false).limit(limit);

class DashboardPage extends StatelessWidget {
  final ValueChanged<int> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) {
    return PageFrame(
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
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(spacing: 16, runSpacing: 16, children: cards.map((m) => MetricCard(m)).toList()),
                const SizedBox(height: 24),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  QuickCard('Manage Employees', Icons.people_alt_rounded, () => onNavigate(1)),
                  QuickCard('Manage Contracts', Icons.assignment_rounded, () => onNavigate(2)),
                  QuickCard('Manage Credentials', Icons.badge_rounded, () => onNavigate(3)),
                  QuickCard('Print Reports', Icons.print_rounded, () => onNavigate(6)),
                ]),
              ],
            ),
          );
        },
      ),
    );
  }
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
  Widget build(BuildContext context) {
    return SizedBox(
      width: 255,
      height: 136,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Container(width: 42, height: 42, decoration: BoxDecoration(color: metric.bg, borderRadius: BorderRadius.circular(14)), child: Icon(metric.icon, color: metric.fg)),
                const Spacer(),
                Text('${metric.value ?? 0}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.7)),
              ]),
              const Spacer(),
              Text(metric.title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)),
            ],
          ),
        ),
      ),
    );
  }
}

class QuickCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  const QuickCard(this.title, this.icon, this.onTap, {super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 250,
      child: Card(
        child: InkWell(
          borderRadius: BorderRadius.circular(22),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Row(children: [
              Icon(icon, color: _primary),
              const SizedBox(width: 12),
              Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
              const Icon(Icons.chevron_right_rounded, color: _muted),
            ]),
          ),
        ),
      ),
    );
  }
}

class EmployeesPage extends StatelessWidget {
  const EmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Create, edit, delete, and search employee or faculty master records.',
        child: CrudTable(
          load: () => loadEmployees(),
          searchHint: 'Search employees, appointment, status, or license',
          addLabel: 'Add Employee',
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('appointment', 'Appointment', flex: 2),
            GridCol('designation', 'Designation', flex: 2),
            GridCol('employee_type', 'Type'),
            GridCol('employment_status', 'Status', isStatus: true),
            GridCol('current_salary', 'Salary', isMoney: true),
          ],
          onAdd: (ctx, refresh) => editEmployee(ctx, null, refresh),
          onEdit: editEmployee,
          onDelete: (row) => db.from('employees').delete().eq('id', row['id']),
        ),
      );
}

class ContractsPage extends StatelessWidget {
  const ContractsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Contracts',
        subtitle: 'Manage contract records with dynamic total days left.',
        child: CrudTable(
          load: () => loadContracts(),
          searchHint: 'Search employee, contract type, date, or status',
          addLabel: 'Add Contract',
          columns: const [
            GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            GridCol('contract_type', 'Contract Type', flex: 2),
            GridCol('status', 'Status', isStatus: true),
            GridCol('contract_start_date', 'Start'),
            GridCol('duration_months', 'Months', isNumber: true),
            GridCol('contract_end_date', 'End'),
            GridCol('days_left', 'Days Left', isNumber: true),
          ],
          onAdd: (ctx, refresh) => editContract(ctx, null, refresh),
          onEdit: editContract,
          onDelete: (row) => db.from('employee_contracts').delete().eq('id', row['id']),
        ),
      );
}

class CredentialsPage extends StatelessWidget {
  const CredentialsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Credentials',
        subtitle: 'Manage licenses and national certificates linked to employees.',
        child: DefaultTabController(
          length: 2,
          child: Column(children: const [
            Align(alignment: Alignment.centerLeft, child: SizedBox(width: 430, child: TabBar(tabs: [Tab(text: 'Licenses'), Tab(text: 'National Certificates')]))),
            SizedBox(height: 16),
            Expanded(child: TabBarView(children: [LicensesTab(), CertificatesTab()])),
          ]),
        ),
      );
}

class LicensesTab extends StatelessWidget {
  const LicensesTab({super.key});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => loadLicenses(),
        searchHint: 'Search employee, license name, number, or status',
        addLabel: 'Add License',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('license_name', 'License', flex: 2),
          GridCol('license_number', 'License No.', flex: 2),
          GridCol('issued_date', 'Issued'),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onEdit: editLicense,
        onDelete: (row) => db.from('employee_licenses').delete().eq('id', row['id']),
      );
}

class CertificatesTab extends StatelessWidget {
  const CertificatesTab({super.key});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => loadCertificates(),
        searchHint: 'Search employee, certificate, number, or status',
        addLabel: 'Add Certificate',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('certificate_name', 'Certificate', flex: 3),
          GridCol('certificate_type', 'Type', flex: 2),
          GridCol('certificate_number', 'Certificate No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editCertificate(ctx, null, refresh),
        onEdit: editCertificate,
        onDelete: (row) => db.from('employee_certificates').delete().eq('id', row['id']),
      );
}

class EvaluationsPage extends StatelessWidget {
  const EvaluationsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage evaluation ratings by academic year and semester.',
        child: CrudTable(
          load: () => loadEvaluations(),
          searchHint: 'Search employee, academic year, semester, or description',
          addLabel: 'Add Evaluation',
          columns: const [
            GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            GridCol('academic_year', 'A.Y.'),
            GridCol('semester', 'Semester'),
            GridCol('superior_rating', 'Superior', isNumber: true),
            GridCol('peer_rating', 'Peer', isNumber: true),
            GridCol('student_rating', 'Student', isNumber: true),
            GridCol('total_rating', 'Total', isNumber: true),
            GridCol('total_description', 'Description', flex: 2),
          ],
          onAdd: (ctx, refresh) => editEvaluation(ctx, null, refresh),
          onEdit: editEvaluation,
          onDelete: (row) => db.from('evaluation_records').delete().eq('id', row['id']),
        ),
      );
}

class RankingPage extends StatelessWidget {
  const RankingPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Ranking',
        subtitle: 'Manage faculty ranking applications. Employee name is read-only when editing existing records.',
        child: CrudTable(
          load: () => loadRankings(),
          searchHint: 'Search employee, cycle, rank, or appointment',
          addLabel: 'Add Ranking',
          columns: const [
            GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            GridCol('cycle_name', 'Cycle', flex: 2),
            GridCol('previous_rank_text', 'Previous', flex: 2),
            GridCol('applied_rank_text', 'Applied', flex: 2),
            GridCol('points_earned', 'Points', isNumber: true),
            GridCol('approved_rank_text', 'Approved', flex: 2),
            GridCol('approved_salary', 'Salary', isMoney: true),
          ],
          onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
          onEdit: editRanking,
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
  final bool allowAdd;
  final List<GridCol> columns;
  final AddHandler? onAdd;
  final EditHandler onEdit;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, this.allowAdd = true, required this.columns, this.onAdd, required this.onEdit, required this.onDelete});

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

  void refresh() => setState(() {
        future = widget.load();
        page = 0;
      });

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: future,
      builder: (context, snap) {
        if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
        if (snap.hasError) return ErrorBox('${snap.error}');

        final rows = (snap.data ?? []).map((item) => Map<String, dynamic>.from(item as Map)).toList();
        final filtered = query.trim().isEmpty ? rows : rows.where((row) => searchableText(row).contains(query.toLowerCase())).toList();
        final activeSortKey = sortKey ?? widget.columns.first.key;
        final sorted = [...filtered]..sort((a, b) => compareRows(a, b, activeSortKey, sortAscending));
        final pageCount = sorted.isEmpty ? 1 : ((sorted.length - 1) ~/ _pageSize) + 1;
        final safePage = page.clamp(0, pageCount - 1).toInt();
        final startIndex = sorted.isEmpty ? 0 : safePage * _pageSize;
        final pageRows = sorted.skip(startIndex).take(_pageSize).toList();
        final endIndex = sorted.isEmpty ? 0 : startIndex + pageRows.length;

        return Column(children: [
          TableToolbar(
            total: rows.length,
            showing: sorted.length,
            hint: widget.searchHint,
            addLabel: widget.addLabel,
            allowAdd: widget.allowAdd && widget.onAdd != null,
            columns: widget.columns,
            sortKey: activeSortKey,
            sortAscending: sortAscending,
            onSearch: (value) => setState(() {
              query = value;
              page = 0;
            }),
            onRefresh: refresh,
            onAdd: widget.onAdd == null ? null : () => widget.onAdd!(context, refresh),
            onSortChanged: (value) => setState(() {
              sortKey = value ?? widget.columns.first.key;
              page = 0;
            }),
            onToggleSortDirection: () => setState(() {
              sortAscending = !sortAscending;
              page = 0;
            }),
          ),
          const SizedBox(height: 14),
          Expanded(child: sorted.isEmpty ? const EmptyBox() : buildTable(pageRows, activeSortKey)),
          const SizedBox(height: 14),
          PaginationFooter(
            page: safePage,
            pageCount: pageCount,
            start: startIndex + 1,
            end: endIndex,
            total: sorted.length,
            onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null,
            onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null,
          ),
        ]);
      },
    );
  }

  Widget buildTable(List<Map<String, dynamic>> rows, String activeSortKey) {
    return Card(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: Column(children: [
          TableHeader(columns: widget.columns, sortKey: activeSortKey, sortAscending: sortAscending, showActions: true, onSort: (key) {
            setState(() {
              if (sortKey == key) {
                sortAscending = !sortAscending;
              } else {
                sortKey = key;
                sortAscending = true;
              }
              page = 0;
            });
          }),
          const Divider(height: 1, color: _line),
          Expanded(
            child: ListView.separated(
              itemCount: rows.length,
              separatorBuilder: (_, __) => const Divider(height: 1, color: _line),
              itemBuilder: (_, i) => TableRowItem(row: rows[i], columns: widget.columns, index: i, onEdit: () => widget.onEdit(context, rows[i], refresh), onDelete: () => confirmDelete(context, rows[i])),
            ),
          ),
        ]),
      ),
    );
  }

  Future<void> confirmDelete(BuildContext context, Map<String, dynamic> row) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Delete Record?'),
        content: Text('This will remove ${formatValue(valueFor(row, widget.columns.first.key))} from this module.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton.tonal(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await widget.onDelete(row);
      refresh();
      if (mounted) showSnack(context, 'Record Deleted.');
    } catch (e) {
      if (mounted) showSnack(context, 'Delete Failed: $e');
    }
  }
}

class TableToolbar extends StatelessWidget {
  final int total;
  final int showing;
  final String hint;
  final String addLabel;
  final bool allowAdd;
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final ValueChanged<String> onSearch;
  final VoidCallback onRefresh;
  final VoidCallback? onAdd;
  final ValueChanged<String?> onSortChanged;
  final VoidCallback onToggleSortDirection;

  const TableToolbar({super.key, required this.total, required this.showing, required this.hint, required this.addLabel, required this.allowAdd, required this.columns, required this.sortKey, required this.sortAscending, required this.onSearch, required this.onRefresh, required this.onAdd, required this.onSortChanged, required this.onToggleSortDirection});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: LayoutBuilder(builder: (context, constraints) {
          final compact = constraints.maxWidth < 940;
          final search = SizedBox(
            width: compact ? constraints.maxWidth : 360,
            child: TextField(onChanged: onSearch, decoration: InputDecoration(prefixIcon: const Icon(Icons.search_rounded), hintText: hint, filled: true, fillColor: const Color(0xFFF8FAFC))),
          );
          final sort = SizedBox(
            width: 188,
            child: DropdownButtonFormField<String>(value: sortKey, isExpanded: true, decoration: const InputDecoration(labelText: 'Sort By'), items: columns.map((c) => DropdownMenuItem(value: c.key, child: Text(c.label, overflow: TextOverflow.ellipsis))).toList(), onChanged: onSortChanged),
          );
          final widgets = <Widget>[
            search,
            sort,
            OutlinedButton.icon(onPressed: onToggleSortDirection, icon: Icon(sortAscending ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded, size: 18), label: Text(sortAscending ? 'A-Z' : 'Z-A')),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
              decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(999), border: Border.all(color: _line)),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                const Icon(Icons.table_rows_rounded, size: 18, color: _accent),
                const SizedBox(width: 8),
                Text('$showing Of $total', style: const TextStyle(color: Color(0xFF475569), fontWeight: FontWeight.w800)),
              ]),
            ),
            OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh_rounded), label: const Text('Refresh')),
          ];
          if (allowAdd && onAdd != null) widgets.add(FilledButton.icon(onPressed: onAdd, icon: const Icon(Icons.add_rounded), label: Text(addLabel)));
          if (compact) return Wrap(spacing: 10, runSpacing: 10, crossAxisAlignment: WrapCrossAlignment.center, children: widgets);
          return Row(children: [Expanded(child: search), for (final w in widgets.skip(1)) ...[const SizedBox(width: 10), w]]);
        }),
      ),
    );
  }
}

class TableHeader extends StatelessWidget {
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final bool showActions;
  final ValueChanged<String> onSort;

  const TableHeader({super.key, required this.columns, required this.sortKey, required this.sortAscending, required this.showActions, required this.onSort});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFFF8FAFC),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(children: [
        for (final col in columns)
          Expanded(
            flex: col.flex,
            child: InkWell(
              borderRadius: BorderRadius.circular(10),
              onTap: () => onSort(col.key),
              child: Padding(
                padding: const EdgeInsets.only(right: 10),
                child: Row(children: [
                  Expanded(child: Text(col.label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 13))),
                  if (sortKey == col.key) Icon(sortAscending ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded, size: 15, color: _primary),
                ]),
              ),
            ),
          ),
        if (showActions) const SizedBox(width: 96, child: Text('Actions', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 13))),
      ]),
    );
  }
}

class TableRowItem extends StatelessWidget {
  final Map<String, dynamic> row;
  final List<GridCol> columns;
  final int index;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const TableRowItem({super.key, required this.row, required this.columns, required this.index, required this.onEdit, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: index.isEven ? Colors.white : const Color(0xFFFBFDFF),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      constraints: const BoxConstraints(minHeight: 62),
      child: Row(crossAxisAlignment: CrossAxisAlignment.center, children: [
        for (final col in columns) Expanded(flex: col.flex, child: Padding(padding: const EdgeInsets.only(right: 10), child: tableCell(col, valueFor(row, col.key)))),
        SizedBox(width: 96, child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_rounded, color: _primary, size: 20)),
          IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline_rounded, color: _danger, size: 20)),
        ])),
      ]),
    );
  }
}

Widget tableCell(GridCol col, Object? raw) {
  if (col.isStatus) return Align(alignment: Alignment.centerLeft, child: StatusChip(formatValue(raw)));
  final text = col.isMoney ? formatMoney(raw) : col.isNumber ? formatNumber(raw) : formatValue(raw);
  return Tooltip(
    message: text,
    waitDuration: const Duration(milliseconds: 600),
    child: Text(text, maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(fontWeight: col.primary ? FontWeight.w800 : FontWeight.w500, color: _ink, fontSize: 13, height: 1.25)),
  );
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
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Row(children: [
          Expanded(child: Text(total == 0 ? 'No Records' : 'Showing $start-$end Of $total - Page ${page + 1} Of $pageCount - 10 Per Page', style: const TextStyle(color: _muted, fontWeight: FontWeight.w800))),
          OutlinedButton.icon(onPressed: onPrevious, icon: const Icon(Icons.chevron_left_rounded), label: const Text('Previous')),
          const SizedBox(width: 8),
          FilledButton.icon(onPressed: onNext, icon: const Icon(Icons.chevron_right_rounded), label: const Text('Next')),
        ]),
      ),
    );
  }
}

class StatusChip extends StatelessWidget {
  final String label;
  const StatusChip(this.label, {super.key});

  @override
  Widget build(BuildContext context) {
    final v = label.toLowerCase();
    Color bg = const Color(0xFFF1F5F9);
    Color fg = _ink;
    if (v.contains('active') || v.contains('ongoing') || v.contains('on-going')) {
      bg = const Color(0xFFDCFCE7);
      fg = const Color(0xFF166534);
    }
    if (v.contains('renewal') || v.contains('due')) {
      bg = const Color(0xFFFEF3C7);
      fg = const Color(0xFF92400E);
    }
    if (v.contains('expired') || v.contains('inactive') || v.contains('separated')) {
      bg = const Color(0xFFFEE2E2);
      fg = const Color(0xFF991B1B);
    }
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

class ReadOnlyEmployeeBox extends StatelessWidget {
  final String employeeName;
  const ReadOnlyEmployeeBox(this.employeeName, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 728,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Employee Name', style: TextStyle(color: Color(0xFF1E40AF), fontWeight: FontWeight.w700, fontSize: 12)),
            const SizedBox(height: 4),
            Text(employeeName, style: const TextStyle(color: _ink, fontSize: 15, fontWeight: FontWeight.w800)),
          ]),
        ),
      );
}

Future<Map<String, dynamic>?> showRecordDialog(BuildContext context, String title, List<EditField> fields, Map<String, dynamic>? initial, {String? readOnlyEmployeeName}) async {
  final formKey = GlobalKey<FormState>();
  final controllers = <String, TextEditingController>{};
  final selected = <String, String?>{};

  for (final f in fields) {
    final raw = initial?[f.key]?.toString();
    if (f.kind == FieldKind.dropdown) {
      selected[f.key] = optionValueOrFirst(raw, f.options, f.required);
    } else {
      controllers[f.key] = TextEditingController(text: formatEditValue(initial?[f.key]));
    }
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(title),
        content: SizedBox(
          width: 760,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(
                spacing: 14,
                runSpacing: 14,
                children: [
                  if (readOnlyEmployeeName != null) ReadOnlyEmployeeBox(readOnlyEmployeeName),
                  ...fields.map((f) {
                    final width = f.kind == FieldKind.multiline ? 728.0 : 354.0;
                    if (f.kind == FieldKind.dropdown) {
                      final opts = uniqueOptions(f.options);
                      return SizedBox(
                        width: width,
                        child: DropdownButtonFormField<String>(
                          value: optionValueOrFirst(selected[f.key], opts, f.required),
                          isExpanded: true,
                          decoration: InputDecoration(labelText: f.label),
                          items: opts.map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                          validator: (v) => f.required && (v == null || v.isEmpty) ? 'Required' : null,
                          onChanged: (v) => setDialogState(() => selected[f.key] = v),
                        ),
                      );
                    }
                    return SizedBox(
                      width: width,
                      child: TextFormField(
                        controller: controllers[f.key],
                        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
                        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer ? TextInputType.number : TextInputType.text,
                        decoration: InputDecoration(labelText: f.label, hintText: f.kind == FieldKind.date ? 'YYYY-MM-DD' : null),
                        validator: (v) => f.required && (v == null || v.trim().isEmpty) ? 'Required' : null,
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              final out = <String, dynamic>{};
              for (final f in fields) {
                out[f.key] = f.kind == FieldKind.dropdown ? emptyToNull(selected[f.key]) : parseFieldValue(controllers[f.key]!.text, f.kind);
              }
              Navigator.pop(context, out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final c in controllers.values) {
    c.dispose();
  }
  return result;
}

Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['name']))).toList();
}

Future<List<EditOption>> rankOptions() async {
  try {
    final rows = await db.from('ranks').select('name, default_salary, salary_grade, point_bracket, rank_group').order('sort_order').order('name').limit(500);
    final out = <EditOption>[];
    final seen = <String>{};
    for (final r in rows) {
      final name = formatValue(r['name']);
      final key = normalizeRankKey(name);
      if (key.isEmpty || seen.contains(key)) continue;
      seen.add(key);
      final salary = num.tryParse('${r['default_salary'] ?? ''}');
      final sg = r['salary_grade'] == null ? '' : ' - SG ${r['salary_grade']}';
      final pay = salary == null ? '' : ' - ${formatMoney(salary)}';
      out.add(EditOption(name, '$name$sg$pay', salary: salary));
    }
    return out;
  } catch (_) {
    return const [];
  }
}

String linkedEmployeeName(Map<String, dynamic>? row) {
  if (row?['employees'] is Map) return formatValue(row?['employees']['full_name']);
  return 'Linked Employee';
}

Future<bool> ensureNoEmployeeDuplicate(BuildContext context, String tableName, Object? employeeId, String moduleName) async {
  if (employeeId == null || employeeId.toString().trim().isEmpty) return true;
  try {
    final existing = await db.from(tableName).select('id').eq('employee_id', employeeId).limit(1);
    if (existing.isNotEmpty) {
      showSnack(context, 'Duplicate prevented: this employee already has a $moduleName record.');
      return false;
    }
    return true;
  } catch (e) {
    showSnack(context, 'Duplicate check failed: $e');
    return false;
  }
}

Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showRecordDialog(
    context,
    row == null ? 'Add Employee' : 'Edit Employee',
    const [
      EditField('full_name', 'Full Name', required: true),
      EditField('appointment', 'Appointment'),
      EditField('designation', 'Designation'),
      EditField('employee_type', 'Employee Type', kind: FieldKind.dropdown, options: [EditOption('full_time', 'Full Time'), EditOption('probationary', 'Probationary'), EditOption('part_time', 'Part Time'), EditOption('staff', 'Staff'), EditOption('faculty_staff', 'Faculty / Staff')]),
      EditField('employment_status', 'Employment Status', kind: FieldKind.dropdown, options: [EditOption('active', 'Active'), EditOption('inactive', 'Inactive'), EditOption('separated', 'Separated')]),
      EditField('current_salary', 'Current Salary', kind: FieldKind.number),
      EditField('license_summary', 'License Summary'),
    ],
    row,
  );
  if (data == null) return;
  data['name_key'] = normalizeName(data['full_name']?.toString() ?? '');
  await saveRow(context, 'employees', row?['id'], data, refresh);
}

Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Contract' : 'Edit Contract',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('contract_type', 'Contract Type'),
      const EditField('contract_start_date', 'Start Date', kind: FieldKind.date),
      const EditField('duration_months', 'Duration In Months', kind: FieldKind.integer),
      const EditField('contract_end_date', 'End Date', kind: FieldKind.date),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}

Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add License' : 'Edit License',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('license_name', 'License Name', required: true),
      const EditField('license_number', 'License Number'),
      const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_licenses', data['employee_id'], 'license')) return;
  await saveRow(context, 'employee_licenses', row?['id'], data, refresh);
}

Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Certificate' : 'Edit Certificate',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('certificate_type', 'Certificate Type'),
      const EditField('certificate_name', 'Certificate Name', required: true),
      const EditField('certificate_number', 'Certificate Number'),
      const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_certificates', data['employee_id'], 'certificate')) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row?['id'], data, refresh);
}

Future<void> editEvaluation(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Evaluation' : 'Edit Evaluation',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('academic_year', 'Academic Year', required: true),
      const EditField('semester', 'Semester', required: true),
      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),
      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),
      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),
      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),
      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),
      const EditField('total_description', 'Total Description', kind: FieldKind.multiline, lines: 3),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'evaluation_records', data['employee_id'], 'evaluation')) return;
  await saveRow(context, 'evaluation_records', row?['id'], data, refresh);
}

Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showRankingDialog(context, isAdd ? await employeeOptions() : const <EditOption>[], await cycleOptions(), await rankOptions(), row);
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'ranking_applications', data['employee_id'], 'ranking')) return;
  await saveRow(context, 'ranking_applications', row?['id'], data, refresh);
}

Future<Map<String, dynamic>?> showRankingDialog(BuildContext context, List<EditOption> employees, List<EditOption> cycles, List<EditOption> ranks, Map<String, dynamic>? initial) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? optionValueOrFirst(null, employees, true) : initial?['employee_id']?.toString();
  String? cycleId = optionValueOrFirst(initial?['cycle_id']?.toString(), cycles, true);
  final appointment = TextEditingController(text: formatEditValue(initial?['appointment']));
  final previousRank = TextEditingController(text: formatEditValue(initial?['previous_rank_text']));
  final previousSalary = TextEditingController(text: formatEditValue(initial?['previous_salary']));
  final appliedRank = TextEditingController(text: formatEditValue(initial?['applied_rank_text']));
  final appliedSalary = TextEditingController(text: formatEditValue(initial?['applied_salary']));
  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));
  final approvedRank = TextEditingController(text: formatEditValue(initial?['approved_rank_text']));
  final approvedSalary = TextEditingController(text: formatEditValue(initial?['approved_salary']));

  Future<void> pickRank(TextEditingController rank, TextEditingController salary) async {
    final selected = await showDialog<EditOption>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Choose Rank'),
        content: SizedBox(
          width: 460,
          height: 440,
          child: ranks.isEmpty
              ? const Center(child: Text('No rank reference found. You can type manually.'))
              : ListView.separated(
                  itemCount: ranks.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (_, i) => ListTile(title: Text(ranks[i].label), onTap: () => Navigator.pop(context, ranks[i])),
                ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel'))],
      ),
    );
    if (selected == null) return;
    rank.text = selected.value;
    if (selected.salary != null) salary.text = selected.salary!.toStringAsFixed(2);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Ranking Record' : 'Edit Ranking Record'),
        content: SizedBox(
          width: 760,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                if (isAdd)
                  SizedBox(
                    width: 354,
                    child: DropdownButtonFormField<String>(
                      value: optionValueOrFirst(employeeId, employees, true),
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Employee Name'),
                      items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                      onChanged: (v) => setDialogState(() => employeeId = v),
                    ),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                SizedBox(
                  width: 354,
                  child: DropdownButtonFormField<String>(
                    value: optionValueOrFirst(cycleId, cycles, true),
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Ranking Cycle'),
                    items: uniqueOptions(cycles).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                    validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                    onChanged: (v) => setDialogState(() => cycleId = v),
                  ),
                ),
                textBox('Appointment', appointment),
                textBox('Points Earned', points, kind: FieldKind.number),
                rankTextBox('Previous Rank', previousRank, () => pickRank(previousRank, previousSalary)),
                textBox('Previous Salary', previousSalary, kind: FieldKind.number),
                rankTextBox('Applied Rank', appliedRank, () => pickRank(appliedRank, appliedSalary)),
                textBox('Applied Salary', appliedSalary, kind: FieldKind.number),
                rankTextBox('Approved Rank', approvedRank, () => pickRank(approvedRank, approvedSalary)),
                textBox('Approved Salary', approvedSalary, kind: FieldKind.number),
                SizedBox(
                  width: 728,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)),
                    child: Text(isAdd ? 'Select an employee for the new ranking record. Duplicate employees are not allowed.' : 'Employee name is locked here. Type ranks manually or use Pick to auto-fill salary.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)),
                  ),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, {
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text),
                'previous_rank_text': emptyToNull(previousRank.text),
                'previous_salary': num.tryParse(previousSalary.text.trim()),
                'applied_rank_text': emptyToNull(appliedRank.text),
                'applied_salary': num.tryParse(appliedSalary.text.trim()),
                'points_earned': num.tryParse(points.text.trim()),
                'approved_rank_text': emptyToNull(approvedRank.text),
                'approved_salary': num.tryParse(approvedSalary.text.trim()),
              });
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final c in [appointment, previousRank, previousSalary, appliedRank, appliedSalary, points, approvedRank, approvedSalary]) {
    c.dispose();
  }
  return result;
}

Widget textBox(String label, TextEditingController controller, {FieldKind kind = FieldKind.text}) => SizedBox(
      width: 354,
      child: TextFormField(controller: controller, keyboardType: kind == FieldKind.number || kind == FieldKind.integer ? TextInputType.number : TextInputType.text, maxLines: kind == FieldKind.multiline ? 3 : 1, decoration: InputDecoration(labelText: label)),
    );

Widget rankTextBox(String label, TextEditingController controller, VoidCallback onPick) => SizedBox(
      width: 354,
      child: Row(children: [
        Expanded(child: TextFormField(controller: controller, decoration: InputDecoration(labelText: label))),
        const SizedBox(width: 8),
        OutlinedButton(onPressed: onPick, child: const Text('Pick')),
      ]),
    );

Future<void> saveRow(BuildContext context, String table, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from(table).insert(data);
      showSnack(context, 'Record Added.');
    } else {
      await db.from(table).update(data).eq('id', id);
      showSnack(context, 'Record Updated.');
    }
    refresh();
  } catch (e) {
    showSnack(context, 'Save Failed: $e');
  }
}

class ReportConfig {
  final String title;
  final Future<List<dynamic>> Function() load;
  final List<GridCol> columns;
  const ReportConfig(this.title, this.load, this.columns);
}

class ReportsPage extends StatefulWidget {
  const ReportsPage({super.key});

  @override
  State<ReportsPage> createState() => _ReportsPageState();
}

class _ReportsPageState extends State<ReportsPage> {
  int selected = 0;

  List<ReportConfig> get reports => [
        ReportConfig('Employee Master List', () => loadEmployees(limit: 5000), const [
          GridCol('full_name', 'Employee Name', flex: 3, primary: true),
          GridCol('appointment', 'Appointment', flex: 2),
          GridCol('designation', 'Designation', flex: 2),
          GridCol('employee_type', 'Type'),
          GridCol('employment_status', 'Status'),
          GridCol('current_salary', 'Salary', isMoney: true),
        ]),
        ReportConfig('Contract Monitoring Report', () => loadContracts(limit: 5000), const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('contract_type', 'Contract Type', flex: 2),
          GridCol('status', 'Status'),
          GridCol('contract_start_date', 'Start'),
          GridCol('contract_end_date', 'End'),
          GridCol('days_left', 'Days Left', isNumber: true),
        ]),
        ReportConfig('License Report', () => loadLicenses(limit: 5000), const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('license_name', 'License', flex: 2),
          GridCol('license_number', 'License No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status'),
        ]),
        ReportConfig('National Certificate Report', () => loadCertificates(limit: 5000), const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('certificate_name', 'Certificate', flex: 3),
          GridCol('certificate_type', 'Type', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status'),
        ]),
        ReportConfig('Evaluation Report', () => loadEvaluations(limit: 5000), const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('academic_year', 'A.Y.'),
          GridCol('semester', 'Semester'),
          GridCol('total_rating', 'Total', isNumber: true),
          GridCol('total_description', 'Description', flex: 2),
        ]),
        ReportConfig('Ranking Report', () => loadRankings(limit: 5000), const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('cycle_name', 'Cycle', flex: 2),
          GridCol('previous_rank_text', 'Previous', flex: 2),
          GridCol('applied_rank_text', 'Applied', flex: 2),
          GridCol('points_earned', 'Points', isNumber: true),
          GridCol('approved_rank_text', 'Approved', flex: 2),
          GridCol('approved_salary', 'Salary', isMoney: true),
        ]),
      ];

  Future<void> printCurrentReport(ReportConfig config) async {
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final data = await config.load();
      final rows = data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
      final markup = buildPrintableReportHtml(config.title, config.columns, rows);
      final blob = html.Blob([markup], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      if (printWindow != null) {
        printWindow.location.href = url;
      } else {
        html.window.open(url, '_blank');
      }
    } catch (e) {
      if (mounted) showSnack(context, 'Print Failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final config = reports[selected];
    return PageFrame(
      title: 'Reports',
      subtitle: 'Print reports per HR module.',
      child: Column(children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(children: [
              SizedBox(
                width: 330,
                child: DropdownButtonFormField<int>(
                  value: selected,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Report Type'),
                  items: [for (var i = 0; i < reports.length; i++) DropdownMenuItem(value: i, child: Text(reports[i].title))],
                  onChanged: (v) => setState(() => selected = v ?? 0),
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(onPressed: () => printCurrentReport(config), icon: const Icon(Icons.print_rounded), label: const Text('Print Report')),
              const SizedBox(width: 12),
              const Expanded(child: Text('Opens a print-ready A4 landscape report.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600))),
            ]),
          ),
        ),
        const SizedBox(height: 14),
        Expanded(
          child: FutureBuilder<List<dynamic>>(
            key: ValueKey(selected),
            future: config.load(),
            builder: (context, snap) {
              if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
              if (snap.hasError) return ErrorBox('${snap.error}');
              final rows = (snap.data ?? []).map((item) => Map<String, dynamic>.from(item as Map)).toList();
              return ReportPreview(title: config.title, columns: config.columns, rows: rows);
            },
          ),
        ),
      ]),
    );
  }
}

class ReportPreview extends StatelessWidget {
  final String title;
  final List<GridCol> columns;
  final List<Map<String, dynamic>> rows;
  const ReportPreview({super.key, required this.title, required this.columns, required this.rows});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: Column(children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            color: const Color(0xFFF8FAFC),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: _ink)),
              const SizedBox(height: 4),
              Text('Generated ${DateTime.now().toString().split('.').first} - ${rows.length} records', style: const TextStyle(color: _muted, fontWeight: FontWeight.w600)),
            ]),
          ),
          const Divider(height: 1, color: _line),
          TableHeader(columns: columns, sortKey: '', sortAscending: true, showActions: false, onSort: (_) {}),
          const Divider(height: 1, color: _line),
          Expanded(
            child: rows.isEmpty
                ? const EmptyBox()
                : ListView.separated(
                    itemCount: rows.length,
                    separatorBuilder: (_, __) => const Divider(height: 1, color: _line),
                    itemBuilder: (_, i) => ReportRow(row: rows[i], columns: columns, index: i),
                  ),
          ),
        ]),
      ),
    );
  }
}

class ReportRow extends StatelessWidget {
  final Map<String, dynamic> row;
  final List<GridCol> columns;
  final int index;
  const ReportRow({super.key, required this.row, required this.columns, required this.index});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: index.isEven ? Colors.white : const Color(0xFFFBFDFF),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
      child: Row(children: [for (final col in columns) Expanded(flex: col.flex, child: Padding(padding: const EdgeInsets.only(right: 10), child: tableCell(col, valueFor(row, col.key))))]),
    );
  }
}

String buildPrintableReportHtml(String title, List<GridCol> columns, List<Map<String, dynamic>> rows) {
  final date = DateTime.now().toString().split('.').first;
  final header = columns.map((c) => '<th>${escapeHtml(c.label)}</th>').join();
  final body = rows.map((row) {
    final cells = columns.map((c) => '<td>${escapeHtml(displayForReport(c, valueFor(row, c.key)))}</td>').join();
    return '<tr>$cells</tr>';
  }).join();
  return '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<style>
@page { size: A4 landscape; margin: 10mm; }
* { box-sizing: border-box; }
body { font-family: Arial, sans-serif; color: #0f172a; margin: 0; }
h1 { font-size: 20px; margin: 0 0 4px; }
.meta { color: #475569; font-size: 11px; margin-bottom: 14px; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 10px; }
th { text-align: left; background: #f1f5f9; font-weight: 700; }
th, td { border: 1px solid #cbd5e1; padding: 6px; vertical-align: top; word-wrap: break-word; }
tr:nth-child(even) td { background: #f8fafc; }
@media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
</style>
<script>
window.addEventListener('load', function () {
  setTimeout(function () { window.focus(); window.print(); }, 350);
});
</script>
</head>
<body>
<h1>${escapeHtml(title)}</h1>
<div class="meta">Generated $date • ${rows.length} records</div>
<table><thead><tr>$header</tr></thead><tbody>$body</tbody></table>
</body>
</html>''';
}

String displayForReport(GridCol col, Object? raw) {
  if (col.isMoney) return formatMoney(raw);
  if (col.isNumber) return formatNumber(raw);
  return formatValue(raw);
}

String escapeHtml(Object? value) {
  return (value?.toString() ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
}

List<EditOption> uniqueOptions(List<EditOption> options) {
  final seen = <String>{};
  final out = <EditOption>[];
  for (final option in options) {
    if (seen.add(option.value)) out.add(option);
  }
  return out;
}

String? optionValueOrFirst(String? value, List<EditOption> options, bool requiredField) {
  final unique = uniqueOptions(options);
  if (value != null && unique.any((o) => o.value == value)) return value;
  if (requiredField && unique.isNotEmpty) return unique.first.value;
  if (unique.any((o) => o.value == '')) return '';
  return null;
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
  if (key == 'days_left') return contractDaysLeft(row['contract_end_date']);
  return row[key];
}

int? contractDaysLeft(Object? endDate) {
  final raw = endDate?.toString();
  if (raw == null || raw.trim().isEmpty) return null;
  final date = DateTime.tryParse(raw);
  if (date == null) return null;
  final today = DateTime.now();
  final base = DateTime(today.year, today.month, today.day);
  final end = DateTime(date.year, date.month, date.day);
  return end.difference(base).inDays;
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
  void walk(Object? v) {
    if (v == null) return;
    if (v is Map) {
      for (final x in v.values) {
        walk(x);
      }
    } else {
      values.add(formatValue(v).toLowerCase());
    }
  }
  walk(row);
  values.add(formatValue(valueFor(row, 'days_left')).toLowerCase());
  return values.join(' ');
}

String formatEditValue(Object? value) {
  if (value == null) return '';
  final text = value.toString();
  return text == 'null' ? '' : text;
}

String normalizeName(String value) => value.trim().replaceAll(RegExp(r'\s+'), ' ').toUpperCase();
String normalizeRankKey(String value) => value.trim().replaceAll(RegExp(r'\s+'), ' ').toLowerCase();

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString().trim();
  if (text.isEmpty || text.toLowerCase() == 'null') return '-';
  final date = DateTime.tryParse(text);
  if (date != null && text.contains('-')) return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  return toTitleCase(text.replaceAll('_', ' ').replaceAll(RegExp(r'\s+'), ' '));
}

String toTitleCase(String input) {
  final acronyms = <String, String>{
    'LPT': 'LPT',
    'MAED': 'MAED',
    'MAT': 'MAT',
    'MA': 'MA',
    'MBA': 'MBA',
    'MIT': 'MIT',
    'PHD': 'PhD',
    'NC': 'NC',
    'PRC': 'PRC',
    'HR': 'HR',
    'MIS': 'MIS',
    'OAA': 'OAA',
    'OSA': 'OSA',
    'TESDA': 'TESDA',
    'CBIT': 'CBIT',
    'CRIM': 'CRIM',
    'CSSH': 'CSSH',
    'GAD': 'GAD',
    'SDS': 'SDS',
    'BPE': 'BPE',
    'MSCRIM': 'MSCRIM',
    'RCRIM': 'RCRIM',
  };
  return input.split(' ').map((word) {
    if (word.isEmpty) return word;
    final clean = word.replaceAll(RegExp(r'[^A-Za-z0-9]'), '').toUpperCase();
    if (acronyms.containsKey(clean)) return word.toUpperCase().replaceFirst(clean, acronyms[clean]!);
    if (RegExp(r'^[IVXLCM]+$').hasMatch(clean)) return word.toUpperCase();
    return word.split('-').map(capitalizeWord).join('-');
  }).join(' ');
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
  return '₱$whole.${s.last}';
}
