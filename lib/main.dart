import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment('SUPABASE_URL', defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co');
const publicClientKey = String.fromEnvironment('SUPABASE_PUBLIC_CLIENT_KEY');

const _primary = Color(0xFF2563EB);
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
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'HR Monitoring',
        theme: ThemeData(
          useMaterial3: true,
          scaffoldBackgroundColor: _bg,
          colorScheme: ColorScheme.fromSeed(seedColor: _primary),
          cardTheme: CardThemeData(
            elevation: 0,
            color: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: _line)),
          ),
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _line)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _line)),
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
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.all(18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(width: 42, height: 42, decoration: BoxDecoration(color: _primary, borderRadius: BorderRadius.circular(14)), child: const Icon(Icons.school, color: Colors.white)),
          const SizedBox(width: 12),
          const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
        ]),
        const SizedBox(height: 6),
        const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted)),
        const SizedBox(height: 26),
        for (var i = 0; i < items.length; i++) SidebarItem(label: items[i].$1, icon: items[i].$2, selected: selectedIndex == i, onTap: () => onChanged(i)),
        const Spacer(),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)),
          child: const Text('Records are paginated: 10 per page. Use search to filter across all records.', style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 12, height: 1.35)),
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
            duration: const Duration(milliseconds: 140),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
            decoration: BoxDecoration(color: selected ? const Color(0xFFEFF6FF) : Colors.transparent, borderRadius: BorderRadius.circular(14)),
            child: Row(children: [
              Icon(icon, color: selected ? _primary : _muted),
              const SizedBox(width: 12),
              Text(label, style: TextStyle(fontWeight: selected ? FontWeight.w900 : FontWeight.w600, color: selected ? _primary : _ink)),
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
          Text(title, style: const TextStyle(fontSize: 30, height: 1.1, fontWeight: FontWeight.w900, color: _ink)),
          const SizedBox(height: 8),
          Text(subtitle, style: const TextStyle(color: _muted)),
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
              Metric('Active employees', row['active_employees'], Icons.people_alt_outlined, const Color(0xFFEFF6FF), const Color(0xFF1D4ED8)),
              Metric('Active faculty', row['active_faculty'], Icons.school_outlined, const Color(0xFFF0FDF4), const Color(0xFF15803D)),
              Metric('For renewal', row['contracts_for_renewal'], Icons.schedule_outlined, const Color(0xFFFFFBEB), const Color(0xFFB45309)),
              Metric('Expired contracts', row['expired_contracts'], Icons.warning_amber_rounded, const Color(0xFFFEF2F2), const Color(0xFFB91C1C)),
              Metric('Licenses due', row['licenses_due'], Icons.badge_outlined, const Color(0xFFF5F3FF), const Color(0xFF6D28D9)),
              Metric('Certificates due', row['certificates_due'], Icons.workspace_premium_outlined, const Color(0xFFECFEFF), const Color(0xFF0E7490)),
              Metric('Ranking records', row['ranking_applications'], Icons.leaderboard_outlined, const Color(0xFFF8FAFC), _ink),
            ];
            return SingleChildScrollView(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Wrap(spacing: 16, runSpacing: 16, children: cards.map((m) => MetricCard(m)).toList()),
                const SizedBox(height: 24),
                Wrap(spacing: 14, runSpacing: 14, children: [
                  QuickCard('Manage employees', Icons.people_alt_outlined, () => onNavigate(1)),
                  QuickCard('Manage contracts', Icons.assignment_outlined, () => onNavigate(2)),
                  QuickCard('Manage credentials', Icons.badge_outlined, () => onNavigate(3)),
                  QuickCard('Manage ranking', Icons.leaderboard_outlined, () => onNavigate(5)),
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
        height: 134,
        child: Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Container(width: 42, height: 42, decoration: BoxDecoration(color: metric.bg, borderRadius: BorderRadius.circular(13)), child: Icon(metric.icon, color: metric.fg)), const Spacer(), Text('${metric.value ?? 0}', style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: _ink))]),
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
  Widget build(BuildContext context) => SizedBox(
        width: 250,
        child: Card(child: InkWell(borderRadius: BorderRadius.circular(18), onTap: onTap, child: Padding(padding: const EdgeInsets.all(18), child: Row(children: [Icon(icon, color: _primary), const SizedBox(width: 12), Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))), const Icon(Icons.chevron_right, color: _muted)])))),
      );
}

