// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment(
  'SUPABASE_URL',
  defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co',
);
const publicClientKey = String.fromEnvironment(
  'SUPABASE_PUBLIC_CLIENT_KEY',
  defaultValue: 'sb_publishable_QJuRm0RkkQfbgAnBPPxbYw_AtG0BK3o',
);

const _primary = Color(0xFF2563EB);
const _accent = Color(0xFF4B5FA7);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF8FAFC);
const _line = Color(0xFFE2E8F0);
const _danger = Color(0xFFDC2626);
const _pageSize = 10;

SupabaseClient get db => Supabase.instance.client;

void safeRefresh(VoidCallback refresh) {
  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());
}

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
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22), side: const BorderSide(color: _line)),
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
  Widget build(BuildContext context) => const Scaffold(
        body: Center(
          child: SizedBox(width: 720, child: Card(child: Padding(padding: EdgeInsets.all(28), child: Text('Start the app with your Supabase public client key using --dart-define.')))),
        ),
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
      const AppointmentPage(),
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
      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
    ];
    return Container(
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(18, 20, 18, 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
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
        ]),
        const SizedBox(height: 7),
        const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
        const SizedBox(height: 30),
        for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].label, icon: items[i].icon, selected: selectedIndex == i, onTap: () => onChanged(i)),
        const Spacer(),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFFDBEAFE))),
          child: const Text('Employee add flow now includes full profile, contract, and credential details.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.35, fontWeight: FontWeight.w600)),
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
            decoration: BoxDecoration(
              color: selected ? const Color(0xFFEFF6FF) : Colors.transparent,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: selected ? const Color(0xFFDBEAFE) : Colors.transparent),
            ),
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

Future<List<dynamic>> loadEmployees({int limit = 1500}) => db
    .from('employees')
    .select('id, full_name, bio_number, gender, education_level, date_hired, starting_date, employment_status, designation, employee_type, civil_status, teaching_status, current_salary, license_summary, birth_date, address, contact_number, email, guardian_name, guardian_relationship, guardian_contact, guardian_address, school_graduated, degree_course, notes')
    .order('full_name')
    .limit(limit);
Future<List<dynamic>> loadContracts({int limit = 1500}) => db.from('employee_contracts').select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name)').order('contract_end_date', ascending: true).limit(limit);
Future<List<dynamic>> loadLicenses({int limit = 1500}) => db.from('employee_licenses').select('id, employee_id, license_name, license_number, issued_date, expiry_date, status, attachment_url, employees(full_name)').order('expiry_date').limit(limit);

Future<List<dynamic>> loadLicensesGrouped({int limit = 5000}) async {
  final rows = await loadLicenses(limit: limit);
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}';
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }
  final out = <Map<String, dynamic>>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.isEmpty) continue;
    final first = list.first;
    String bullets(String key) => list.map((r) => '• ${formatValue(r[key])}').join('\n');
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'license_ids': list.map((r) => r['id']).toList(),
      'license_records': list,
      'license_name': bullets('license_name'),
      'license_number': bullets('license_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name']).compareTo(formatValue(b['employee_name'])));
  return out;
}

Future<List<dynamic>> loadCertificates({int limit = 1500}) => db.from('employee_certificates').select('id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, attachment_url, employees(full_name)').order('expiry_date').limit(limit);
Future<List<dynamic>> loadEvaluations({int limit = 1500}) => db.from('evaluation_records').select('id, employee_id, academic_year, semester, superior_rating, peer_rating, self_rating, student_rating, total_rating, total_description, employees(full_name)').order('academic_year').limit(limit);
Future<List<dynamic>> loadRankings({int limit = 1500}) => db.from('ranking_applications').select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, approved_date, employees(full_name), ranking_cycles(name)').order('points_earned', ascending: false).limit(limit);
Future<List<dynamic>> loadAppointments({int limit = 5000}) => db.from('employee_appointments').select('id, employee_id, category, appointment_title, employees(full_name)').order('category').limit(limit);

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

class QuickCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  const QuickCard(this.title, this.icon, this.onTap, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
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

class EmployeesPage extends StatelessWidget {
  const EmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Add full employee information, contract, credentials, and view complete records.',
        child: CrudTable(
          load: () => loadEmployees(),
          searchHint: 'Search employee, bio number, gender, education, status, or date hired',
          addLabel: 'Add Employee',
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('education_level', 'Educational Attainment', flex: 2),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onAdd: (ctx, refresh) => addEmployeeFull(ctx, refresh),
          onView: viewEmployee,
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
        child: const DefaultTabController(
          length: 2,
          child: Column(children: [
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
        load: () => loadLicensesGrouped(),
        searchHint: 'Search employee, license name, number, or status',
        addLabel: 'Add License',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('license_name', 'License', flex: 2),
          GridCol('license_number', 'License No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onView: viewLicenseGroup,
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


class AppointmentPage extends StatelessWidget {
  const AppointmentPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Appointment',
        subtitle: 'View employee appointment classifications and assigned appointment/designation from the ranking Excel list.',
        child: CrudTable(
          load: () => loadAppointments(),
          searchHint: 'Search employee, type, or appointment',
          addLabel: 'Add Appointment',
          allowAdd: false,
          reportTitle: 'Appointment Reference Report',
          columns: const [
            GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            GridCol('category', 'Type', flex: 2),
            GridCol('appointment_title', 'Appointment', flex: 4),
          ],
          onView: viewAppointment,
          onEdit: editAppointment,
          onDelete: (row) => db.from('employee_appointments').delete().eq('id', row['id']),
        ),
      );
}


Future<void> viewAppointment(BuildContext context, Map<String, dynamic> row) async {
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(formatValue(row['employee_name'])),
      content: SizedBox(
        width: 620,
        child: Wrap(spacing: 10, runSpacing: 10, children: [
          DetailTile('Type', formatValue(row['category'])),
          DetailTile('Appointment', formatValue(row['appointment_title'])),
        ]),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    ),
  );
}

Future<void> editAppointment(BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final data = await showRecordDialog(
    context,
    'Edit Appointment',
    const [
      EditField('category', 'Type', kind: FieldKind.dropdown, required: true, options: [EditOption('Full-time', 'Full-time'), EditOption('Probationary', 'Probationary')]),
      EditField('appointment_title', 'Appointment', required: true),
    ],
    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  await saveRow(context, 'employee_appointments', row['id'], data, refresh);
}

class RankingPage extends StatefulWidget {
  const RankingPage({super.key});

  @override
  State<RankingPage> createState() => _RankingPageState();
}

class _RankingPageState extends State<RankingPage> {
  String filter = 'All';
  String rankFilter = 'All';
  late Future<List<EditOption>> rankFilterOptionsFuture;

  @override
  void initState() {
    super.initState();
    rankFilterOptionsFuture = rankOptions();
  }

  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final text = '${row['appointment'] ?? ''}'.toLowerCase().replaceAll('_', ' ').replaceAll('-', ' ');
    final isFullTime = text.contains('full') && text.contains('time');
    final isProbationary = text.contains('probationary');
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }

  Iterable<String> _rankValues(Map<String, dynamic> row) sync* {
    for (final key in const ['previous_rank_text', 'applied_rank_text', 'approved_rank_text']) {
      final value = '${row[key] ?? ''}'.trim();
      if (value.isNotEmpty && value != '-') yield value;
    }
  }

  bool _matchesRankFilter(Map<String, dynamic> row) {
    if (rankFilter == 'All') return true;
    final selected = normalizeRankKey(rankFilter);
    return _rankValues(row).any((value) => normalizeRankKey(value) == selected);
  }

  String _rankingReportTitle() {
    final appointmentLabel = filter == 'All' ? 'Full-time and Probationary' : filter;
    final rankLabel = rankFilter == 'All' ? 'All Ranks' : rankFilter;
    return 'Ranking Report - $appointmentLabel - $rankLabel';
  }

  Future<List<dynamic>> _loadRankings() async {
    final rows = await loadRankings(limit: 5000);
    return rows
        .map((item) => normalizeRow(Map<String, dynamic>.from(item as Map)))
        .where((row) => _matchesRankingFilter(row, filter) && _matchesRankFilter(row))
        .toList();
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: '2026 Faculty Ranking',
        subtitle: 'Manage faculty ranking applications following the Excel ranking summary layout.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  const Text('Filter:', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                  const SizedBox(width: 12),
                  for (final item in const ['All', 'Full-time', 'Probationary']) ...[
                    ChoiceChip(
                      label: Text(item == 'All' ? 'All (Full-time + Probationary)' : item),
                      selected: filter == item,
                      onSelected: (_) => setState(() {
                        filter = item;
                        rankFilter = 'All';
                      }),
                    ),
                    const SizedBox(width: 8),
                  ],
                ]),
                const SizedBox(height: 12),
                FutureBuilder<List<EditOption>>(
                  future: rankFilterOptionsFuture,
                  builder: (context, snap) {
                    final ranks = snap.data ?? const <EditOption>[];
                    final options = <EditOption>[
                      const EditOption('All', 'All Ranks'),
                      ...uniqueOptions(ranks).map((option) => EditOption(option.value, option.value)),
                    ];
                    final selectedRank = options.any((option) => option.value == rankFilter) ? rankFilter : 'All';
                    return rankFilterAutocompleteBox(
                      selectedRank: selectedRank,
                      options: options,
                      onChanged: (value) => setState(() => rankFilter = value),
                    );
                  },
                ),
              ]),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey('$filter|$rankFilter'),
              load: () => _loadRankings(),
              searchHint: 'Search employee, rank, salary, points, or appointment',
              addLabel: 'Add Ranking',
              reportTitle: _rankingReportTitle(),
              columns: const [
                GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
                GridCol('appointment_title', 'Appointment', flex: 3),
                GridCol('previous_rank_text', 'Previous Rank', flex: 2),
                GridCol('previous_salary', 'Basic Salary', isMoney: true),
                GridCol('applied_rank_text', 'Rank Applied', flex: 2),
                GridCol('applied_salary', 'Basic Salary Adjustment', flex: 2, isMoney: true),
                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
                GridCol('approved_date', 'Approved Date'),
              ],
              onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
              onView: viewRanking,
              onEdit: editRanking,
              onApprove: approveRanking,
              showDelete: true,
              onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}


class RankFilterAutocompleteBox extends StatefulWidget {
  final String selectedRank;
  final List<EditOption> options;
  final ValueChanged<String> onChanged;

  const RankFilterAutocompleteBox({super.key, required this.selectedRank, required this.options, required this.onChanged});

  @override
  State<RankFilterAutocompleteBox> createState() => _RankFilterAutocompleteBoxState();
}

class _RankFilterAutocompleteBoxState extends State<RankFilterAutocompleteBox> {
  late TextEditingController controller;

  @override
  void initState() {
    super.initState();
    controller = TextEditingController(text: widget.selectedRank == 'All' ? 'All Ranks' : widget.selectedRank);
  }

  @override
  void didUpdateWidget(covariant RankFilterAutocompleteBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    final nextText = widget.selectedRank == 'All' ? 'All Ranks' : widget.selectedRank;
    if (oldWidget.selectedRank != widget.selectedRank && controller.text != nextText) {
      controller.text = nextText;
    }
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 360,
        child: Autocomplete<EditOption>(
          initialValue: TextEditingValue(text: controller.text),
          displayStringForOption: (option) => option.label,
          optionsBuilder: (textEditingValue) {
            final sorted = uniqueOptions(widget.options).toList()..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
            final query = textEditingValue.text.trim().toLowerCase();
            if (query.isEmpty) return sorted;
            final normalizedQuery = normalizeRankKey(query);
            return sorted.where((option) {
              final value = option.value.toLowerCase();
              final label = option.label.toLowerCase();
              final normalizedValue = normalizeRankKey(option.value);
              final normalizedLabel = normalizeRankKey(option.label);
              return value.contains(query) || label.contains(query) || normalizedValue.contains(normalizedQuery) || normalizedLabel.contains(normalizedQuery);
            });
          },
          onSelected: (option) {
            controller.text = option.label;
            widget.onChanged(option.value);
          },
          fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) {
            if (textController.text != controller.text) textController.text = controller.text;
            return TextFormField(
              controller: textController,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: 'Filter by Ranking',
                hintText: 'Search or select rank',
                suffixIcon: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (widget.selectedRank != 'All')
                      IconButton(
                        tooltip: 'Clear rank filter',
                        icon: const Icon(Icons.close_rounded),
                        onPressed: () {
                          textController.text = 'All Ranks';
                          controller.text = 'All Ranks';
                          widget.onChanged('All');
                        },
                      ),
                    const Icon(Icons.search_rounded),
                    const SizedBox(width: 10),
                  ],
                ),
              ),
              onTap: () {
                if (widget.selectedRank == 'All') textController.selection = TextSelection(baseOffset: 0, extentOffset: textController.text.length);
              },
              onChanged: (value) {
                controller.text = value;
                final clean = value.trim();
                if (clean.isEmpty) {
                  widget.onChanged('All');
                  return;
                }
                final exact = uniqueOptions(widget.options).where((option) => option.label.toLowerCase() == clean.toLowerCase() || option.value.toLowerCase() == clean.toLowerCase() || normalizeRankKey(option.value) == normalizeRankKey(clean)).toList();
                if (exact.isNotEmpty) widget.onChanged(exact.first.value);
              },
            );
          },
          optionsViewBuilder: (context, onSelected, options) => Align(
            alignment: Alignment.topLeft,
            child: Material(
              elevation: 6,
              borderRadius: BorderRadius.circular(14),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520, maxHeight: 320),
                child: ListView.separated(
                  padding: EdgeInsets.zero,
                  shrinkWrap: true,
                  itemCount: options.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final option = options.elementAt(index);
                    return ListTile(
                      dense: true,
                      title: Text(option.label, overflow: TextOverflow.ellipsis),
                      onTap: () => onSelected(option),
                    );
                  },
                ),
              ),
            ),
          ),
        ),
      );
}

