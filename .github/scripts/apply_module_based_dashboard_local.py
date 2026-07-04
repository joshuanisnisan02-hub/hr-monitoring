from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

start = text.find('class DashboardData {')
end = text.find('class Metric {', start)
if start < 0 or end < 0:
    raise SystemExit('Could not find DashboardData/DashboardPage block to replace.')

new_block = r'''class DashboardData {
  final int activeEmployees;
  final int activeFaculty;
  final int resignedEmployees;
  final int totalFemale;
  final int totalMale;
  final int contractsTotal;
  final int contractsOngoing;
  final int contractsForRenewal;
  final int expiredContracts;
  final int licensesTotal;
  final int licensesDue;
  final int certificatesTotal;
  final int certificatesDue;
  final int evaluationsTotal;
  final int appointmentsTotal;
  final int rankingsTotal;

  const DashboardData({
    required this.activeEmployees,
    required this.activeFaculty,
    required this.resignedEmployees,
    required this.totalFemale,
    required this.totalMale,
    required this.contractsTotal,
    required this.contractsOngoing,
    required this.contractsForRenewal,
    required this.expiredContracts,
    required this.licensesTotal,
    required this.licensesDue,
    required this.certificatesTotal,
    required this.certificatesDue,
    required this.evaluationsTotal,
    required this.appointmentsTotal,
    required this.rankingsTotal,
  });

  int get totalGender => totalFemale + totalMale;
  int get credentialsTotal => licensesTotal + certificatesTotal;
}

Map<String, dynamic> dashboardRow(dynamic item) =>
    normalizeRow(Map<String, dynamic>.from(item as Map));

String dashboardStatus(dynamic item) =>
    formatValue(dashboardRow(item)['status']).trim().toLowerCase();

bool dashboardStatusContains(dynamic item, List<String> terms) {
  final status = dashboardStatus(item);
  return terms.any(status.contains);
}

Future<DashboardData> loadDashboardData() async {
  final results = await Future.wait<List<dynamic>>([
    loadActiveEmployees(limit: 5000),
    loadResignedEmployees(limit: 5000),
    activeOnlyRows(loadContracts(limit: 5000)),
    activeOnlyRows(loadLicenses(limit: 5000)),
    activeOnlyRows(loadCertificates(limit: 5000)),
    activeOnlyRows(loadEvaluations(limit: 5000)),
    activeOnlyRows(loadAppointments(limit: 5000)),
    activeOnlyRows(loadRankings(limit: 5000)),
  ]);

  final employees = results[0];
  final resignedEmployees = results[1];
  final contracts = results[2];
  final licenses = results[3];
  final certificates = results[4];
  final evaluations = results[5];
  final appointments = results[6];
  final rankings = results[7];

  var female = 0;
  var male = 0;
  var faculty = 0;

  for (final item in employees) {
    final row = dashboardRow(item);
    final gender = formatValue(row['gender']).trim().toLowerCase();
    if (gender == 'female' || gender == 'f') female++;
    if (gender == 'male' || gender == 'm') male++;

    final roleText = [
      row['designation'],
      row['employee_type'],
      row['teaching_status'],
      row['education_level'],
    ].map(formatValue).join(' ').toLowerCase();
    if (roleText.contains('faculty') ||
        roleText.contains('teacher') ||
        roleText.contains('teaching')) {
      faculty++;
    }
  }

  final contractsForRenewal = contracts
      .where((item) => dashboardStatusContains(item, ['renew']))
      .length;
  final expiredContracts = contracts
      .where((item) => dashboardStatusContains(item, ['expired']))
      .length;
  final contractsOngoing = contracts
      .where((item) =>
          dashboardStatusContains(item, ['ongoing', 'on-going', 'active']))
      .length;
  final licensesDue = licenses
      .where((item) => dashboardStatusContains(item, ['renew', 'expired']))
      .length;
  final certificatesDue = certificates
      .where((item) => dashboardStatusContains(item, ['renew', 'expired']))
      .length;

  return DashboardData(
    activeEmployees: employees.length,
    activeFaculty: faculty,
    resignedEmployees: resignedEmployees.length,
    totalFemale: female,
    totalMale: male,
    contractsTotal: contracts.length,
    contractsOngoing: contractsOngoing,
    contractsForRenewal: contractsForRenewal,
    expiredContracts: expiredContracts,
    licensesTotal: licenses.length,
    licensesDue: licensesDue,
    certificatesTotal: certificates.length,
    certificatesDue: certificatesDue,
    evaluationsTotal: evaluations.length,
    appointmentsTotal: appointments.length,
    rankingsTotal: rankings.length,
  );
}

class DashboardPage extends StatelessWidget {
  final ValueChanged<int> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle:
            'Live summary based on the current data shown in each module. Click a card to open its module.',
        child: FutureBuilder<DashboardData>(
          future: loadDashboardData(),
          builder: (_, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) return ErrorBox('${snap.error}');
            final data = snap.data ??
                const DashboardData(
                  activeEmployees: 0,
                  activeFaculty: 0,
                  resignedEmployees: 0,
                  totalFemale: 0,
                  totalMale: 0,
                  contractsTotal: 0,
                  contractsOngoing: 0,
                  contractsForRenewal: 0,
                  expiredContracts: 0,
                  licensesTotal: 0,
                  licensesDue: 0,
                  certificatesTotal: 0,
                  certificatesDue: 0,
                  evaluationsTotal: 0,
                  appointmentsTotal: 0,
                  rankingsTotal: 0,
                );

            final moduleCards = <Metric>[
              Metric('Employees', data.activeEmployees, Icons.people_alt_rounded,
                  const Color(0xFFEFF6FF), const Color(0xFF1D4ED8),
                  targetIndex: 1),
              Metric('Contracts', data.contractsTotal,
                  Icons.assignment_rounded, const Color(0xFFFFFBEB),
                  const Color(0xFFB45309), targetIndex: 2),
              Metric('Credentials', data.credentialsTotal, Icons.badge_rounded,
                  const Color(0xFFF5F3FF), const Color(0xFF6D28D9),
                  targetIndex: 3),
              Metric('Evaluations', data.evaluationsTotal,
                  Icons.rate_review_rounded, const Color(0xFFECFEFF),
                  const Color(0xFF0E7490), targetIndex: 4),
              Metric('Appointments', data.appointmentsTotal,
                  Icons.work_outline_rounded, const Color(0xFFF0FDF4),
                  const Color(0xFF15803D), targetIndex: 5),
              Metric('Ranking', data.rankingsTotal,
                  Icons.leaderboard_rounded, const Color(0xFFF8FAFC), _ink,
                  targetIndex: 6),
              Metric('Reports', data.totalGender, Icons.summarize_rounded,
                  const Color(0xFFFFF7ED), const Color(0xFFC2410C),
                  targetIndex: 7),
              Metric('Resigned Employees', data.resignedEmployees,
                  Icons.person_off_rounded, const Color(0xFFFEF2F2),
                  const Color(0xFFB91C1C), targetIndex: 8),
            ];

            final attentionCards = <Metric>[
              Metric('Ongoing Contracts', data.contractsOngoing,
                  Icons.verified_rounded, const Color(0xFFF0FDF4),
                  const Color(0xFF15803D), targetIndex: 2),
              Metric('For Renewal', data.contractsForRenewal,
                  Icons.schedule_rounded, const Color(0xFFFFFBEB),
                  const Color(0xFFB45309), targetIndex: 2),
              Metric('Expired Contracts', data.expiredContracts,
                  Icons.warning_amber_rounded, const Color(0xFFFEF2F2),
                  const Color(0xFFB91C1C), targetIndex: 2),
              Metric('Licenses Due', data.licensesDue, Icons.badge_rounded,
                  const Color(0xFFF5F3FF), const Color(0xFF6D28D9),
                  targetIndex: 3),
              Metric('Certificates Due', data.certificatesDue,
                  Icons.workspace_premium_rounded, const Color(0xFFECFEFF),
                  const Color(0xFF0E7490), targetIndex: 3),
            ];

            final reportCards = <Metric>[
              Metric('Total Female', data.totalFemale, Icons.female_rounded,
                  const Color(0xFFFDF2F8), const Color(0xFFDB2777),
                  targetIndex: 7),
              Metric('Total Male', data.totalMale, Icons.male_rounded,
                  const Color(0xFFEFF6FF), const Color(0xFF2563EB),
                  targetIndex: 7),
              Metric('Total Gender', data.totalGender, Icons.wc_rounded,
                  const Color(0xFFF8FAFC), _ink,
                  targetIndex: 7),
              Metric('Active Faculty', data.activeFaculty, Icons.school_rounded,
                  const Color(0xFFF0FDF4), const Color(0xFF15803D),
                  targetIndex: 1),
              Metric('License Summary', data.licensesTotal,
                  Icons.badge_rounded, const Color(0xFFFFF7ED),
                  const Color(0xFFC2410C), targetIndex: 7),
              Metric('NC/TM Summary', data.certificatesTotal,
                  Icons.workspace_premium_rounded, const Color(0xFFECFEFF),
                  const Color(0xFF0E7490), targetIndex: 7),
            ];

            return RefreshIndicator(
              onRefresh: () async {
                _crudTableDataCache.clear();
                await loadDashboardData();
              },
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Per Module Data',
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
                      const Text('Needs Attention',
                          style: TextStyle(
                              fontWeight: FontWeight.w900,
                              color: _ink,
                              fontSize: 16)),
                      const SizedBox(height: 14),
                      Wrap(
                          spacing: 24,
                          runSpacing: 24,
                          children: attentionCards
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
              ),
            );
          },
        ),
      );
}

'''

text = text[:start] + new_block + text[end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Module-based dashboard may already be applied.')
else:
    print('Applied module-based dashboard counts and card layout.')