class EmployeesPage extends StatelessWidget {
  const EmployeesPage({super.key});
  Future<List<dynamic>> load() => db.from('employees').select('id, full_name, appointment, designation, employee_type, employment_status, current_salary, license_summary').order('full_name').limit(1500);

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Create, edit, delete, and search employee or faculty master records.',
        child: CrudList(
          load: load,
          searchHint: 'Search employee name, appointment, status, or license',
          addLabel: 'Add employee',
          titleKey: 'full_name',
          subtitleKeys: const ['appointment', 'designation'],
          fields: const [
            ListField('employment_status', 'Status', isStatus: true),
            ListField('employee_type', 'Type'),
            ListField('current_salary', 'Salary', isMoney: true),
            ListField('license_summary', 'License'),
          ],
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
        child: CrudList(
          load: load,
          searchHint: 'Search employee, contract type, date, or status',
          addLabel: 'Add contract',
          titleKey: 'employee_name',
          subtitleKeys: const ['contract_type'],
          fields: const [
            ListField('status', 'Status', isStatus: true),
            ListField('contract_start_date', 'Start'),
            ListField('duration_months', 'Months', isNumber: true),
            ListField('contract_end_date', 'End'),
          ],
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
  Future<List<dynamic>> load() => db.from('employee_licenses').select('id, employee_id, license_name, license_number, issued_date, expiry_date, status, employees(full_name)').order('expiry_date').limit(1500);

  @override
  Widget build(BuildContext context) => CrudList(
        load: load,
        searchHint: 'Search employee, license name, number, or status',
        addLabel: 'Add license',
        titleKey: 'employee_name',
        subtitleKeys: const ['license_name'],
        fields: const [
          ListField('status', 'Status', isStatus: true),
          ListField('license_number', 'License No.'),
          ListField('issued_date', 'Issued'),
          ListField('expiry_date', 'Expiry'),
        ],
        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onEdit: (ctx, row, refresh) => editLicense(ctx, row, refresh),
        onDelete: (row) => db.from('employee_licenses').delete().eq('id', row['id']),
      );
}

class CertificatesTab extends StatelessWidget {
  const CertificatesTab({super.key});
  Future<List<dynamic>> load() => db.from('employee_certificates').select('id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, employees(full_name)').order('expiry_date').limit(1500);

  @override
  Widget build(BuildContext context) => CrudList(
        load: load,
        searchHint: 'Search employee, certificate, number, or status',
        addLabel: 'Add certificate',
        titleKey: 'employee_name',
        subtitleKeys: const ['certificate_name'],
        fields: const [
          ListField('status', 'Status', isStatus: true),
          ListField('certificate_type', 'Type'),
          ListField('certificate_number', 'Certificate No.'),
          ListField('expiry_date', 'Expiry'),
        ],
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
        child: CrudList(
          load: load,
          searchHint: 'Search employee, academic year, semester, or description',
          addLabel: 'Add evaluation',
          titleKey: 'employee_name',
          subtitleKeys: const ['academic_year', 'semester'],
          fields: const [
            ListField('total_rating', 'Total', isNumber: true),
            ListField('superior_rating', 'Superior', isNumber: true),
            ListField('peer_rating', 'Peer', isNumber: true),
            ListField('student_rating', 'Student', isNumber: true),
            ListField('total_description', 'Description'),
          ],
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
        subtitle: 'Manage faculty ranking applications, points, ranks, and salaries.',
        child: CrudList(
          load: load,
          searchHint: 'Search employee, cycle, rank, or appointment',
          addLabel: 'Add ranking',
          titleKey: 'employee_name',
          subtitleKeys: const ['cycle_name', 'appointment'],
          fields: const [
            ListField('points_earned', 'Points', isNumber: true),
            ListField('previous_rank_text', 'Previous Rank'),
            ListField('applied_rank_text', 'Applied Rank'),
            ListField('approved_rank_text', 'Approved Rank'),
            ListField('approved_salary', 'Approved Salary', isMoney: true),
          ],
          onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
          onEdit: (ctx, row, refresh) => editRanking(ctx, row, refresh),
          onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
        ),
      );
}

class ListField {
  final String key;
  final String label;
  final bool isStatus;
  final bool isMoney;
  final bool isNumber;
  const ListField(this.key, this.label, {this.isStatus = false, this.isMoney = false, this.isNumber = false});
}

typedef AddHandler = Future<void> Function(BuildContext context, VoidCallback refresh);
typedef EditHandler = Future<void> Function(BuildContext context, Map<String, dynamic> row, VoidCallback refresh);

class CrudList extends StatefulWidget {
  final Future<List<dynamic>> Function() load;
  final String searchHint;
  final String addLabel;
  final String titleKey;
  final List<String> subtitleKeys;
  final List<ListField> fields;
  final AddHandler onAdd;
  final EditHandler onEdit;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  const CrudList({super.key, required this.load, required this.searchHint, required this.addLabel, required this.titleKey, required this.subtitleKeys, required this.fields, required this.onAdd, required this.onEdit, required this.onDelete});

  @override
  State<CrudList> createState() => _CrudListState();
}

class _CrudListState extends State<CrudList> {
  late Future<List<dynamic>> future;
  String query = '';
  int page = 0;

  @override
  void initState() {
    super.initState();
    future = widget.load();
  }

  void refresh() => setState(() {
        future = widget.load();
        page = 0;
      });

  void setSearch(String value) => setState(() {
        query = value;
        page = 0;
      });

  @override
  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(
        future: future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
          if (snap.hasError) return ErrorBox('${snap.error}');

          final rows = snap.data?.cast<Map<String, dynamic>>() ?? [];
          final filtered = query.trim().isEmpty ? rows : rows.where((r) => searchableText(r).contains(query.toLowerCase())).toList();
          final pageCount = filtered.isEmpty ? 1 : ((filtered.length - 1) ~/ _pageSize) + 1;
          final safePage = page.clamp(0, pageCount - 1).toInt();
          final startIndex = filtered.isEmpty ? 0 : safePage * _pageSize;
          final pageRows = filtered.skip(startIndex).take(_pageSize).toList();
          final endIndex = filtered.isEmpty ? 0 : startIndex + pageRows.length;

          return Column(children: [
            ListToolbar(
              total: rows.length,
              showing: filtered.length,
              hint: widget.searchHint,
              addLabel: widget.addLabel,
              onSearch: setSearch,
              onRefresh: refresh,
              onAdd: () => widget.onAdd(context, refresh),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: filtered.isEmpty
                  ? const EmptyBox()
                  : ListView.separated(
                      keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
                      itemCount: pageRows.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (_, i) => RecordCard(
                        row: pageRows[i],
                        titleKey: widget.titleKey,
                        subtitleKeys: widget.subtitleKeys,
                        fields: widget.fields,
                        onEdit: () => widget.onEdit(context, pageRows[i], refresh),
                        onDelete: () => confirmDelete(context, pageRows[i]),
                      ),
                    ),
            ),
            const SizedBox(height: 12),
            PaginationFooter(
              page: safePage,
              pageCount: pageCount,
              start: startIndex + 1,
              end: endIndex,
              total: filtered.length,
              onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null,
              onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null,
            ),
          ]);
        },
      );

  Future<void> confirmDelete(BuildContext context, Map<String, dynamic> row) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Delete record?'),
        content: Text('This will remove ${formatValue(valueFor(row, widget.titleKey))} from this module.'),
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
      if (mounted) showSnack(context, 'Record deleted.');
    } catch (e) {
      if (mounted) showSnack(context, 'Delete failed: $e');
    }
  }
}

