import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment('SUPABASE_URL', defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co');
const publicClientKey = String.fromEnvironment('SUPABASE_PUBLIC_CLIENT_KEY');

const _primary = Color(0xFF2563EB);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF8FAFC);
const _cardBorder = Color(0xFFE2E8F0);

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
          colorScheme: ColorScheme.fromSeed(seedColor: _primary, brightness: Brightness.light),
          scaffoldBackgroundColor: _bg,
          fontFamily: 'Arial',
          cardTheme: CardThemeData(
            elevation: 0,
            color: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: _cardBorder)),
            margin: EdgeInsets.zero,
          ),
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _cardBorder)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _cardBorder)),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _primary, width: 1.4)),
          ),
        ),
        home: publicClientKey.isEmpty ? const SetupPage() : const ShellPage(),
      );
}

class SetupPage extends StatelessWidget {
  const SetupPage({super.key});

  @override
  Widget build(BuildContext context) => const Scaffold(
        body: Center(
          child: SizedBox(
            width: 700,
            child: Card(
              child: Padding(
                padding: EdgeInsets.all(28),
                child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('HR Monitoring setup', style: TextStyle(fontSize: 30, fontWeight: FontWeight.w900)),
                  SizedBox(height: 12),
                  Text('Start Flutter with the Supabase project URL and public client key using --dart-define.'),
                ]),
              ),
            ),
          ),
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
      DashboardPage(onNavigate: (v) => setState(() => index = v)),
      EmployeesPage(onSaved: () => setState(() {})),
      const QueryPage(
        title: 'Contract Monitoring',
        subtitle: 'Track contract start date, duration, ending date, days remaining, and renewal status.',
        table: 'hr_contract_monitoring',
        columns: ['full_name', 'contract_type', 'contract_start_date', 'duration_months', 'contract_end_date', 'days_to_contract_end', 'computed_status'],
        searchHint: 'Search employee, contract type, or status',
      ),
      const CredentialsPage(),
      const QueryPage(
        title: 'Evaluation Records',
        subtitle: 'View superior, peer, self, student, and total evaluation ratings by academic year and semester.',
        table: 'hr_evaluation_summary',
        columns: ['full_name', 'academic_year', 'semester', 'superior_rating', 'peer_rating', 'self_rating', 'student_rating', 'total_rating', 'total_description'],
        searchHint: 'Search employee, semester, or rating description',
      ),
      const QueryPage(
        title: 'Faculty Ranking Summary',
        subtitle: 'Review previous rank, rank applied for, approved rank, salary, and points earned.',
        table: 'hr_faculty_ranking_summary',
        columns: ['full_name', 'appointment', 'previous_rank', 'previous_salary', 'rank_applied_for', 'applied_salary', 'points_earned', 'approved_rank', 'approved_salary'],
        searchHint: 'Search employee, rank, or appointment',
      ),
    ];

    return Scaffold(
      body: LayoutBuilder(builder: (context, constraints) {
        final compact = constraints.maxWidth < 980;
        return Row(children: [
          if (compact)
            NavigationRail(
              backgroundColor: Colors.white,
              selectedIndex: index,
              onDestinationSelected: (v) => setState(() => index = v),
              labelType: NavigationRailLabelType.all,
              destinations: _destinations,
            )
          else
            AppSidebar(selectedIndex: index, onChanged: (v) => setState(() => index = v)),
          const VerticalDivider(width: 1, color: _cardBorder),
          Expanded(child: pages[index]),
        ]);
      }),
    );
  }
}

const _destinations = [
  NavigationRailDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: Text('Dashboard')),
  NavigationRailDestination(icon: Icon(Icons.people_alt_outlined), selectedIcon: Icon(Icons.people_alt), label: Text('Employees')),
  NavigationRailDestination(icon: Icon(Icons.assignment_outlined), selectedIcon: Icon(Icons.assignment), label: Text('Contracts')),
  NavigationRailDestination(icon: Icon(Icons.badge_outlined), selectedIcon: Icon(Icons.badge), label: Text('Credentials')),
  NavigationRailDestination(icon: Icon(Icons.rate_review_outlined), selectedIcon: Icon(Icons.rate_review), label: Text('Evaluations')),
  NavigationRailDestination(icon: Icon(Icons.leaderboard_outlined), selectedIcon: Icon(Icons.leaderboard), label: Text('Ranking')),
];

class AppSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;
  const AppSidebar({super.key, required this.selectedIndex, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final items = [
      ('Dashboard', Icons.dashboard_outlined),
      ('Employees', Icons.people_alt_outlined),
      ('Contracts', Icons.assignment_outlined),
      ('Credentials', Icons.badge_outlined),
      ('Evaluations', Icons.rate_review_outlined),
      ('Ranking', Icons.leaderboard_outlined),
    ];
    return Container(
      width: 248,
      color: Colors.white,
      padding: const EdgeInsets.all(18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(color: _primary, borderRadius: BorderRadius.circular(14)),
            child: const Icon(Icons.school, color: Colors.white),
          ),
          const SizedBox(width: 12),
          const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
        ]),
        const SizedBox(height: 8),
        const Text('Excel-based faculty and staff records', style: TextStyle(color: _muted, fontSize: 12)),
        const SizedBox(height: 26),
        for (int i = 0; i < items.length; i++)
          SidebarItem(
            label: items[i].$1,
            icon: items[i].$2,
            selected: selectedIndex == i,
            onTap: () => onChanged(i),
          ),
        const Spacer(),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)),
          child: const Text('Tip: Use search boxes to quickly find a faculty member, license, contract, or ranking record.', style: TextStyle(fontSize: 12, color: Color(0xFF1E3A8A), height: 1.35)),
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
        padding: const EdgeInsets.only(bottom: 8),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 150),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
            decoration: BoxDecoration(color: selected ? const Color(0xFFEFF6FF) : Colors.transparent, borderRadius: BorderRadius.circular(14)),
            child: Row(children: [
              Icon(icon, color: selected ? _primary : _muted, size: 22),
              const SizedBox(width: 12),
              Text(label, style: TextStyle(fontWeight: selected ? FontWeight.w800 : FontWeight.w600, color: selected ? _primary : _ink)),
            ]),
          ),
        ),
      );
}

class DashboardPage extends StatelessWidget {
  final ValueChanged<int> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle: 'At-a-glance summary of faculty, contracts, credentials, evaluations, and ranking records.',
        child: FutureBuilder<List<dynamic>>(
          future: Supabase.instance.client.from('hr_dashboard_counts').select(),
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snap.hasError) return ErrorBox('${snap.error}', onRetry: () {});
            final row = snap.data?.isNotEmpty == true ? snap.data!.first as Map<String, dynamic> : <String, dynamic>{};
            final cards = [
              DashboardMetric('Active employees', row['active_employees'], Icons.people_alt_outlined, 'All active HR records', const Color(0xFFEFF6FF), const Color(0xFF1D4ED8)),
              DashboardMetric('Active faculty', row['active_faculty'], Icons.school_outlined, 'Faculty master list', const Color(0xFFF0FDF4), const Color(0xFF15803D)),
              DashboardMetric('For renewal', row['contracts_for_renewal'], Icons.schedule_outlined, 'Contracts due soon', const Color(0xFFFFFBEB), const Color(0xFFB45309)),
              DashboardMetric('Expired contracts', row['expired_contracts'], Icons.warning_amber_rounded, 'Needs HR action', const Color(0xFFFEF2F2), const Color(0xFFB91C1C)),
              DashboardMetric('Licenses due', row['licenses_due'], Icons.badge_outlined, 'Licenses near expiry', const Color(0xFFF5F3FF), const Color(0xFF6D28D9)),
              DashboardMetric('Certificates due', row['certificates_due'], Icons.workspace_premium_outlined, 'NCs near expiry', const Color(0xFFECFEFF), const Color(0xFF0E7490)),
              DashboardMetric('Ranking records', row['ranking_applications'], Icons.leaderboard_outlined, 'Faculty ranking cycle', const Color(0xFFF8FAFC), _ink),
            ];
            return SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Wrap(spacing: 16, runSpacing: 16, children: cards.map((m) => MetricCard(m)).toList()),
                const SizedBox(height: 24),
                const Text('Quick access', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(height: 12),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  QuickAccessCard(title: 'Review employees', subtitle: 'Open the master list', icon: Icons.people_alt_outlined, onTap: () => onNavigate(1)),
                  QuickAccessCard(title: 'Check contracts', subtitle: 'See renewal and expired items', icon: Icons.assignment_outlined, onTap: () => onNavigate(2)),
                  QuickAccessCard(title: 'View credentials', subtitle: 'Licenses and certificates', icon: Icons.badge_outlined, onTap: () => onNavigate(3)),
                  QuickAccessCard(title: 'Faculty ranking', subtitle: 'Ranking summary records', icon: Icons.leaderboard_outlined, onTap: () => onNavigate(5)),
                ]),
              ]),
            );
          },
        ),
      );
}