Widget rankFilterAutocompleteBox({required String selectedRank, required List<EditOption> options, required ValueChanged<String> onChanged}) => RankFilterAutocompleteBox(selectedRank: selectedRank, options: options, onChanged: onChanged);

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
typedef ViewHandler = Future<void> Function(BuildContext context, Map<String, dynamic> row);

class CrudTable extends StatefulWidget {
  final Future<List<dynamic>> Function() load;
  final String searchHint;
  final String addLabel;
  final bool allowAdd;
  final List<GridCol> columns;
  final AddHandler? onAdd;
  final EditHandler onEdit;
  final ViewHandler? onView;
  final EditHandler? onApprove;
  final bool showDelete;
  final String? reportTitle;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudTable({super.key, required this.load, required this.searchHint, required this.addLabel, this.allowAdd = true, required this.columns, this.onAdd, required this.onEdit, this.onView, this.onApprove, this.showDelete = true, this.reportTitle, required this.onDelete});

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

  double get actionWidth {
    var count = 1; // Edit button
    if (widget.onView != null) count++;
    if (widget.onApprove != null) count++;
    if (widget.showDelete) count++;
    return (count * 46).toDouble();
  }

  void printRows(List<Map<String, dynamic>> rows) {
    final baseTitle = widget.reportTitle ?? (widget.addLabel.toLowerCase().startsWith('add ') ? '${widget.addLabel.substring(4)} Report' : '${widget.addLabel} Report');
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final markup = buildPrintableReportHtml(baseTitle, widget.columns, rows);
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
  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(
        future: future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
          if (snap.hasError) return ErrorBox('${snap.error}');
          final rows = (snap.data ?? []).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
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
              onPrint: () => printRows(sorted),
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
              start: sorted.isEmpty ? 0 : startIndex + 1,
              end: endIndex,
              total: sorted.length,
              onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null,
              onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null,
            ),
          ]);
        },
      );

  Widget buildTable(List<Map<String, dynamic>> rows, String activeSortKey) => Card(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: Column(children: [
            TableHeader(columns: widget.columns, sortKey: activeSortKey, sortAscending: sortAscending, showActions: true, actionWidth: actionWidth, onSort: (key) {
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
                itemBuilder: (_, i) => TableRowItem(
                  row: rows[i],
                  columns: widget.columns,
                  index: i,
                  actionWidth: actionWidth,
                  onView: widget.onView == null ? null : () => widget.onView!(context, rows[i]),
                  onEdit: () => widget.onEdit(context, rows[i], refresh),
                  onApprove: widget.onApprove == null ? null : () => widget.onApprove!(context, rows[i], refresh),
                  onDelete: widget.showDelete ? () => confirmDelete(context, rows[i]) : null,
                ),
              ),
            ),
          ]),
        ),
      );

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
  final VoidCallback onPrint;
  final VoidCallback? onAdd;
  final ValueChanged<String?> onSortChanged;
  final VoidCallback onToggleSortDirection;

  const TableToolbar({super.key, required this.total, required this.showing, required this.hint, required this.addLabel, required this.allowAdd, required this.columns, required this.sortKey, required this.sortAscending, required this.onSearch, required this.onRefresh, required this.onPrint, required this.onAdd, required this.onSortChanged, required this.onToggleSortDirection});

  @override
  Widget build(BuildContext context) => Card(
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
                child: Row(mainAxisSize: MainAxisSize.min, children: [const Icon(Icons.table_rows_rounded, size: 18, color: _accent), const SizedBox(width: 8), Text('$showing Of $total', style: const TextStyle(color: Color(0xFF475569), fontWeight: FontWeight.w800))]),
              ),
              OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh_rounded), label: const Text('Refresh')),
              FilledButton.tonalIcon(onPressed: onPrint, icon: const Icon(Icons.print_rounded), label: const Text('Print')),
            ];
            if (allowAdd && onAdd != null) widgets.add(FilledButton.icon(onPressed: onAdd, icon: const Icon(Icons.add_rounded), label: Text(addLabel)));
            if (compact) return Wrap(spacing: 10, runSpacing: 10, crossAxisAlignment: WrapCrossAlignment.center, children: widgets);
            return Row(children: [Expanded(child: search), for (final w in widgets.skip(1)) ...[const SizedBox(width: 10), w]]);
          }),
        ),
      );
}

class TableHeader extends StatelessWidget {
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final bool showActions;
  final double actionWidth;
  final ValueChanged<String> onSort;

  const TableHeader({super.key, required this.columns, required this.sortKey, required this.sortAscending, required this.showActions, required this.actionWidth, required this.onSort});

  @override
  Widget build(BuildContext context) => Container(
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
          if (showActions) SizedBox(width: actionWidth, child: const Text('Actions', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 13))),
        ]),
      );
}

class TableRowItem extends StatelessWidget {
  final Map<String, dynamic> row;
  final List<GridCol> columns;
  final int index;
  final double actionWidth;
  final VoidCallback? onView;
  final VoidCallback onEdit;
  final VoidCallback? onApprove;
  final VoidCallback? onDelete;