class ListToolbar extends StatelessWidget {
  final int total;
  final int showing;
  final String hint;
  final String addLabel;
  final ValueChanged<String> onSearch;
  final VoidCallback onRefresh;
  final VoidCallback onAdd;
  const ListToolbar({super.key, required this.total, required this.showing, required this.hint, required this.addLabel, required this.onSearch, required this.onRefresh, required this.onAdd});

  @override
  Widget build(BuildContext context) => Row(children: [
        Expanded(child: TextField(onChanged: onSearch, decoration: InputDecoration(prefixIcon: const Icon(Icons.search), hintText: hint, contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14)))),
        const SizedBox(width: 12),
        Chip(avatar: const Icon(Icons.list_alt_outlined, size: 18), label: Text('$showing of $total'), backgroundColor: Colors.white, side: const BorderSide(color: _line)),
        const SizedBox(width: 12),
        OutlinedButton.icon(onPressed: onRefresh, icon: const Icon(Icons.refresh), label: const Text('Refresh')),
        const SizedBox(width: 12),
        FilledButton.icon(onPressed: onAdd, icon: const Icon(Icons.add), label: Text(addLabel)),
      ]);
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
    final text = total == 0 ? 'No records' : 'Showing $start-$end of $total • Page ${page + 1} of $pageCount • 10 per page';
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Row(children: [
          Expanded(child: Text(text, style: const TextStyle(color: _muted, fontWeight: FontWeight.w700))),
          OutlinedButton.icon(onPressed: onPrevious, icon: const Icon(Icons.chevron_left), label: const Text('Previous')),
          const SizedBox(width: 8),
          FilledButton.icon(onPressed: onNext, icon: const Text('Next'), label: const Icon(Icons.chevron_right)),
        ]),
      ),
    );
  }
}

