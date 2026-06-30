from pathlib import Path
import textwrap

p = Path('lib/main.dart')
s = p.read_text()

# Add Appointment page to app page list and sidebar.
s = s.replace("""      const EvaluationsPage(),
      const RankingPage(),""", """      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),""", 1)
s = s.replace("""      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),""", """      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),""", 1)

# Remove Appointment column from Ranking table and adjust search hint.
s = s.replace("Search employee, appointment, rank, salary, or points", "Search employee, rank, salary, or points", 1)
s = s.replace("                GridCol('appointment', 'Appointment', flex: 2),\n", "", 1)

# Add a standalone Appointment module before RankingPage.
if 'class AppointmentPage extends StatelessWidget' not in s:
    appointment_page = textwrap.dedent(r'''

    class AppointmentPage extends StatelessWidget {
      const AppointmentPage({super.key});

      @override
      Widget build(BuildContext context) => PageFrame(
            title: 'Appointment',
            subtitle: 'View employee appointment classifications and assigned appointment/designation from the ranking Excel list.',
            child: CrudTable(
              load: () => loadRankings(limit: 5000),
              searchHint: 'Search employee or appointment',
              addLabel: 'Add Appointment',
              allowAdd: false,
              reportTitle: 'Appointment Report',
              columns: const [
                GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
                GridCol('appointment_category', 'Type', flex: 2),
                GridCol('appointment_title', 'Appointment', flex: 4),
              ],
              onView: viewRanking,
              onEdit: editRanking,
              onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
            ),
          );
    }
    ''').rstrip()
    marker = '\nclass RankingPage extends StatefulWidget'
    if marker not in s:
        raise SystemExit('RankingPage marker not found')
    s = s.replace(marker, appointment_page + '\n' + marker, 1)

# Normalize row must expose appointment category and title.
old_normalize = """  if (out['ranking_cycles'] is Map) out['cycle_name'] = out['ranking_cycles']['name'];
  if (out['date_hired'] == null || out['date_hired'].toString().isEmpty) out['date_hired'] = out['starting_date'];"""
new_normalize = """  if (out['ranking_cycles'] is Map) out['cycle_name'] = out['ranking_cycles']['name'];
  if (out.containsKey('appointment')) {
    final appointmentText = '${out['appointment'] ?? ''}'.trim();
    final parts = appointmentText.split(RegExp(r'\\s+-\\s+'));
    if (parts.length >= 2 && (parts.first.toLowerCase().contains('full') || parts.first.toLowerCase().contains('probationary'))) {
      out['appointment_category'] = parts.first;
      out['appointment_title'] = parts.skip(1).join(' - ');
    } else {
      out['appointment_category'] = '-';
      out['appointment_title'] = appointmentText.isEmpty ? '-' : appointmentText;
    }
  }
  if (out['date_hired'] == null || out['date_hired'].toString().isEmpty) out['date_hired'] = out['starting_date'];"""
if old_normalize in s and "appointment_category" not in s[s.find('Map<String, dynamic> normalizeRow'):s.find('Object? valueFor')]:
    s = s.replace(old_normalize, new_normalize, 1)

p.write_text(s)
