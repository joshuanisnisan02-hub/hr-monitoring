import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment('SUPABASE_URL', defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co');
const publicClientKey = String.fromEnvironment('SUPABASE_PUBLIC_CLIENT_KEY');

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
        theme: ThemeData(useMaterial3: true, colorSchemeSeed: const Color(0xFF2563EB)),
        home: publicClientKey.isEmpty ? const SetupPage() : const ShellPage(),
      );
}

class SetupPage extends StatelessWidget {
  const SetupPage({super.key});
  @override
  Widget build(BuildContext context) => const Scaffold(
        body: Center(
          child: SizedBox(
            width: 680,
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
  static const labels = ['Dashboard', 'Employees', 'Contracts', 'Credentials', 'Evaluations', 'Ranking'];
  @override
  Widget build(BuildContext context) {
    final pages = [
      const DashboardPage(),
      EmployeesPage(onSaved: () => setState(() {})),
      const QueryPage(title: 'Contract Monitoring', subtitle: 'CONTRACT sheet flow: start date, duration, end date, days left, status.', table: 'hr_contract_monitoring', columns: ['full_name', 'contract_type', 'contract_start_date', 'duration_months', 'contract_end_date', 'days_to_contract_end', 'computed_status']),
      const CredentialsPage(),
      const QueryPage(title: 'Evaluation Records', subtitle: 'Superior, peer, self, student, and total rating records.', table: 'hr_evaluation_summary', columns: ['full_name', 'academic_year', 'semester', 'superior_rating', 'peer_rating', 'self_rating', 'student_rating', 'total_rating', 'total_description']),
      const QueryPage(title: 'Faculty Ranking Summary', subtitle: 'FULL TIME, PROBATIONARY, and SUMMARY ranking columns.', table: 'hr_faculty_ranking_summary', columns: ['full_name', 'appointment', 'previous_rank', 'previous_salary', 'rank_applied_for', 'applied_salary', 'points_earned', 'approved_rank', 'approved_salary']),
    ];
    return Scaffold(
      body: Row(children: [
        NavigationRail(
          selectedIndex: index,
          onDestinationSelected: (v) => setState(() => index = v),
          labelType: NavigationRailLabelType.all,
          destinations: const [
            NavigationRailDestination(icon: Icon(Icons.dashboard_outlined), label: Text('Dashboard')),
            NavigationRailDestination(icon: Icon(Icons.people_alt_outlined), label: Text('Employees')),
            NavigationRailDestination(icon: Icon(Icons.assignment_outlined), label: Text('Contracts')),
            NavigationRailDestination(icon: Icon(Icons.badge_outlined), label: Text('Credentials')),
            NavigationRailDestination(icon: Icon(Icons.rate_review_outlined), label: Text('Evaluations')),
            NavigationRailDestination(icon: Icon(Icons.leaderboard_outlined), label: Text('Ranking')),
          ],
        ),
        const VerticalDivider(width: 1),
        Expanded(child: pages[index]),
      ]),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});
  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle: 'Summary from faculty list, contract monitoring, credentials, evaluation, and ranking sheets.',
        child: FutureBuilder<List<dynamic>>(
          future: Supabase.instance.client.from('hr_dashboard_counts').select(),
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snap.hasError) return ErrorBox('${snap.error}');
            final row = snap.data?.isNotEmpty == true ? snap.data!.first as Map<String, dynamic> : <String, dynamic>{};
            return Wrap(spacing: 16, runSpacing: 16, children: row.entries.map((e) => MetricCard(e.key.replaceAll('_', ' '), e.value)).toList());
          },
        ),
      );
}

class EmployeesPage extends StatelessWidget {
  final VoidCallback onSaved;
  const EmployeesPage({super.key, required this.onSaved});
  Future<List<dynamic>> load() => Supabase.instance.client.from('employees').select('full_name, appointment, designation, employee_type, employment_status, current_salary').order('full_name');
  Future<void> add(BuildContext context) async {
    final name = TextEditingController();
    final appointment = TextEditingController();
    final salary = TextEditingController();
    final ok = await showDialog<bool>(context: context, builder: (_) => AlertDialog(
      title: const Text('Add employee/faculty'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: name, decoration: const InputDecoration(labelText: 'Full name')),
        const SizedBox(height: 10),
        TextField(controller: appointment, decoration: const InputDecoration(labelText: 'Appointment')),
        const SizedBox(height: 10),
        TextField(controller: salary, decoration: const InputDecoration(labelText: 'Current salary')),
      ]),
      actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Save'))],
    ));
    if (ok == true && name.text.trim().isNotEmpty) {
      await Supabase.instance.client.from('employees').insert({'full_name': name.text.trim(), 'appointment': appointment.text.trim(), 'current_salary': num.tryParse(salary.text.trim()), 'source_workbook': 'Manual Entry'});
      onSaved();
    }
  }
  @override
  Widget build(BuildContext context) => PageFrame(
    title: 'Faculty and Staff Master List',
    subtitle: 'One employee record connects contracts, licenses, evaluations, and faculty ranking.',
    action: FilledButton.icon(onPressed: () => add(context), icon: const Icon(Icons.add), label: const Text('Add employee')),
    child: DataQuery(future: load(), columns: const ['full_name', 'appointment', 'designation', 'employee_type', 'employment_status', 'current_salary']),
  );
}