class DashboardMetric {
  final String title;
  final Object? value;
  final IconData icon;
  final String caption;
  final Color bg;
  final Color fg;
  const DashboardMetric(this.title, this.value, this.icon, this.caption, this.bg, this.fg);
}

class MetricCard extends StatelessWidget {
  final DashboardMetric metric;
  const MetricCard(this.metric, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 260,
        height: 142,
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Container(width: 42, height: 42, decoration: BoxDecoration(color: metric.bg, borderRadius: BorderRadius.circular(13)), child: Icon(metric.icon, color: metric.fg)),
                const Spacer(),
                Text('${metric.value ?? 0}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: _ink)),
              ]),
              const Spacer(),
              Text(metric.title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)),
              const SizedBox(height: 3),
              Text(metric.caption, style: const TextStyle(fontSize: 12, color: _muted)),
            ]),
          ),
        ),
      );
}

class QuickAccessCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback onTap;
  const QuickAccessCard({super.key, required this.title, required this.subtitle, required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 260,
        child: Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(18),
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(children: [
                Icon(icon, color: _primary),
                const SizedBox(width: 12),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                  const SizedBox(height: 3),
                  Text(subtitle, style: const TextStyle(fontSize: 12, color: _muted)),
                ])),
                const Icon(Icons.chevron_right, color: _muted),
              ]),
            ),
          ),
        ),
      );
}

class EmployeesPage extends StatelessWidget {
  final VoidCallback onSaved;
  const EmployeesPage({super.key, required this.onSaved});

  Future<List<dynamic>> load() => Supabase.instance.client
      .from('employees')
      .select('full_name, appointment, designation, employee_type, employment_status, current_salary, license_summary')
      .order('full_name')
      .limit(1000);

  Future<void> add(BuildContext context) async {
    final name = TextEditingController();
    final appointment = TextEditingController();
    final salary = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Add employee/faculty'),
        content: SizedBox(
          width: 460,
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(controller: name, decoration: const InputDecoration(labelText: 'Full name')),
            const SizedBox(height: 10),
            TextField(controller: appointment, decoration: const InputDecoration(labelText: 'Appointment')),
            const SizedBox(height: 10),
            TextField(controller: salary, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Current salary')),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Save')),
        ],
      ),
    );
    if (ok == true && name.text.trim().isNotEmpty) {
      await Supabase.instance.client.from('employees').insert({
        'name_key': normalizeName(name.text),
        'full_name': name.text.trim(),
        'appointment': cleanText(appointment.text),
        'current_salary': num.tryParse(salary.text.trim()),
        'source_workbook': 'Manual Entry',
      });
      onSaved();
    }
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Faculty and Staff Master List',
        subtitle: 'Search and review the master records imported from the Excel workbooks.',
        action: FilledButton.icon(onPressed: () => add(context), icon: const Icon(Icons.add), label: const Text('Add employee')),
        child: DataQuery(
          future: load(),
          columns: const ['full_name', 'appointment', 'designation', 'employee_type', 'employment_status', 'current_salary', 'license_summary'],
          searchHint: 'Search employee name, appointment, designation, or license',
        ),
      );
}

class CredentialsPage extends StatelessWidget {
  const CredentialsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Licenses and National Certificates',
        subtitle: 'Monitor PRC licenses, other credentials, and TESDA/National Certificate records.',
        child: ListView(children: const [
          SectionHeader(title: 'Licenses', subtitle: 'Professional licenses and expiry status'),
          SizedBox(height: 12),
          DataQueryView(
            table: 'hr_license_monitoring',
            columns: ['full_name', 'license_name', 'license_number', 'issued_date', 'expiry_date', 'computed_status'],
            searchHint: 'Search employee, license name, number, or status',
            compact: true,
          ),
          SizedBox(height: 26),
          SectionHeader(title: 'National Certificates', subtitle: 'TESDA / National Certificate monitoring'),
          SizedBox(height: 12),
          DataQueryView(
            table: 'hr_certificate_monitoring',
            columns: ['full_name', 'certificate_type', 'certificate_name', 'certificate_number', 'expiry_date', 'computed_status'],
            searchHint: 'Search employee, certificate, number, or status',
            compact: true,
          ),
        ]),
      );
}

class SectionHeader extends StatelessWidget {
  final String title;
  final String subtitle;
  const SectionHeader({super.key, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: _ink)),
        const SizedBox(height: 3),
        Text(subtitle, style: const TextStyle(color: _muted)),
      ]);
}

class QueryPage extends StatelessWidget {
  final String title, subtitle, table, searchHint;
  final List<String> columns;
  const QueryPage({super.key, required this.title, required this.subtitle, required this.table, required this.columns, required this.searchHint});