  const TableRowItem({super.key, required this.row, required this.columns, required this.index, required this.actionWidth, this.onView, required this.onEdit, this.onApprove, this.onDelete});

  @override
  Widget build(BuildContext context) => Container(
        color: index.isEven ? Colors.white : const Color(0xFFFBFDFF),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: const BoxConstraints(minHeight: 62),
        child: Row(crossAxisAlignment: CrossAxisAlignment.center, children: [
          for (final col in columns) Expanded(flex: col.flex, child: Padding(padding: const EdgeInsets.only(right: 10), child: tableCell(col, valueFor(row, col.key)))),
          SizedBox(
            width: actionWidth,
            child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              if (onView != null) IconButton(tooltip: 'View', onPressed: onView, icon: const Icon(Icons.visibility_rounded, color: Color(0xFF0E7490), size: 20)),
              IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_rounded, color: _primary, size: 20)),
              if (onApprove != null) IconButton(tooltip: 'Approve Applied Rank', onPressed: onApprove, icon: const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 20)),
              if (onDelete != null) IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline_rounded, color: _danger, size: 20)),
            ]),
          ),
        ]),
      );
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
  Widget build(BuildContext context) => Card(
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
    if (v.contains('expired') || v.contains('inactive') || v.contains('separated') || v.contains('resigned')) {
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

class DialogSectionTitle extends StatelessWidget {
  final String title;
  const DialogSectionTitle(this.title, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 728,
        child: Container(
          margin: const EdgeInsets.only(top: 14, bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFFEFF6FF),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFBFDBFE)),
          ),
          child: Row(children: [
            const Expanded(child: Divider(color: Color(0xFF93C5FD), thickness: 1)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: Text(
                title.toUpperCase(),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF1E3A8A),
                  letterSpacing: 0.6,
                ),
              ),
            ),
            const Expanded(child: Divider(color: Color(0xFF93C5FD), thickness: 1)),
          ]),
        ),
      );
}


String dialogSectionForField(String key) {
  const sections = <String, String>{
    'full_name': 'Personal Information',
    'bio_number': 'Personal Information',
    'gender': 'Personal Information',
    'civil_status': 'Personal Information',
    'birth_date': 'Personal Information',
    'address': 'Personal Information',
    'contact_number': 'Personal Information',
    'email': 'Personal Information',

    'education_level': 'Educational Background',
    'school_graduated': 'Educational Background',
    'degree_course': 'Educational Background',

    'guardian_name': 'Guardian Information',
    'guardian_relationship': 'Guardian Information',
    'guardian_contact': 'Guardian Information',
    'guardian_address': 'Guardian Information',

    'designation': 'Employment Information',
    'employee_type': 'Employment Information',
    'teaching_status': 'Employment Information',
    'employment_status': 'Employment Information',
    'date_hired': 'Employment Information',
    'starting_date': 'Employment Information',
    'current_salary': 'Employment Information',
    'license_summary': 'Employment Information',
    'notes': 'Employment Information',

    'contract_type': 'Contract Information',
    'contract_start_date': 'Contract Information',
    'duration_months': 'Contract Information',
    'contract_end_date': 'Contract Information',
    'contract_attachment_url': 'Contract Information',
    'contract_status': 'Contract Information',

    'credential_kind': 'Credential Information',

    'license_name': 'License Information',
    'license_number': 'License Information',
    'license_issued_date': 'License Information',
    'license_expiry_date': 'License Information',
    'license_attachment_url': 'License Information',
    'license_status': 'License Information',

    'certificate_type': 'Certificate Information',
    'certificate_name': 'Certificate Information',
    'certificate_number': 'Certificate Information',
    'certificate_issued_date': 'Certificate Information',
    'certificate_expiry_date': 'Certificate Information',
    'certificate_attachment_url': 'Certificate Information',
    'certificate_status': 'Certificate Information',
  };
  return sections[key] ?? 'Other Information';
}

List<Widget> buildDialogFieldWidgets(
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState,
) {
  final widgets = <Widget>[];
  String? currentSection;

  for (final f in fields) {
    final section = dialogSectionForField(f.key);
    if (section != currentSection) {
      if (widgets.isNotEmpty) widgets.add(const SizedBox(width: 728, height: 4));
      widgets.add(DialogSectionTitle(section));
      currentSection = section;
    }

    final width = f.kind == FieldKind.multiline ? 728.0 : 354.0;
    if (f.kind == FieldKind.dropdown) {
      final opts = uniqueOptions(f.options);
      widgets.add(SizedBox(
        width: width,
        child: DropdownButtonFormField<String>(
          value: optionValueOrFirst(selected[f.key], opts, f.required),
          isExpanded: true,
          decoration: InputDecoration(labelText: f.label),
          items: opts.map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
          validator: (v) => f.required && (v == null || v.isEmpty) ? 'Required' : null,
          onChanged: (v) => setDialogState(() => selected[f.key] = v),
        ),
      ));
      continue;
    }

    widgets.add(SizedBox(
      width: width,
      child: TextFormField(
        controller: controllers[f.key],
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer ? TextInputType.number : TextInputType.text,
        decoration: InputDecoration(labelText: f.label, hintText: f.kind == FieldKind.date ? 'January 02, 2026' : null),
        validator: (v) => f.required && (v == null || v.trim().isEmpty) ? 'Required' : null,
      ),
    ));
  }

  return widgets;
}
Future<Map<String, dynamic>?> showRecordDialog(BuildContext context, String title, List<EditField> fields, Map<String, dynamic>? initial, {String? readOnlyEmployeeName, List<Widget> prefix = const []}) async {
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
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                if (readOnlyEmployeeName != null) ReadOnlyEmployeeBox(readOnlyEmployeeName),
                ...prefix,
                ...buildDialogFieldWidgets(fields, controllers, selected, setDialogState),
              ]),
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

Future<void> addEmployeeFull(BuildContext context, VoidCallback refresh) async {
  final data = await showRecordDialog(context, 'Add Employee', addEmployeeFields(), null);
  if (data == null) return;
  final employee = extractKeys(data, employeeKeys);
  employee['name_key'] = normalizeName(employee['full_name']?.toString() ?? '');
  employee['date_hired'] ??= employee['starting_date'];
  employee['starting_date'] ??= employee['date_hired'];

  try {
    final inserted = await db.from('employees').insert(employee).select('id').single();
    final employeeId = inserted['id'];
    final contract = extractKeys(data, contractKeys)..['employee_id'] = employeeId;
    if (hasUsefulValue(contract, ['contract_type', 'contract_start_date', 'contract_end_date', 'attachment_url'])) {
      contract['status'] ??= 'On-going';
      await db.from('employee_contracts').insert(contract);
    }
    final credentialType = data['credential_kind']?.toString() ?? 'license';
    if (credentialType == 'certificate') {
      final certificate = extractKeys(data, certificateKeys)..['employee_id'] = employeeId;
      if (hasUsefulValue(certificate, ['certificate_name', 'certificate_number', 'expiry_date', 'attachment_url'])) {
        certificate['certificate_type'] ??= 'National Certificate';
        certificate['status'] ??= 'Active';
        await db.from('employee_certificates').insert(certificate);
      }
    } else {
      final license = extractKeys(data, licenseKeys)..['employee_id'] = employeeId;
      if (hasUsefulValue(license, ['license_name', 'license_number', 'expiry_date', 'attachment_url'])) {
        license['status'] ??= 'Active';
        await db.from('employee_licenses').insert(license);
      }
    }
    refresh();
    showSnack(context, 'Employee, contract, and credential details saved.');
  } catch (e) {
    showSnack(context, 'Save Failed: $e');
  }
}

Future<void> viewEmployee(BuildContext context, Map<String, dynamic> row) async {
  try {
    final contracts = await db.from('employee_contracts').select().eq('employee_id', row['id']).order('contract_start_date', ascending: false);
    final licenses = await db.from('employee_licenses').select().eq('employee_id', row['id']).order('expiry_date');
    final certificates = await db.from('employee_certificates').select().eq('employee_id', row['id']).order('expiry_date');
    if (!context.mounted) return;
    await showDialog<void>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(formatValue(row['full_name'])),
        content: SizedBox(
          width: 820,
          child: SingleChildScrollView(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              detailSection('Personal Information', row, const {
                'Bio Number': 'bio_number',
                'Gender': 'gender',
                'Civil Status': 'civil_status',
                'Birth Date': 'birth_date',
                'Address': 'address',
                'Contact Number': 'contact_number',
                'Email': 'email',
              }),
              detailSection('Educational Background', row, const {
                'Educational Attainment': 'education_level',
                'School Graduated': 'school_graduated',
                'Degree / Course': 'degree_course',
              }),
              detailSection('Guardian Information', row, const {
                'Guardian Name': 'guardian_name',
                'Relationship': 'guardian_relationship',
                'Guardian Contact': 'guardian_contact',
                'Guardian Address': 'guardian_address',
              }),
              detailSection('Employment Information', row, const {
                'Designation': 'designation',
                'Employee Type': 'employee_type',
                'Teaching Status': 'teaching_status',
                'Date Hired': 'date_hired_display',
                'Employee Status': 'employment_status',
                'Current Salary': 'current_salary',
                'License Summary': 'license_summary',
                'Notes': 'notes',
              }),
              relatedSection('Contracts', contracts, const ['contract_type', 'contract_start_date', 'duration_months', 'contract_end_date', 'status', 'attachment_url']),
              relatedSection('Licenses', licenses, const ['license_name', 'license_number', 'issued_date', 'expiry_date', 'status', 'attachment_url']),
              relatedSection('Certificates', certificates, const ['certificate_type', 'certificate_name', 'certificate_number', 'issued_date', 'expiry_date', 'status', 'attachment_url']),
            ]),
          ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
      ),
    );
  } catch (e) {
    showSnack(context, 'View Failed: $e');
  }
}