class RecordCard extends StatelessWidget {
  final Map<String, dynamic> row;
  final String titleKey;
  final List<String> subtitleKeys;
  final List<ListField> fields;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  const RecordCard({super.key, required this.row, required this.titleKey, required this.subtitleKeys, required this.fields, required this.onEdit, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    final title = formatValue(valueFor(row, titleKey));
    final subtitles = subtitleKeys.map((k) => formatValue(valueFor(row, k))).where((v) => v != '-' && v.trim().isNotEmpty).join(' • ');

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w900, color: _ink, fontSize: 15)),
              if (subtitles.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(subtitles, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: _muted, fontSize: 13)),
              ],
              const SizedBox(height: 12),
              Wrap(spacing: 10, runSpacing: 10, children: fields.map((f) => FieldPill(field: f, value: valueFor(row, f.key))).toList()),
            ]),
          ),
          const SizedBox(width: 10),
          Row(mainAxisSize: MainAxisSize.min, children: [
            IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_outlined, color: _primary)),
            IconButton(tooltip: 'Delete', onPressed: onDelete, icon: const Icon(Icons.delete_outline, color: _danger)),
          ]),
        ]),
      ),
    );
  }
}

class FieldPill extends StatelessWidget {
  final ListField field;
  final Object? value;
  const FieldPill({super.key, required this.field, required this.value});

  @override
  Widget build(BuildContext context) {
    if (field.isStatus) return StatusChip(formatValue(value));
    final display = field.isMoney ? formatMoney(value) : field.isNumber ? formatNumber(value) : formatValue(value);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(12), border: Border.all(color: _line)),
      child: Text('${field.label}: $display', style: const TextStyle(fontSize: 12, color: _ink, fontWeight: FontWeight.w700)),
    );
  }
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
    return Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7), decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)), child: Text(label, style: TextStyle(color: fg, fontSize: 12, fontWeight: FontWeight.w900)));
  }
}

class ErrorBox extends StatelessWidget {
  final String message;
  const ErrorBox(this.message, {super.key});