  @override
  Widget build(BuildContext context) => PageFrame(title: title, subtitle: subtitle, child: DataQueryView(table: table, columns: columns, searchHint: searchHint));
}

class DataQueryView extends StatelessWidget {
  final String table;
  final List<String> columns;
  final String searchHint;
  final bool compact;
  const DataQueryView({super.key, required this.table, required this.columns, required this.searchHint, this.compact = false});

  Future<List<dynamic>> load() => Supabase.instance.client.from(table).select(columns.join(', ')).limit(1000);

  @override
  Widget build(BuildContext context) => DataQuery(future: load(), columns: columns, searchHint: searchHint, compact: compact);
}

class DataQuery extends StatefulWidget {
  final Future<List<dynamic>> future;
  final List<String> columns;
  final String searchHint;
  final bool compact;
  const DataQuery({super.key, required this.future, required this.columns, required this.searchHint, this.compact = false});

  @override
  State<DataQuery> createState() => _DataQueryState();
}

class _DataQueryState extends State<DataQuery> {
  late Future<List<dynamic>> _future;
  String query = '';

  @override
  void initState() {
    super.initState();
    _future = widget.future;
  }

  @override
  void didUpdateWidget(covariant DataQuery oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.future != widget.future) _future = widget.future;
  }

  void refresh() => setState(() => _future = widget.future);

  @override
  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
          if (snap.hasError) return ErrorBox('${snap.error}', onRetry: refresh);
          final rows = snap.data?.cast<Map<String, dynamic>>() ?? [];
          final filtered = query.trim().isEmpty
              ? rows
              : rows.where((row) => row.values.any((v) => v.toString().toLowerCase().contains(query.toLowerCase()))).toList();

          return Column(crossAxisAlignment: CrossAxisAlignment.stretch, mainAxisSize: widget.compact ? MainAxisSize.min : MainAxisSize.max, children: [
            DataToolbar(
              total: rows.length,
              showing: filtered.length,
              hint: widget.searchHint,
              onSearch: (v) => setState(() => query = v),
              onRefresh: refresh,
            ),
            const SizedBox(height: 12),
            if (filtered.isEmpty)
              const EmptyBox()
            else
              Flexible(
                fit: widget.compact ? FlexFit.loose : FlexFit.tight,
                child: Card(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(18),
                    child: SingleChildScrollView(
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: DataTable(
                          headingRowColor: MaterialStateProperty.all(const Color(0xFFF8FAFC)),
                          columnSpacing: 28,
                          horizontalMargin: 18,
                          columns: widget.columns.map((c) => DataColumn(label: Text(labelFor(c), style: const TextStyle(fontWeight: FontWeight.w900, color: _ink)))).toList(),
                          rows: filtered.map((row) => DataRow(cells: widget.columns.map((c) => DataCell(cellFor(c, row[c]))).toList())).toList(),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ]);
        },
      );
}

class DataToolbar extends StatelessWidget {
  final int total;
  final int showing;
  final String hint;
  final ValueChanged<String> onSearch;
  final VoidCallback onRefresh;
  const DataToolbar({super.key, required this.total, required this.showing, required this.hint, required this.onSearch, required this.onRefresh});

  @override
  Widget build(BuildContext context) => Wrap(
        spacing: 12,
        runSpacing: 12,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          SizedBox(
            width: 430,
            child: TextField(
              onChanged: onSearch,
              decoration: InputDecoration(prefixIcon: const Icon(Icons.search), hintText: hint, contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14)),
            ),
          ),
          Chip(label: Text('Showing $showing of $total records'), avatar: const Icon(Icons.table_rows_outlined, size: 18), backgroundColor: Colors.white, side: const BorderSide(color: _cardBorder)),
          OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh), label: const Text('Refresh')),
        ],
      );
}

class PageFrame extends StatelessWidget {
  final String title, subtitle;
  final Widget child;
  final Widget? action;
  const PageFrame({super.key, required this.title, required this.subtitle, required this.child, this.action});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(28, 24, 28, 28),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w900, color: _ink, height: 1.1)),
              const SizedBox(height: 8),
              Text(subtitle, style: const TextStyle(color: _muted, fontSize: 14)),
            ])),
            if (action != null) action!,
          ]),
          const SizedBox(height: 22),
          Expanded(child: child),
        ]),
      );
}