Future<void> viewRanking(BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(formatValue(normalized['employee_name'])),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Ranking Information', normalized, const {
              'Employee Name': 'employee_name',
              'Appointment': 'appointment',
              'Previous Rank': 'previous_rank_text',
              'Basic Salary': 'previous_salary',
              'Rank Applied': 'applied_rank_text',
              'Basic Salary Adjustment': 'applied_salary',
              'Points Earned': 'points_earned',
              'Approved Rank': 'approved_rank_text',
              'Salary Rate': 'approved_salary',
            }),
          ]),
        ),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    ),
  );
}

Widget detailSection(String title, Map<String, dynamic> row, Map<String, String> fields) => Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
        const SizedBox(height: 8),
        Wrap(spacing: 10, runSpacing: 10, children: [for (final item in fields.entries) DetailTile(item.key, formatDetailValue(valueFor(row, item.value), item.value))]),
      ]),
    );

Widget relatedSection(String title, List<dynamic> records, List<String> keys) => Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
        const SizedBox(height: 8),
        if (records.isEmpty)
          const Text('No record added.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600))
        else
          for (final rec in records)
            Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
              child: Wrap(spacing: 8, runSpacing: 8, children: [for (final key in keys) DetailTile(titleCase(key), formatDetailValue((rec as Map)[key], key))]),
            ),
      ]),
    );

class DetailTile extends StatelessWidget {
  final String label;
  final String value;
  const DetailTile(this.label, this.value, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 245,
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), border: Border.all(color: _line)),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(label, style: const TextStyle(fontSize: 11, color: _muted, fontWeight: FontWeight.w800)),
            const SizedBox(height: 3),
            Text(value, style: const TextStyle(fontSize: 13, color: _ink, fontWeight: FontWeight.w700)),
          ]),
        ),
      );
}

Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  final out = rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
  out.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return out;
}

Future<List<String>> licenseNameOptions() async {
  const defaults = <String>[
    'Licensed Professional Teacher (LPT)',
    'Registered Criminologist (RCRIM)',
    'Registered Nurse (RN)',
    'Registered Social Worker (RSW)',
    'Registered Librarian (RL)',
    'Real Estate Broker (REB)',
    'Professional Regulation Commission (PRC) License',
  ];
  final seen = <String>{};
  final out = <String>[];
  void addName(String name) {
    final clean = name.trim();
    if (clean.isEmpty) return;
    final key = clean.toLowerCase();
    if (seen.add(key)) out.add(clean);
  }
  for (final item in defaults) {
    addName(item);
  }
  try {
    final rows = await db.from('employee_licenses').select('license_name').order('license_name').limit(3000);
    for (final r in rows) {
      addName('${r['license_name'] ?? ''}');
    }
  } catch (_) {}
  return out;
}

Future<List<String>> certificateNameOptions() async {
  const defaults = <String>[
    'National Certificate I (NC I)',
    'National Certificate II (NC II)',
    'National Certificate III (NC III)',
    'National Certificate IV (NC IV)',
    'Trainer Methodology Certificate I (TM I)',
    'Trainer Methodology Certificate II (TM II)',
  ];
  final seen = <String>{};
  final out = <String>[];
  void addName(String name) {
    final clean = name.trim();
    if (clean.isEmpty) return;
    final key = clean.toLowerCase();
    if (seen.add(key)) out.add(clean);
  }
  for (final item in defaults) {
    addName(item);
  }
  try {
    final rows = await db.from('employee_certificates').select('certificate_name').order('certificate_name').limit(3000);
    for (final r in rows) {
      addName('${r['certificate_name'] ?? ''}');
    }
  } catch (_) {}
  return out;
}

Future<Map<String, String>> rankingAppointmentByEmployee() async {
  final rows = await db.from('employee_appointments').select('employee_id, category, appointment_title').limit(5000);
  final out = <String, String>{};
  for (final r in rows) {
    final id = r['employee_id']?.toString();
    final category = formatEditValue(r['category']);
    final appointment = formatEditValue(r['appointment_title']);
    if (id != null && id.isNotEmpty && appointment.isNotEmpty) {
      out[id] = category.isEmpty ? appointment : '$category - $appointment';
    }
  }
  return out;
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['name']))).toList();
}

Future<List<EditOption>> rankOptions() async {
  try {
    final rows = await db.from('ranks').select('name, default_salary').order('sort_order').order('name').limit(500);
    final out = <EditOption>[];
    final seen = <String>{};
    for (final r in rows) {
      final name = formatValue(r['name']);
      final key = normalizeRankKey(name);
      if (key.isEmpty || seen.contains(key)) continue;
      seen.add(key);
      final salary = num.tryParse('${r['default_salary'] ?? ''}');
      final pay = salary == null ? '' : ' - ${formatMoney(salary)}';
      out.add(EditOption(name, '$name$pay', salary: salary));
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
    employeeEditFields(),
    normalizeRow(row ?? {}),
  );
  if (data == null) return;
  data['name_key'] = normalizeName(data['full_name']?.toString() ?? '');
  data['date_hired'] ??= data['starting_date'];
  data['starting_date'] ??= data['date_hired'];
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
      const EditField('attachment_url', 'Attachment URL'),
      const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived'), EditOption('Resigned', 'Resigned')]),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}


class SelectedLicenseInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  final TextEditingController attachment = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;
  String status = '';

  SelectedLicenseInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
    attachment.dispose();
  }
}

String licenseStatusFromExpiry(String text) {
  final value = text.trim();
  if (value.isEmpty) return '';
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final expiry = DateTime(parsed.year, parsed.month, parsed.day);
  if (expiry.isBefore(today)) return 'Expired';
  if (expiry.difference(today).inDays <= 90) return 'For Renewal';
  return 'Active';
}

Future<void> pickAndUploadLicensePdf(BuildContext context, SelectedLicenseInput entry, StateSetter setDialogState) async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return;
  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return;
  }
  setDialogState(() => entry.uploadingAttachment = true);
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path = 'licenses/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes, fileOptions: const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      entry.attachmentUrl = url;
      entry.attachmentFileName = file.name;
      entry.uploadingAttachment = false;
    });
  } catch (e) {
    setDialogState(() => entry.uploadingAttachment = false);
    showSnack(context, 'PDF upload failed: $e');
  }
}

Future<List<Map<String, dynamic>>?> showAddLicenseDialog(BuildContext context, List<EditOption> employees, List<String> licenses) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  final selected = <String, SelectedLicenseInput>{};

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add License'),
        content: SizedBox(
          width: 1040,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                SizedBox(
                  width: 430,
                  child: DropdownButtonFormField<String>(
                    value: employeeId,
                    isExpanded: true,
                    hint: const Text('Select Employee'),
                    decoration: const InputDecoration(labelText: 'Employee Name'),
                    items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                    validator: (v) => v == null || v.isEmpty ? 'Please select employee' : null,
                    onChanged: (v) => setDialogState(() => employeeId = v),
                  ),
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('License Checklist'),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    for (final license in licenses)
                      SizedBox(
                        width: 278,
                        child: CheckboxListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          controlAffinity: ListTileControlAffinity.leading,
                          title: Text(license, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
                          value: selected.containsKey(license),
                          onChanged: (checked) => setDialogState(() {
                            if (checked == true) {
                              selected.putIfAbsent(license, () => SelectedLicenseInput(license));
                            } else {
                              selected.remove(license)?.dispose();
                            }
                          }),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('Selected Licenses'),
                if (selected.isEmpty)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                    child: const Text('Select one or more licenses above. The selected licenses will appear here as a table.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
                  )
                else
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
                    child: Column(children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        decoration: const BoxDecoration(color: Color(0xFFF8FAFC), borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
                        child: const Row(children: [
                          Expanded(flex: 3, child: Text('License Name', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('License Number', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Expiry Date', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Attachment (PDF)', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          SizedBox(width: 130, child: Text('Status', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                        ]),
                      ),
                      for (final entry in selected.values)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Expanded(flex: 3, child: Padding(padding: const EdgeInsets.only(top: 14), child: Text(entry.name, style: const TextStyle(fontWeight: FontWeight.w800, color: _ink)))),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.number,
                                decoration: const InputDecoration(labelText: 'License Number'),
                                validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.expiry,
                                decoration: const InputDecoration(labelText: 'Expiry Date', hintText: 'January 02, 2026'),
                                validator: (v) {
                                  if (v == null || v.trim().isEmpty) return 'Required';
                                  if (parseFlexibleDate(v.trim()) == null) return 'Use January 02, 2026';
                                  return null;
                                },
                                onChanged: (v) => setDialogState(() => entry.status = licenseStatusFromExpiry(v)),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                OutlinedButton.icon(
                                  onPressed: entry.uploadingAttachment ? null : () => pickAndUploadLicensePdf(context, entry, setDialogState),
                                  icon: entry.uploadingAttachment
                                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                      : const Icon(Icons.picture_as_pdf_rounded),
                                  label: Text(entry.uploadingAttachment ? 'Uploading...' : (entry.attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF')),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  entry.attachmentFileName.isEmpty ? 'No PDF attached' : entry.attachmentFileName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontSize: 12, color: entry.attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700),
                                ),
                              ]),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.attachment,
                                decoration: const InputDecoration(labelText: 'Attachment (PDF)', hintText: 'PDF URL'),
                              ),
                            ),
                            const SizedBox(width: 10),
                            SizedBox(width: 130, child: Padding(padding: const EdgeInsets.only(top: 10), child: StatusChip(entry.status.isEmpty ? '-' : entry.status))),
                          ]),
                        ),
                    ]),
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
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one license.');
                return;
              }
              final missingPdf = selected.values.where((entry) => entry.attachmentUrl.trim().isEmpty).toList();
              if (missingPdf.isNotEmpty) {
                showSnack(context, 'Please attach a PDF file for every selected license.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {
                final status = licenseStatusFromExpiry(entry.expiry.text);
                return <String, dynamic>{
                  'employee_id': employeeId,
                  'license_name': entry.name,
                  'license_number': entry.number.text.trim(),
                  'expiry_date': toIsoDateInput(entry.expiry.text),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),
                  'status': status.isEmpty ? null : status,
                  'updated_at': now,
                };
              }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final item in selected.values) {
    item.dispose();
  }
  return result;
}