  @override
  Widget build(BuildContext context) => Card(color: const Color(0xFFFFF7ED), child: Padding(padding: const EdgeInsets.all(18), child: Text('Unable to load records: $message', style: const TextStyle(color: Color(0xFF9A3412)))));
}

class EmptyBox extends StatelessWidget {
  const EmptyBox({super.key});

  @override
  Widget build(BuildContext context) => const Card(child: Center(child: Padding(padding: EdgeInsets.all(34), child: Text('No matching records found.', style: TextStyle(color: _muted, fontWeight: FontWeight.w700)))));
}

enum FieldKind { text, number, integer, date, dropdown, multiline }

class EditOption {
  final String value;
  final String label;
  const EditOption(this.value, this.label);
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
    final v = initial?[f.key];
    if (f.kind == FieldKind.dropdown) {
      selected[f.key] = v?.toString().isNotEmpty == true ? v.toString() : (f.options.isNotEmpty ? f.options.first.value : null);
    } else {
      controllers[f.key] = TextEditingController(text: formatEditValue(v));
    }
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(builder: (context, setDialogState) => AlertDialog(
          title: Text(title),
          content: SizedBox(
            width: 760,
            child: Form(
              key: formKey,
              child: SingleChildScrollView(
                child: Wrap(spacing: 14, runSpacing: 14, children: fields.map((f) {
                  final width = f.kind == FieldKind.multiline ? 728.0 : 354.0;
                  if (f.kind == FieldKind.dropdown) {
                    return SizedBox(
                      width: width,
                      child: DropdownButtonFormField<String>(
                        value: selected[f.key],
                        isExpanded: true,
                        decoration: InputDecoration(labelText: f.label),
                        items: f.options.map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                        validator: (_) => f.required && (selected[f.key] == null || selected[f.key]!.isEmpty) ? 'Required' : null,
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
                }).toList()),
              ),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            FilledButton(onPressed: () {
              if (!formKey.currentState!.validate()) return;
              final out = <String, dynamic>{};
              for (final f in fields) {
                if (f.kind == FieldKind.dropdown) {
                  out[f.key] = selected[f.key];
                } else {
                  final t = controllers[f.key]!.text.trim();
                  if (t.isEmpty) { out[f.key] = null; }
                  else if (f.kind == FieldKind.number) { out[f.key] = num.tryParse(t); }
                  else if (f.kind == FieldKind.integer) { out[f.key] = int.tryParse(t); }
                  else { out[f.key] = t; }
                }
              }
              Navigator.pop(context, out);
            }, child: const Text('Save')),
          ],
        )),
  );
  for (final c in controllers.values) { c.dispose(); }
  return result;
}

Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(2000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), r['full_name'].toString())).toList();
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), r['name'].toString())).toList();
}

Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showRecordDialog(context, row == null ? 'Add employee' : 'Edit employee', const [
    EditField('full_name', 'Full name', required: true),
    EditField('appointment', 'Appointment'),
    EditField('designation', 'Designation'),
    EditField('employee_type', 'Employee type', kind: FieldKind.dropdown, options: [EditOption('full_time', 'Full time'), EditOption('probationary', 'Probationary'), EditOption('part_time', 'Part time'), EditOption('staff', 'Staff'), EditOption('faculty_staff', 'Faculty / Staff')]),
    EditField('employment_status', 'Employment status', kind: FieldKind.dropdown, options: [EditOption('active', 'Active'), EditOption('inactive', 'Inactive'), EditOption('separated', 'Separated')]),
    EditField('current_salary', 'Current salary', kind: FieldKind.number),
    EditField('license_summary', 'License summary'),
  ], row);
  if (data == null) return;
  data['name_key'] = normalizeName(data['full_name']?.toString() ?? '');
  await saveRow(context, 'employees', row?['id'], data, refresh);
}

Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add contract' : 'Edit contract', [
    EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees),
    const EditField('contract_type', 'Contract type'),
    const EditField('contract_start_date', 'Start date', kind: FieldKind.date),
    const EditField('duration_months', 'Duration in months', kind: FieldKind.integer),
    const EditField('contract_end_date', 'End date', kind: FieldKind.date),
    const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
  ], row);
  if (data == null) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}

Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add license' : 'Edit license', [
    EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees),
    const EditField('license_name', 'License name', required: true),
    const EditField('license_number', 'License number'),
    const EditField('issued_date', 'Issued date', kind: FieldKind.date),
    const EditField('expiry_date', 'Expiry date', kind: FieldKind.date),
    const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
  ], row);
  if (data == null) return;
  await saveRow(context, 'employee_licenses', row?['id'], data, refresh);
}

Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add certificate' : 'Edit certificate', [
    EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees),
    const EditField('certificate_type', 'Certificate type'),
    const EditField('certificate_name', 'Certificate name', required: true),
    const EditField('certificate_number', 'Certificate number'),
    const EditField('issued_date', 'Issued date', kind: FieldKind.date),
    const EditField('expiry_date', 'Expiry date', kind: FieldKind.date),
    const EditField('status', 'Status', kind: FieldKind.dropdown, options: [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]),
  ], row);
  if (data == null) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row?['id'], data, refresh);
}

