from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8')
start = text.find('class DashboardPage extends StatelessWidget {')
end = text.find('class EmployeesPage extends StatefulWidget {', start)
if start < 0 or end < 0:
    raise SystemExit('Could not find Dashboard block to replace.')

replacement = r'''
class DashboardData {
  final Map<String, dynamic> counts;
  final int totalFemale;
  final int totalMale;
  final int rankSummary;
  final int licenseSummary;
  final int certificateSummary;

  const DashboardData({
    required this.counts,
    required this.totalFemale,
    required this.totalMale,
    required this.rankSummary,
    required this.licenseSummary,
    required this.certificateSummary,
  });

  int get totalGender => totalFemale + totalMale;
}

Future<DashboardData> loadDashboardData() async {
  final countRows = await db.from('hr_dashboard_counts').select();
  final counts = countRows.isNotEmpty
      ? Map<String, dynamic>.from(countRows.first as Map)
      : <String, dynamic>{};

  final employees = await loadActiveEmployees(limit: 5000);
  var female = 0;
  var male = 0;
  for (final item in employees) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final gender = formatValue(row['gender']).trim().toLowerCase();
    if (gender == 'female' || gender == 'f') female++;
    if (gender == 'male' || gender == 'm') male++;
  }

  final rankings = await activeOnlyRows(loadRankings(limit: 5000));
  final licenses = await activeOnlyRows(loadLicenses(limit: 5000));
  final certificates = await activeOnlyRows(loadCertificates(limit: 5000));

  return DashboardData(
    counts: counts,
    totalFemale: female,
    totalMale: male,
    rankSummary: rankings.length,
    licenseSummary: licenses.length,
    certificateSummary: certificates.length,
  );
}

class DashboardPage extends StatelessWidget {
  final ValueChanged<int> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle:
            'At-a-glance summary of HR monitoring records. Click a card to open the related module/report.',
        child: FutureBuilder<DashboardData>(
          future: loadDashboardData(),
          builder: (_, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) return ErrorBox('${snap.error}');
            final data = snap.data ??
                const DashboardData(
                  counts: {},
                  totalFemale: 0,
                  totalMale: 0,
                  rankSummary: 0,
                  licenseSummary: 0,
                  certificateSummary: 0,
                );
            final row = data.counts;
            final moduleCards = [
              Metric(
                  'Active Employees',
                  row['active_employees'],
                  Icons.people_alt_rounded,
                  const Color(0xFFEFF6FF),
                  const Color(0xFF1D4ED8),
                  targetIndex: 1),
              Metric(
                  'Active Faculty',
                  row['active_faculty'],
                  Icons.school_rounded,
                  const Color(0xFFF0FDF4),
                  const Color(0xFF15803D),
                  targetIndex: 1),
              Metric(
                  'For Renewal',
                  row['contracts_for_renewal'],
                  Icons.schedule_rounded,
                  const Color(0xFFFFFBEB),
                  const Color(0xFFB45309),
                  targetIndex: 2),
              Metric(
                  'Expired Contracts',
                  row['expired_contracts'],
                  Icons.warning_amber_rounded,
                  const Color(0xFFFEF2F2),
                  const Color(0xFFB91C1C),
                  targetIndex: 2),
              Metric('Licenses Due', row['licenses_due'], Icons.badge_rounded,
                  const Color(0xFFF5F3FF), const Color(0xFF6D28D9),
                  targetIndex: 3),
              Metric(
                  'Certificates Due',
                  row['certificates_due'],
                  Icons.workspace_premium_rounded,
                  const Color(0xFFECFEFF),
                  const Color(0xFF0E7490),
                  targetIndex: 3),
              Metric('Ranking Records', row['ranking_applications'],
                  Icons.leaderboard_rounded, const Color(0xFFF8FAFC), _ink,
                  targetIndex: 6),
            ];
            final reportCards = [
              Metric('Total Female', data.totalFemale, Icons.female_rounded,
                  const Color(0xFFFDF2F8), const Color(0xFFDB2777),
                  targetIndex: 7),
              Metric('Total Male', data.totalMale, Icons.male_rounded,
                  const Color(0xFFEFF6FF), const Color(0xFF2563EB),
                  targetIndex: 7),
              Metric('Total Gender', data.totalGender, Icons.wc_rounded,
                  const Color(0xFFF8FAFC), _ink,
                  targetIndex: 7),
              Metric('Rank Summary', data.rankSummary, Icons.bar_chart_rounded,
                  const Color(0xFFF0FDF4), const Color(0xFF16A34A),
                  targetIndex: 7),
              Metric('License Summary', data.licenseSummary,
                  Icons.badge_rounded, const Color(0xFFFFF7ED),
                  const Color(0xFFC2410C),
                  targetIndex: 7),
              Metric('NC/TM Summary', data.certificateSummary,
                  Icons.workspace_premium_rounded, const Color(0xFFECFEFF),
                  const Color(0xFF0E7490),
                  targetIndex: 7),
            ];
            return SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Module Status',
                        style: TextStyle(
                            fontWeight: FontWeight.w900,
                            color: _ink,
                            fontSize: 16)),
                    const SizedBox(height: 14),
                    Wrap(
                        spacing: 24,
                        runSpacing: 24,
                        children: moduleCards
                            .map((m) => MetricCard(m, onNavigate: onNavigate))
                            .toList()),
                    const SizedBox(height: 30),
                    const Text('Report Totals',
                        style: TextStyle(
                            fontWeight: FontWeight.w900,
                            color: _ink,
                            fontSize: 16)),
                    const SizedBox(height: 14),
                    Wrap(
                        spacing: 24,
                        runSpacing: 24,
                        children: reportCards
                            .map((m) => MetricCard(m, onNavigate: onNavigate))
                            .toList()),
                    const SizedBox(height: 30),
                    Wrap(spacing: 20, runSpacing: 14, children: [
                      QuickCard('Manage Employees', Icons.people_alt_rounded,
                          () => onNavigate(1)),
                      QuickCard('Manage Contracts', Icons.assignment_rounded,
                          () => onNavigate(2)),
                      QuickCard('Manage Credentials', Icons.badge_rounded,
                          () => onNavigate(3)),
                      QuickCard('Open Reports', Icons.summarize_rounded,
                          () => onNavigate(7)),
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
  final int? targetIndex;
  const Metric(this.title, this.value, this.icon, this.bg, this.fg,
      {this.targetIndex});
}

class MetricCard extends StatelessWidget {
  final Metric metric;
  final ValueChanged<int>? onNavigate;
  const MetricCard(this.metric, {super.key, this.onNavigate});

  @override
  Widget build(BuildContext context) {
    final content = Padding(
      padding: const EdgeInsets.all(18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                  color: metric.bg, borderRadius: BorderRadius.circular(14)),
              child: Icon(metric.icon, color: metric.fg)),
          const Spacer(),
          Text('${metric.value ?? 0}',
              style: const TextStyle(
                  fontSize: 34,
                  fontWeight: FontWeight.w900,
                  color: _ink,
                  letterSpacing: -0.7)),
        ]),
        const Spacer(),
        Row(children: [
          Expanded(
              child: Text(metric.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w900, color: _ink))),
          if (metric.targetIndex != null)
            const Icon(Icons.chevron_right_rounded, color: Color(0xFF64748B)),
        ]),
      ]),
    );

    return SizedBox(
      width: 248,
      height: 128,
      child: Card(
        child: metric.targetIndex == null || onNavigate == null
            ? content
            : InkWell(
                borderRadius: BorderRadius.circular(22),
                onTap: () => onNavigate!(metric.targetIndex!),
                child: content,
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
  Widget build(BuildContext context) => SizedBox(
        width: 245,
        child: Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(22),
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(children: [
                Icon(icon, color: _primary),
                const SizedBox(width: 12),
                Expanded(
                    child: Text(title,
                        style: const TextStyle(
                            fontWeight: FontWeight.w900, color: _ink))),
                const Icon(Icons.chevron_right_rounded, color: _muted),
              ]),
            ),
          ),
        ),
      );
}

'''

text = text[:start] + replacement + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied live-system dashboard layout with Module Status and Report Totals.')