Future<void> viewLicenseGroup(BuildContext context, Map<String, dynamic> row) async {
  final records = (row['license_records'] is List) ? List<Map<String, dynamic>>.from(row['license_records'] as List) : <Map<String, dynamic>>[row];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('License Details - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 920,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            for (final rec in records)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                child: Wrap(spacing: 10, runSpacing: 10, children: [
                  DetailTile('License Name', formatValue(rec['license_name'])),
                  DetailTile('License Number', formatValue(rec['license_number'])),
                  DetailTile('Expiry Date', formatValue(rec['expiry_date'])),
                  DetailTile('Status', formatValue(rec['status'])),
                  DetailTile('Attachment PDF', formatValue(rec['attachment_url'])),
                ]),
              ),
          ]),
        ),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    ),
  );
}


Future<Map<String, dynamic>?> pickLicenseRecordToEdit(BuildContext context, Map<String, dynamic> row) async {
  final records = (row['license_records'] is List) ? List<Map<String, dynamic>>.from(row['license_records'] as List) : <Map<String, dynamic>>[row];
  if (records.isEmpty) return null;
  if (records.length == 1) return records.first;
  return showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Choose License to Edit'),
      content: SizedBox(
        width: 520,
        child: ListView.separated(
          shrinkWrap: true,
          itemCount: records.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (_, i) => ListTile(
            title: Text(formatValue(records[i]['license_name'])),
            subtitle: Text('License No.: ${formatValue(records[i]['license_number'])} • Expiry: ${formatValue(records[i]['expiry_date'])}'),
            onTap: () => Navigator.pop(context, records[i]),
          ),
        ),
      ),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel'))],
    ),
  );
}

Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddLicenseDialog(context, await employeeOptions(), await licenseNameOptions());
    if (records == null || records.isEmpty) return;
    try {
      await db.from('employee_licenses').insert(records);
      showSnack(context, records.length == 1 ? 'License record added.' : '${records.length} license records added.');
      refresh();
    } catch (e) {
      showSnack(context, 'Add License Failed: $e');
    }
    return;
  }

  final editRow = await pickLicenseRecordToEdit(context, row);
  if (editRow == null) return;
  final employeeName = formatValue(row['employee_name'] ?? editRow['employee_name']);
  final data = await showRecordDialog(
    context,
    'Edit License',
    const [
      EditField('license_name', 'License Name', required: true),
      EditField('license_number', 'License Number'),
      EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      EditField('attachment_url', 'Attachment URL'),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    editRow,
    readOnlyEmployeeName: employeeName == '-' ? linkedEmployeeName(editRow) : employeeName,
  );
  if (data == null) return;
  await saveRow(context, 'employee_licenses', editRow['id'], data, refresh);
}


class SelectedCertificateInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  final TextEditingController attachment = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;
  String status = '';

  SelectedCertificateInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
  }
}

String certificateStatusFromExpiry(String text) => licenseStatusFromExpiry(text);

Future<void> pickAndUploadCertificatePdf(BuildContext context, SelectedCertificateInput entry, StateSetter setDialogState) async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return;
  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return;
  }
  setDialogState(() => entry.uploadingAttachment = true);
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path = 'certificates/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes, fileOptions: const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      entry.attachmentUrl = url;
      entry.attachmentFileName = file.name;
      entry.uploadingAttachment = false;
    });
  } catch (e) {
    setDialogState(() => entry.uploadingAttachment = false);
    showSnack(context, 'PDF upload failed: $e');
  }
}

Future<List<Map<String, dynamic>>?> showAddCertificateDialog(BuildContext context, List<EditOption> employees, List<String> certificates) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  final selected = <String, SelectedCertificateInput>{};

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add Certificate'),
        content: SizedBox(
          width: 1040,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const DialogSectionTitle('Employee Information'),
                SizedBox(
                  width: 430,
                  child: DropdownButtonFormField<String>(
                    value: employeeId,
                    isExpanded: true,
                    hint: const Text('Select Employee'),
                    decoration: const InputDecoration(labelText: 'Employee Name'),
                    items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                    validator: (v) => v == null || v.isEmpty ? 'Please select employee' : null,
                    onChanged: (v) => setDialogState(() => employeeId = v),
                  ),
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('Certificate Checklist'),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    for (final cert in certificates)
                      SizedBox(
                        width: 278,
                        child: CheckboxListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          controlAffinity: ListTileControlAffinity.leading,
                          title: Text(cert, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _ink)),
                          value: selected.containsKey(cert),
                          onChanged: (checked) => setDialogState(() {
                            if (checked == true) {
                              selected.putIfAbsent(cert, () => SelectedCertificateInput(cert));
                            } else {
                              selected.remove(cert)?.dispose();
                            }
                          }),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                const DialogSectionTitle('Selected Certificates'),
                if (selected.isEmpty)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                    child: const Text('Select one or more certificates above. The selected certificates will appear here as a table.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700)),
                  )
                else
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
                    child: Column(children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        decoration: const BoxDecoration(color: Color(0xFFF8FAFC), borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
                        child: const Row(children: [
                          Expanded(flex: 3, child: Text('Certificate Name', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Certificate Number', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Expiry Date', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Attachment (PDF)', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          SizedBox(width: 130, child: Text('Status', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                        ]),
                      ),
                      for (final entry in selected.values)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Expanded(flex: 3, child: Padding(padding: const EdgeInsets.only(top: 14), child: Text(entry.name, style: const TextStyle(fontWeight: FontWeight.w800, color: _ink)))),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.number,
                                decoration: const InputDecoration(labelText: 'Certificate Number'),
                                validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.expiry,
                                decoration: const InputDecoration(labelText: 'Expiry Date', hintText: 'January 02, 2026'),
                                validator: (v) {
                                  if (v == null || v.trim().isEmpty) return 'Required';
                                  if (parseFlexibleDate(v.trim()) == null) return 'Use January 02, 2026';
                                  return null;
                                },
                                onChanged: (v) => setDialogState(() => entry.status = certificateStatusFromExpiry(v)),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                OutlinedButton.icon(
                                  onPressed: entry.uploadingAttachment ? null : () => pickAndUploadCertificatePdf(context, entry, setDialogState),
                                  icon: entry.uploadingAttachment
                                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                      : const Icon(Icons.picture_as_pdf_rounded),
                                  label: Text(entry.uploadingAttachment ? 'Uploading...' : (entry.attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF')),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  entry.attachmentFileName.isEmpty ? 'No PDF attached' : entry.attachmentFileName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontSize: 12, color: entry.attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700),
                                ),
                              ]),
                            ),
                            const SizedBox(width: 10),
                            SizedBox(width: 130, child: Padding(padding: const EdgeInsets.only(top: 10), child: StatusChip(entry.status.isEmpty ? '-' : entry.status))),
                          ]),
                        ),
                    ]),
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
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one certificate.');
                return;
              }
              final missingPdf = selected.values.where((entry) => entry.attachmentUrl.trim().isEmpty).toList();
              if (missingPdf.isNotEmpty) {
                showSnack(context, 'Please attach a PDF file for every selected certificate.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {
                final status = certificateStatusFromExpiry(entry.expiry.text);
                return <String, dynamic>{
                  'employee_id': employeeId,
                  'certificate_type': 'National Certificate',
                  'certificate_name': entry.name,
                  'certificate_number': entry.number.text.trim(),
                  'expiry_date': toIsoDateInput(entry.expiry.text),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),
                  'status': status.isEmpty ? null : status,
                  'updated_at': now,
                };
              }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final item in selected.values) {
    item.dispose();
  }
  return result;
}

Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddCertificateDialog(context, await employeeOptions(), await certificateNameOptions());
    if (records == null || records.isEmpty) return;
    try {
      await db.from('employee_certificates').insert(records);
      showSnack(context, records.length == 1 ? 'Certificate record added.' : '${records.length} certificate records added.');
      refresh();
    } catch (e) {
      showSnack(context, 'Add Certificate Failed: $e');
    }
    return;
  }

  final data = await showRecordDialog(
    context,
    'Edit Certificate',
    const [
      EditField('certificate_type', 'Certificate Type'),
      EditField('certificate_name', 'Certificate Name', required: true),
      EditField('certificate_number', 'Certificate Number'),
      EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      EditField('attachment_url', 'Attachment URL'),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ],
    row,
    readOnlyEmployeeName: linkedEmployeeName(row),
  );
  if (data == null) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row['id'], data, refresh);
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
      const EditField('total_description', 'Description'),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'evaluation_records', data['employee_id'], 'evaluation')) return;
  await saveRow(context, 'evaluation_records', row?['id'], data, refresh);
}