class ErrorBox extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;
  const ErrorBox(this.message, {super.key, this.onRetry});

  @override
  Widget build(BuildContext context) => Card(
        color: const Color(0xFFFFF7ED),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Icon(Icons.error_outline, color: Color(0xFFC2410C)),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('Unable to load records', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
              const SizedBox(height: 4),
              Text(message, style: const TextStyle(color: _muted)),
            ])),
            if (onRetry != null) TextButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh), label: const Text('Retry')),
          ]),
        ),
      );
}

class EmptyBox extends StatelessWidget {
  const EmptyBox({super.key});

  @override
  Widget build(BuildContext context) => const Card(
        child: Padding(
          padding: EdgeInsets.all(34),
          child: Center(child: Text('No matching records found.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600))),
        ),
      );
}

Widget cellFor(String column, Object? value) {
  if (isStatusColumn(column)) return StatusChip(label: formatValue(value));
  if (column.contains('salary')) return Text(formatMoney(value), style: const TextStyle(fontWeight: FontWeight.w700));
  if (column.contains('rating') || column.contains('points')) return Text(formatNumber(value), style: const TextStyle(fontWeight: FontWeight.w700));
  return ConstrainedBox(constraints: const BoxConstraints(maxWidth: 260), child: Text(formatValue(value), overflow: TextOverflow.ellipsis));
}

bool isStatusColumn(String column) => column.contains('status');

class StatusChip extends StatelessWidget {
  final String label;
  const StatusChip({super.key, required this.label});

  @override
  Widget build(BuildContext context) {
    final normalized = label.toLowerCase();
    Color bg = const Color(0xFFF1F5F9);
    Color fg = _ink;
    if (normalized.contains('active') || normalized.contains('ongoing') || normalized.contains('on-going')) {
      bg = const Color(0xFFDCFCE7);
      fg = const Color(0xFF166534);
    } else if (normalized.contains('renewal') || normalized.contains('due')) {
      bg = const Color(0xFFFEF3C7);
      fg = const Color(0xFF92400E);
    } else if (normalized.contains('expired') || normalized.contains('inactive') || normalized.contains('separated')) {
      bg = const Color(0xFFFEE2E2);
      fg = const Color(0xFF991B1B);
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)),
      child: Text(label, style: TextStyle(color: fg, fontSize: 12, fontWeight: FontWeight.w900)),
    );
  }
}

String cleanText(String value) => value.trim().isEmpty ? '' : value.trim();
String normalizeName(String value) => value.trim().replaceAll(RegExp(r'\s+'), ' ').toUpperCase();

String labelFor(String column) {
  const labels = {
    'full_name': 'Employee Name',
    'employee_code': 'Employee ID',
    'appointment': 'Appointment',
    'designation': 'Designation',
    'employee_type': 'Type',
    'employment_status': 'Status',
    'current_salary': 'Current Salary',
    'license_summary': 'License Summary',
    'contract_type': 'Contract Type',
    'contract_start_date': 'Start Date',
    'duration_months': 'Duration',
    'contract_end_date': 'End Date',
    'days_to_contract_end': 'Days Left',
    'computed_status': 'Status',
    'license_name': 'License',
    'license_number': 'License No.',
    'issued_date': 'Issued',
    'expiry_date': 'Expiry',
    'certificate_type': 'Certificate Type',
    'certificate_name': 'Certificate',
    'certificate_number': 'Certificate No.',
    'academic_year': 'Academic Year',
    'semester': 'Semester',
    'superior_rating': 'Superior',
    'peer_rating': 'Peer',
    'self_rating': 'Self',
    'student_rating': 'Student',
    'total_rating': 'Total',
    'total_description': 'Description',
    'previous_rank': 'Previous Rank',
    'previous_salary': 'Previous Salary',
    'rank_applied_for': 'Applied Rank',
    'applied_salary': 'Applied Salary',
    'points_earned': 'Points',
    'approved_rank': 'Approved Rank',
    'approved_salary': 'Approved Salary',
  };
  return labels[column] ?? column.replaceAll('_', ' ').toUpperCase();
}

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString().trim();
  if (text.isEmpty || text.toLowerCase() == 'null') return '-';
  final date = DateTime.tryParse(text);
  if (date != null && text.contains('-')) return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  return text.replaceAll('_', ' ');
}

String formatMoney(Object? value) {
  final n = num.tryParse(value?.toString() ?? '');
  if (n == null) return '-';
  final s = n.toStringAsFixed(2);
  final parts = s.split('.');
  final whole = parts.first.replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',');
  return 'PHP $whole.${parts.last}';
}

String formatNumber(Object? value) {
  final n = num.tryParse(value?.toString() ?? '');
  if (n == null) return '-';
  return n % 1 == 0 ? n.toInt().toString() : n.toStringAsFixed(2);
}