class CredentialsPage extends StatelessWidget {
  const CredentialsPage({super.key});
  @override
  Widget build(BuildContext context) => PageFrame(
    title: 'Licenses and National Certificates',
    subtitle: 'LICENSE, LICENSE SUMMARY, and NATIONAL CERT monitoring.',
    child: ListView(children: const [
      Text('Licenses', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
      SizedBox(height: 12),
      DataQueryView(table: 'employee_licenses', columns: ['license_name', 'license_number', 'issued_date', 'expiry_date', 'status']),
      SizedBox(height: 24),
      Text('National Certificates', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
      SizedBox(height: 12),
      DataQueryView(table: 'employee_certificates', columns: ['certificate_type', 'certificate_name', 'certificate_number', 'expiry_date', 'status']),
    ]),
  );
}

class QueryPage extends StatelessWidget {
  final String title, subtitle, table;
  final List<String> columns;
  const QueryPage({super.key, required this.title, required this.subtitle, required this.table, required this.columns});
  @override
  Widget build(BuildContext context) => PageFrame(title: title, subtitle: subtitle, child: DataQueryView(table: table, columns: columns));
}

class DataQueryView extends StatelessWidget {
  final String table;
  final List<String> columns;
  const DataQueryView({super.key, required this.table, required this.columns});
  Future<List<dynamic>> load() => Supabase.instance.client.from(table).select(columns.join(', '));
  @override
  Widget build(BuildContext context) => DataQuery(future: load(), columns: columns);
}

class DataQuery extends StatelessWidget {
  final Future<List<dynamic>> future;
  final List<String> columns;
  const DataQuery({super.key, required this.future, required this.columns});
  @override
  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(
    future: future,
    builder: (context, snap) {
      if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
      if (snap.hasError) return ErrorBox('${snap.error}');
      final rows = snap.data?.cast<Map<String, dynamic>>() ?? [];
      if (rows.isEmpty) return const Card(child: Center(child: Padding(padding: EdgeInsets.all(32), child: Text('No records yet. Encode or import Excel rows to start monitoring.'))));
      return Card(child: SingleChildScrollView(child: SingleChildScrollView(scrollDirection: Axis.horizontal, child: DataTable(
        columns: columns.map((c) => DataColumn(label: Text(c.replaceAll('_', ' ').toUpperCase(), style: const TextStyle(fontWeight: FontWeight.w800)))).toList(),
        rows: rows.map((r) => DataRow(cells: columns.map((c) => DataCell(Text(formatValue(r[c])))).toList())).toList(),
      ))));
    },
  );
}

class PageFrame extends StatelessWidget {
  final String title, subtitle;
  final Widget child;
  final Widget? action;
  const PageFrame({super.key, required this.title, required this.subtitle, required this.child, this.action});
  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.all(28), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Row(children: [Expanded(child: Text(title, style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w900))), if (action != null) action!]),
    const SizedBox(height: 6),
    Text(subtitle),
    const SizedBox(height: 22),
    Expanded(child: child),
  ]));
}

class MetricCard extends StatelessWidget {
  final String title;
  final Object? value;
  const MetricCard(this.title, this.value, {super.key});
  @override
  Widget build(BuildContext context) => SizedBox(width: 250, height: 120, child: Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title), const Spacer(), Text('${value ?? 0}', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900))]))));
}

class ErrorBox extends StatelessWidget {
  final String message;
  const ErrorBox(this.message, {super.key});
  @override
  Widget build(BuildContext context) => Card(color: const Color(0xFFFFE4E6), child: Padding(padding: const EdgeInsets.all(18), child: Text(message)));
}

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  final date = DateTime.tryParse(text);
  if (date != null && text.contains('-')) return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  return text;
}