Future<void> editEvaluation(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final data = await showRecordDialog(context, row == null ? 'Add evaluation' : 'Edit evaluation', [
    EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees),
    const EditField('academic_year', 'Academic year', required: true),
    const EditField('semester', 'Semester', required: true),
    const EditField('superior_rating', 'Superior rating', kind: FieldKind.number),
    const EditField('peer_rating', 'Peer rating', kind: FieldKind.number),
    const EditField('self_rating', 'Self rating', kind: FieldKind.number),
    const EditField('student_rating', 'Student rating', kind: FieldKind.number),
    const EditField('total_rating', 'Total rating', kind: FieldKind.number),
    const EditField('total_description', 'Total description', kind: FieldKind.multiline, lines: 3),
  ], row);
  if (data == null) return;
  await saveRow(context, 'evaluation_records', row?['id'], data, refresh);
}

Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final employees = await employeeOptions();
  final cycles = await cycleOptions();
  final data = await showRecordDialog(context, row == null ? 'Add ranking record' : 'Edit ranking record', [
    EditField('employee_id', 'Employee', kind: FieldKind.dropdown, required: true, options: employees),
    EditField('cycle_id', 'Ranking cycle', kind: FieldKind.dropdown, required: true, options: cycles),
    const EditField('appointment', 'Appointment'),
    const EditField('previous_rank_text', 'Previous rank'),
    const EditField('previous_salary', 'Previous salary', kind: FieldKind.number),
    const EditField('applied_rank_text', 'Applied rank'),
    const EditField('applied_salary', 'Applied salary', kind: FieldKind.number),
    const EditField('points_earned', 'Points earned', kind: FieldKind.number),
    const EditField('approved_rank_text', 'Approved rank'),
    const EditField('approved_salary', 'Approved salary', kind: FieldKind.number),
  ], row);
  if (data == null) return;
  await saveRow(context, 'ranking_applications', row?['id'], data, refresh);
}

Future<void> saveRow(BuildContext context, String table, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from(table).insert(data);
      showSnack(context, 'Record added.');
    } else {
      await db.from(table).update(data).eq('id', id);
      showSnack(context, 'Record updated.');
    }
    refresh();
  } catch (e) {
    showSnack(context, 'Save failed: $e');
  }
}

void showSnack(BuildContext context, String message) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));

Object? valueFor(Map<String, dynamic> row, String key) {
  if (key == 'employee_name') return row['employees'] is Map ? row['employees']['full_name'] : null;
  if (key == 'cycle_name') return row['ranking_cycles'] is Map ? row['ranking_cycles']['name'] : null;
  return row[key];
}

String searchableText(Map<String, dynamic> row) {
  final values = <String>[];
  void walk(Object? v) {
    if (v == null) return;
    if (v is Map) {
      for (final x in v.values) { walk(x); }
    } else {
      values.add(v.toString().toLowerCase());
    }
  }
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
  return text.replaceAll('_', ' ');
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