Future<void> approveRanking(BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final appliedRank = emptyToNull(row['applied_rank_text']);
  final appliedSalary = row['applied_salary'];
  if (appliedRank == null && appliedSalary == null) {
    showSnack(context, 'No applied rank to approve.');
    return;
  }
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Approve Applied Rank?'),
      content: Text('This will approve ${formatValue(row['applied_rank_text'])} for ${formatValue(valueFor(row, 'employee_name'))}.'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Approve')),
      ],
    ),
  );
  if (ok != true) return;
  try {
    await db.from('ranking_applications').update({
      'approved_rank_text': row['applied_rank_text'],
      'approved_salary': row['applied_salary'],
      'approved_date': DateFormat('yyyy-MM-dd').format(DateTime.now()),
      'updated_at': DateTime.now().toIso8601String(),
    }).eq('id', row['id']);
    showSnack(context, 'Applied rank approved.');
    refresh();
  } catch (e) {
    showSnack(context, 'Approval failed: $e');
  }
}

Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showRankingDialog(context, isAdd ? await employeeOptions() : const <EditOption>[], await cycleOptions(), await rankOptions(), row, isAdd ? await rankingAppointmentByEmployee() : const <String, String>{});
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'ranking_applications', data['employee_id'], 'ranking')) return;
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (row == null) {
      await db.from('ranking_applications').insert(data);
      if (context.mounted) showSnack(context, 'Record Added.');
    } else {
      await db.from('ranking_applications').update(data).eq('id', row['id']);
      if (context.mounted) showSnack(context, 'Record Updated.');
    }
    safeRefresh(refresh);
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Failed: $e');
  }
}

Future<Map<String, dynamic>?> showRankingDialog(BuildContext context, List<EditOption> employees, List<EditOption> cycles, List<EditOption> ranks, Map<String, dynamic>? initial, Map<String, String> appointmentByEmployee) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  String selectedEmployeeName = isAdd ? '' : linkedEmployeeName(initial);
  String? cycleId = optionValueOrFirst(initial?['cycle_id']?.toString(), cycles, true);
  final appointment = TextEditingController(text: formatEditValue(initial?['appointment']));
  final previousRank = TextEditingController(text: formatEditValue(initial?['previous_rank_text']));
  final previousSalary = TextEditingController(text: formatMoneyEdit(initial?['previous_salary']));
  final appliedRank = TextEditingController(text: formatEditValue(initial?['applied_rank_text']));
  final appliedSalary = TextEditingController(text: formatMoneyEdit(initial?['applied_salary']));
  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));

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
              : ListView.separated(itemCount: ranks.length, separatorBuilder: (_, __) => const Divider(height: 1), itemBuilder: (_, i) => ListTile(title: Text(ranks[i].label), onTap: () => Navigator.pop(context, ranks[i]))),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel'))],
      ),
    );
    if (selected == null) return;
    rank.text = selected.value;
    if (selected.salary != null) salary.text = formatMoney(selected.salary);
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
                    child: Autocomplete<EditOption>(
                      displayStringForOption: (option) => option.label,
                      optionsBuilder: (textEditingValue) {
                        final sortedEmployees = uniqueOptions(employees).toList()
                          ..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
                        final query = textEditingValue.text.trim().toLowerCase();
                        if (query.isEmpty) return sortedEmployees;
                        final normalizedQuery = normalizeName(query);
                        return sortedEmployees.where((option) {
                          final label = option.label.toLowerCase();
                          final normalizedLabel = normalizeName(option.label);
                          return label.contains(query) || normalizedLabel.contains(normalizedQuery);
                        });
                      },
                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        selectedEmployeeName = option.label;
                        appointment.text = appointmentByEmployee[option.value] ?? '';
                        applyRankSalaryForEmployee(previousRank, previousSalary, ranks, selectedEmployeeName);
                        applyRankSalaryForEmployee(appliedRank, appliedSalary, ranks, selectedEmployeeName);
                      }),
                      fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: 'Employee Name',
                          hintText: 'Select or type employee name',
                          suffixIcon: Icon(Icons.search_rounded),
                        ),
                        validator: (_) => employeeId == null || employeeId!.isEmpty ? 'Please select employee from the list' : null,
                        onChanged: (value) => setDialogState(() {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees).where((option) => option.label.toLowerCase() == typed).toList();
                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            selectedEmployeeName = exact.first.label;
                            appointment.text = appointmentByEmployee[exact.first.value] ?? '';
                            applyRankSalaryForEmployee(previousRank, previousSalary, ranks, selectedEmployeeName);
                            applyRankSalaryForEmployee(appliedRank, appliedSalary, ranks, selectedEmployeeName);
                          } else {
                            employeeId = null;
                            selectedEmployeeName = '';
                            appointment.text = '';
                          }
                        }),
                      ),
                      optionsViewBuilder: (context, onSelected, options) => Align(
                        alignment: Alignment.topLeft,
                        child: Material(
                          elevation: 6,
                          borderRadius: BorderRadius.circular(14),
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 520, maxHeight: 320),
                            child: ListView.separated(
                              padding: EdgeInsets.zero,
                              shrinkWrap: true,
                              itemCount: options.length,
                              separatorBuilder: (_, __) => const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final option = options.elementAt(index);
                                return ListTile(
                                  dense: true,
                                  title: Text(option.label, overflow: TextOverflow.ellipsis),
                                  onTap: () => onSelected(option),
                                );
                              },
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                textBox('Appointment', appointment, readOnly: true),
                if (isAdd)
                  rankAutocompleteBox('Previous Rank', previousRank, previousSalary, ranks, selectedEmployeeName)
                else
                  textBox('Previous Rank', previousRank, readOnly: true),
                textBox('Previous Salary', previousSalary, kind: FieldKind.number, readOnly: true),
                if (!isAdd) ...[
                  textBox('Points Earned', points, kind: FieldKind.number),
                  rankAutocompleteBox('Applied Rank', appliedRank, appliedSalary, ranks, selectedEmployeeName),
                  textBox('Applied Salary', appliedSalary, kind: FieldKind.number),
                ],
                SizedBox(width: 728, child: Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)), child: Text(isAdd ? 'Select Employee, then pick the Previous Rank to auto-fill Previous Salary. Applied rank and points can be updated later using Edit.' : 'Employee name is locked here. Use the table Approve button to approve the applied rank.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)))),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              FocusManager.instance.primaryFocus?.unfocus();
              final out = <String, dynamic>{
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text),
                'previous_rank_text': emptyToNull(previousRank.text),
                'previous_salary': parseMoneyInput(previousSalary.text),
              };
              if (!isAdd) {
                out.addAll({
                  'applied_rank_text': emptyToNull(appliedRank.text),
                  'applied_salary': parseMoneyInput(appliedSalary.text),
                  'points_earned': num.tryParse(points.text.trim()),
                });
              }
              Navigator.of(context, rootNavigator: true).pop(out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  await Future<void>.delayed(Duration.zero);
  for (final c in [appointment, previousRank, previousSalary, appliedRank, appliedSalary, points]) {
    c.dispose();
  }
  return result;
}

Widget textBox(String label, TextEditingController controller, {FieldKind kind = FieldKind.text, bool readOnly = false}) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: readOnly,
        keyboardType: kind == FieldKind.number || kind == FieldKind.integer ? TextInputType.number : TextInputType.text,
        maxLines: kind == FieldKind.multiline ? 3 : 1,
        style: TextStyle(color: readOnly ? _muted : _ink, fontWeight: readOnly ? FontWeight.w800 : FontWeight.w500),
        decoration: InputDecoration(labelText: label, fillColor: readOnly ? const Color(0xFFF8FAFC) : Colors.white),
      ),
    );

Widget rankTextBox(String label, TextEditingController controller, VoidCallback onPick) => SizedBox(
      width: 354,
      child: Row(children: [
        Expanded(child: TextFormField(controller: controller, decoration: InputDecoration(labelText: label))),
        const SizedBox(width: 8),
        OutlinedButton(onPressed: onPick, child: const Text('Pick')),
      ]),
    );

Widget rankAutocompleteBox(String label, TextEditingController controller, TextEditingController salaryController, List<EditOption> ranks, String employeeName) => SizedBox(
      width: 354,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.value,
        optionsBuilder: (textEditingValue) {
          final options = uniqueOptions(ranks).toList()..sort((a, b) => a.value.toLowerCase().compareTo(b.value.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return options;
          final normalizedQuery = normalizeRankKey(query);
          return options.where((option) {
            final value = option.value.toLowerCase();
            final labelText = option.label.toLowerCase();
            final normalizedValue = normalizeRankKey(option.value);
            return value.contains(query) || labelText.contains(query) || normalizedValue.contains(normalizedQuery);
          });
        },
        onSelected: (option) {
          controller.text = option.value;
          if (option.salary != null) salaryController.text = formatMoney(adjustedRankSalary(option.salary!, employeeName));
        },
        fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: InputDecoration(labelText: label, hintText: 'Select or type rank', suffixIcon: const Icon(Icons.search_rounded)),
          onChanged: (value) {
            controller.text = value;
            final selectedKey = normalizeRankKey(value);
            final exact = uniqueOptions(ranks).where((option) => normalizeRankKey(option.value) == selectedKey).toList();
            if (exact.isNotEmpty && exact.first.salary != null) salaryController.text = formatMoney(adjustedRankSalary(exact.first.salary!, employeeName));
          },
        ),
        optionsViewBuilder: (context, onSelected, options) => Align(
          alignment: Alignment.topLeft,
          child: Material(
            elevation: 6,
            borderRadius: BorderRadius.circular(14),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520, maxHeight: 320),
              child: ListView.separated(
                padding: EdgeInsets.zero,
                shrinkWrap: true,
                itemCount: options.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final option = options.elementAt(index);
                  return ListTile(
                    dense: true,
                    title: Text(option.value, overflow: TextOverflow.ellipsis),
                    subtitle: option.salary == null ? null : Text(formatMoney(option.salary)),
                    onTap: () => onSelected(option),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );

const _salaryAlignmentBonusSurnames = <String>{'saulong', 'epil', 'roderos', 'flores', 'saligumba'};

bool hasSalaryAlignmentBonus(Object? employeeName) {
  final normalized = normalizeName('${employeeName ?? ''}'.replaceAll(RegExp(r'[^A-Za-z0-9 ]+'), ' '));
  if (normalized.isEmpty) return false;
  final parts = normalized.split(RegExp(r'\s+'));
  return parts.any(_salaryAlignmentBonusSurnames.contains);
}

num adjustedRankSalary(num salary, Object? employeeName) => salary + (hasSalaryAlignmentBonus(employeeName) ? 1000 : 0);

EditOption? matchedRankOption(List<EditOption> ranks, String rankText) {
  final key = normalizeRankKey(rankText);
  if (key.isEmpty) return null;
  for (final option in uniqueOptions(ranks)) {
    if (normalizeRankKey(option.value) == key) return option;
  }
  return null;
}

void applyRankSalaryForEmployee(TextEditingController rankController, TextEditingController salaryController, List<EditOption> ranks, Object? employeeName) {
  final option = matchedRankOption(ranks, rankController.text);
  if (option?.salary == null) return;
  salaryController.text = formatMoney(adjustedRankSalary(option!.salary!, employeeName));
}

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
          GridCol('bio_number', 'Bio Number'),
          GridCol('gender', 'Gender'),
          GridCol('education_level', 'Educational Attainment', flex: 2),
          GridCol('date_hired_display', 'Date Hired'),
          GridCol('employment_status', 'Status'),
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
          GridCol('appointment', 'Appointment', flex: 2),
          GridCol('previous_rank_text', 'Previous Rank', flex: 2),
          GridCol('previous_salary', 'Basic Salary', isMoney: true),
          GridCol('applied_rank_text', 'Rank Applied', flex: 2),
          GridCol('applied_salary', 'Basic Salary Adjustment', flex: 2, isMoney: true),
          GridCol('points_earned', 'Points Earned', isNumber: true),
          GridCol('approved_rank_text', 'Approved Rank', flex: 2),
          GridCol('approved_date', 'Approved Date'),
          GridCol('appointment_title', 'Appointment', flex: 3),
        ]),
      ];

  Future<void> printCurrentReport(ReportConfig config) async {
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final data = await config.load();
      final rows = data.map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
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
              final rows = (snap.data ?? []).map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();
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
  Widget build(BuildContext context) => Card(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: Column(children: [
            Container(width: double.infinity, color: const Color(0xFFF8FAFC), padding: const EdgeInsets.all(16), child: Text('$title Preview', style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
            const Divider(height: 1, color: _line),
            Expanded(
              child: rows.isEmpty
                  ? const EmptyBox()
                  : ListView.separated(
                      itemCount: rows.take(50).length,
                      separatorBuilder: (_, __) => const Divider(height: 1, color: _line),
                      itemBuilder: (_, i) => Container(
                        padding: const EdgeInsets.all(14),
                        child: Wrap(spacing: 12, runSpacing: 8, children: [
                          for (final c in columns)
                            SizedBox(width: 180, child: Text('${c.label}: ${c.isMoney ? formatMoney(valueFor(rows[i], c.key)) : formatValue(valueFor(rows[i], c.key))}', maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(fontWeight: c.primary ? FontWeight.w800 : FontWeight.w500, color: _ink))),
                        ]),
                      ),
                    ),
            ),
          ]),
        ),
      );
}

String buildPrintableReportHtml(String title, List<GridCol> columns, List<Map<String, dynamic>> rows) {
  final cols = columns.map((c) => '<th>${escapeHtml(c.label)}</th>').join();
  final body = rows.map((r) => '<tr>${columns.map((c) => '<td>${escapeHtml(c.isMoney ? formatMoney(valueFor(r, c.key)) : formatValue(valueFor(r, c.key)))}</td>').join()}</tr>').join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 landscape;margin:12mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #cbd5e1;padding:6px;text-align:left;vertical-align:top}th{background:#eff6ff}</style></head><body><h1>${escapeHtml(title)}</h1><table><thead><tr>$cols</tr></thead><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}

List<EditField> employeeEditFields() => const [
      EditField('full_name', 'Full Name', required: true),
      EditField('bio_number', 'Bio Number'),
      EditField('gender', 'Gender', kind: FieldKind.dropdown, options: [EditOption('Male', 'Male'), EditOption('Female', 'Female')]),
      EditField('civil_status', 'Civil Status'),
      EditField('birth_date', 'Birth Date', kind: FieldKind.date),
      EditField('address', 'Address', kind: FieldKind.multiline, lines: 2),
      EditField('contact_number', 'Contact Number'),
      EditField('email', 'Email'),
      EditField('education_level', 'Educational Attainment'),
      EditField('school_graduated', 'School Graduated'),
      EditField('degree_course', 'Degree / Course'),
      EditField('guardian_name', 'Guardian Name'),
      EditField('guardian_relationship', 'Guardian Relationship'),
      EditField('guardian_contact', 'Guardian Contact'),
      EditField('guardian_address', 'Guardian Address', kind: FieldKind.multiline, lines: 2),
      EditField('designation', 'Designation'),
      EditField('employee_type', 'Employee Type', kind: FieldKind.dropdown, options: [EditOption('full_time', 'Full Time'), EditOption('probationary', 'Probationary'), EditOption('part_time', 'Part Time'), EditOption('staff', 'Staff'), EditOption('faculty_staff', 'Faculty / Staff')]),
      EditField('teaching_status', 'Teaching Status'),
      EditField('employment_status', 'Employee Status', kind: FieldKind.dropdown, options: [EditOption('active', 'Active'), EditOption('inactive', 'Inactive'), EditOption('separated', 'Separated'), EditOption('resigned', 'Resigned')]),
      EditField('date_hired', 'Date Hired', kind: FieldKind.date),
      EditField('current_salary', 'Current Salary', kind: FieldKind.number),
      EditField('license_summary', 'License Summary'),
      EditField('notes', 'Notes', kind: FieldKind.multiline, lines: 3),
    ];

List<EditField> addEmployeeFields() => const [
      EditField('full_name', 'Full Name', required: true),
      EditField('bio_number', 'Bio Number'),
      EditField('gender', 'Gender', kind: FieldKind.dropdown, options: [EditOption('Male', 'Male'), EditOption('Female', 'Female')]),
      EditField('civil_status', 'Civil Status'),
      EditField('birth_date', 'Birth Date', kind: FieldKind.date),
      EditField('address', 'Address', kind: FieldKind.multiline, lines: 2),
      EditField('contact_number', 'Contact Number'),
      EditField('email', 'Email'),
      EditField('education_level', 'Educational Attainment'),
      EditField('school_graduated', 'School Graduated'),
      EditField('degree_course', 'Degree / Course'),
      EditField('guardian_name', 'Guardian Name'),
      EditField('guardian_relationship', 'Guardian Relationship'),
      EditField('guardian_contact', 'Guardian Contact'),
      EditField('guardian_address', 'Guardian Address', kind: FieldKind.multiline, lines: 2),
      EditField('designation', 'Designation'),
      EditField('employee_type', 'Employee Type', kind: FieldKind.dropdown, options: [EditOption('full_time', 'Full Time'), EditOption('probationary', 'Probationary'), EditOption('part_time', 'Part Time'), EditOption('staff', 'Staff'), EditOption('faculty_staff', 'Faculty / Staff')]),
      EditField('teaching_status', 'Teaching Status'),
      EditField('employment_status', 'Employee Status', kind: FieldKind.dropdown, options: [EditOption('active', 'Active'), EditOption('inactive', 'Inactive'), EditOption('separated', 'Separated'), EditOption('resigned', 'Resigned')]),
      EditField('date_hired', 'Date Hired', kind: FieldKind.date),
      EditField('current_salary', 'Current Salary', kind: FieldKind.number),
      EditField('license_summary', 'License Summary'),
      EditField('notes', 'Notes', kind: FieldKind.multiline, lines: 3),
      EditField('contract_type', 'Contract Type'),
      EditField('contract_start_date', 'Contract Start Date', kind: FieldKind.date),
      EditField('duration_months', 'Contract Duration In Months', kind: FieldKind.integer),
      EditField('contract_end_date', 'Contract End Date', kind: FieldKind.date),
      EditField('contract_attachment_url', 'Contract Attachment URL'),
      EditField('contract_status', 'Contract Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived'), EditOption('Resigned', 'Resigned')]),
      EditField('credential_kind', 'Credential Type To Add', kind: FieldKind.dropdown, options: [EditOption('license', 'License'), EditOption('certificate', 'National Certificate')]),
      EditField('license_name', 'License Name'),
      EditField('license_number', 'License Number'),
      EditField('license_issued_date', 'License Issued Date', kind: FieldKind.date),
      EditField('license_expiry_date', 'License Expiry Date', kind: FieldKind.date),
      EditField('license_attachment_url', 'License Attachment URL'),
      EditField('license_status', 'License Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
      EditField('certificate_type', 'Certificate Type'),
      EditField('certificate_name', 'Certificate Name'),
      EditField('certificate_number', 'Certificate Number'),
      EditField('certificate_issued_date', 'Certificate Issued Date', kind: FieldKind.date),
      EditField('certificate_expiry_date', 'Certificate Expiry Date', kind: FieldKind.date),
      EditField('certificate_attachment_url', 'Certificate Attachment URL'),
      EditField('certificate_status', 'Certificate Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
    ];

const employeeKeys = ['full_name', 'bio_number', 'gender', 'civil_status', 'birth_date', 'address', 'contact_number', 'email', 'education_level', 'school_graduated', 'degree_course', 'guardian_name', 'guardian_relationship', 'guardian_contact', 'guardian_address', 'designation', 'employee_type', 'teaching_status', 'employment_status', 'date_hired', 'starting_date', 'current_salary', 'license_summary', 'notes'];
const contractKeys = ['contract_type', 'contract_start_date', 'duration_months', 'contract_end_date', 'status', 'attachment_url'];
const licenseKeys = ['license_name', 'license_number', 'issued_date', 'expiry_date', 'status', 'attachment_url'];
const certificateKeys = ['certificate_type', 'certificate_name', 'certificate_number', 'issued_date', 'expiry_date', 'status', 'attachment_url'];

Map<String, dynamic> extractKeys(Map<String, dynamic> data, List<String> keys) {
  final out = <String, dynamic>{};
  for (final key in keys) {
    Object? value;
    if (data.containsKey(key)) value = data[key];
    final isContract = keys.contains('contract_type');
    final isLicense = keys.contains('license_name');
    final isCertificate = keys.contains('certificate_name');
    if (key == 'status') {
      value = isContract ? data['contract_status'] : isLicense ? data['license_status'] : isCertificate ? data['certificate_status'] : data[key];
    }
    if (key == 'attachment_url') {
      value = isContract ? data['contract_attachment_url'] : isLicense ? data['license_attachment_url'] : isCertificate ? data['certificate_attachment_url'] : data[key];
    }
    if (key == 'issued_date') value = isLicense ? data['license_issued_date'] : isCertificate ? data['certificate_issued_date'] : data[key];
    if (key == 'expiry_date') value = isLicense ? data['license_expiry_date'] : isCertificate ? data['certificate_expiry_date'] : data[key];
    if (value != null && value.toString().trim().isNotEmpty) out[key] = value;
  }
  return out;
}

bool hasUsefulValue(Map<String, dynamic> data, List<String> keys) => keys.any((k) => data[k] != null && data[k].toString().trim().isNotEmpty);

Object? parseFieldValue(String text, FieldKind kind) {
  final value = text.trim();
  if (value.isEmpty) return null;
  if (kind == FieldKind.number) return num.tryParse(value.replaceAll(RegExp(r'[^0-9.\-]'), ''));
  if (kind == FieldKind.integer) return int.tryParse(value.replaceAll(RegExp(r'[^0-9\-]'), ''));
  if (kind == FieldKind.date) return toIsoDateInput(value);
  return value;
}

Object? emptyToNull(Object? value) {
  if (value == null) return null;
  final text = value.toString().trim();
  return text.isEmpty ? null : value;
}

String? optionValueOrFirst(String? raw, List<EditOption> options, bool required) {
  final values = options.map((o) => o.value).toSet();
  if (raw != null && raw.isNotEmpty && values.contains(raw)) return raw;
  if (required && options.isNotEmpty) return options.first.value;
  if (!required && raw != null && raw.isNotEmpty && values.contains(raw)) return raw;
  return null;
}

List<EditOption> uniqueOptions(List<EditOption> options) {
  final seen = <String>{};
  final out = <EditOption>[];
  for (final o in options) {
    if (seen.add(o.value)) out.add(o);
  }
  return out;
}

Map<String, dynamic> normalizeRow(Map<String, dynamic> row) {
  final out = Map<String, dynamic>.from(row);
  if (out['employees'] is Map) out['employee_name'] = out['employees']['full_name'];
  if (out['ranking_cycles'] is Map) out['cycle_name'] = out['ranking_cycles']['name'];
  if (out.containsKey('appointment')) {
    final appointmentText = '${out['appointment'] ?? ''}'.trim();
    final parts = appointmentText.split(RegExp(r'\s+-\s+'));
    if (parts.length >= 2 && (parts.first.toLowerCase().contains('full') || parts.first.toLowerCase().contains('probationary'))) {
      out['appointment_category'] = parts.first;
      out['appointment_title'] = parts.skip(1).join(' - ');
    } else {
      out['appointment_category'] = '-';
      out['appointment_title'] = appointmentText.isEmpty ? '-' : appointmentText;
    }
  }
  if (out['date_hired'] == null || out['date_hired'].toString().isEmpty) out['date_hired'] = out['starting_date'];
  out['date_hired_display'] = out['date_hired'] ?? out['starting_date'];
  if (out.containsKey('contract_end_date')) out['days_left'] = daysLeft(out['contract_end_date']);
  return out;
}

Object? valueFor(Map<String, dynamic> row, String key) => normalizeRow(row)[key];

String searchableText(Map<String, dynamic> row) => row.values.map((v) {
      if (v is Map) return v.values.join(' ');
      return '$v';
    }).join(' ').toLowerCase();

int compareRows(Map<String, dynamic> a, Map<String, dynamic> b, String key, bool asc) {
  final av = valueFor(a, key);
  final bv = valueFor(b, key);
  final an = num.tryParse('${av ?? ''}');
  final bn = num.tryParse('${bv ?? ''}');
  int result;
  if (an != null && bn != null) {
    result = an.compareTo(bn);
  } else {
    result = formatValue(av).toLowerCase().compareTo(formatValue(bv).toLowerCase());
  }
  return asc ? result : -result;
}

bool looksLikeDateText(String text) => RegExp(r'^\d{4}-\d{2}-\d{2}').hasMatch(text.trim()) || RegExp(r'^[A-Za-z]+\s+\d{1,2},\s*\d{4}$').hasMatch(text.trim()) || RegExp(r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$').hasMatch(text.trim());

DateTime? parseFlexibleDate(Object? value) {
  if (value == null) return null;
  final text = value.toString().trim();
  if (text.isEmpty || text == '-') return null;
  final iso = RegExp(r'^(\d{4})-(\d{2})-(\d{2})').firstMatch(text);
  if (iso != null) return DateTime.tryParse('${iso.group(1)}-${iso.group(2)}-${iso.group(3)}');
  for (final pattern in const ['MMMM dd, yyyy', 'MMMM d, yyyy', 'MMM dd, yyyy', 'MMM d, yyyy', 'MM-dd-yyyy', 'M-d-yyyy', 'MM/dd/yyyy', 'M/d/yyyy']) {
    try {
      return DateFormat(pattern).parseStrict(text);
    } catch (_) {}
  }
  return null;
}

String formatDateLong(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return formatValueRaw(value);
  return DateFormat('MMMM dd, yyyy').format(parsed);
}

String? toIsoDateInput(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return value == null || value.toString().trim().isEmpty ? null : value.toString().trim();
  return DateFormat('yyyy-MM-dd').format(parsed);
}

String formatValueRaw(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  return text;
}

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  if (looksLikeDateText(text)) return formatDateLong(text);
  return text;
}

String formatEditValue(Object? value) {
  if (value == null) return '';
  final raw = formatValueRaw(value);
  if (raw == '-') return '';
  return looksLikeDateText(raw) ? formatDateLong(raw) : raw;
}

String formatMoneyEdit(Object? value) {
  final text = formatMoney(value);
  return text == '-' ? '' : text;
}

num? parseMoneyInput(String text) {
  final cleaned = text.replaceAll(RegExp(r'[^0-9.\-]'), '');
  if (cleaned.trim().isEmpty) return null;
  return num.tryParse(cleaned);
}

String formatDetailValue(Object? value, String key) {
  if (key.contains('salary')) return formatMoney(value);
  if (key.contains('date')) return formatDateLong(value);
  return formatValue(value);
}

String formatMoney(Object? value) {
  final n = num.tryParse('${value ?? ''}');
  if (n == null) return formatValue(value);
  return NumberFormat.currency(symbol: 'PHP ', decimalDigits: 2).format(n);
}

String formatNumber(Object? value) {
  final n = num.tryParse('${value ?? ''}');
  if (n == null) return formatValue(value);
  return n % 1 == 0 ? n.toInt().toString() : n.toStringAsFixed(2);
}

int? daysLeft(Object? date) {
  if (date == null) return null;
  final parsed = parseFlexibleDate(date);
  if (parsed == null) return null;
  final today = DateTime.now();
  final base = DateTime(today.year, today.month, today.day);
  return DateTime(parsed.year, parsed.month, parsed.day).difference(base).inDays;
}

String normalizeName(String input) => input.trim().toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
String normalizeRankKey(String input) => input.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
String titleCase(String input) => input.split('_').map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}').join(' ');
String escapeHtml(String input) => input.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');

void showSnack(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}

