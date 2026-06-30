from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Add independent appointment loader.
if 'Future<List<dynamic>> loadAppointments' not in s:
    s = s.replace(
        """Future<List<dynamic>> loadRankings({int limit = 1500}) => db.from('ranking_applications').select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, approved_date, employees(full_name), ranking_cycles(name)').order('points_earned', ascending: false).limit(limit);""",
        """Future<List<dynamic>> loadRankings({int limit = 1500}) => db.from('ranking_applications').select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, approved_date, employees(full_name), ranking_cycles(name)').order('points_earned', ascending: false).limit(limit);
Future<List<dynamic>> loadAppointments({int limit = 5000}) => db.from('employee_appointments').select('id, employee_id, category, appointment_title, employees(full_name)').order('category').limit(limit);""",
        1,
    )

# Appointment module should load the independent reference table, not rankings.
s = s.replace(
    """          load: () => loadRankings(limit: 5000),
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
          onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),""",
    """          load: () => loadAppointments(),
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
          onDelete: (row) => db.from('employee_appointments').delete().eq('id', row['id']),""",
    1,
)

# Add appointment view/edit handlers before RankingPage.
if 'Future<void> viewAppointment(BuildContext context, Map<String, dynamic> row)' not in s:
    appointment_handlers = r'''
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

'''
    s = s.replace('class RankingPage extends StatefulWidget {', appointment_handlers + 'class RankingPage extends StatefulWidget {', 1)

# Ranking Add should pull appointment from employee_appointments reference table.
s = s.replace(
    """Future<Map<String, String>> rankingAppointmentByEmployee() async {
  final rows = await db.from('ranking_applications').select('employee_id, appointment').limit(5000);
  final out = <String, String>{};
  for (final r in rows) {
    final id = r['employee_id']?.toString();
    final appointment = formatEditValue(r['appointment']);
    if (id != null && id.isNotEmpty && appointment.isNotEmpty) out[id] = appointment;
  }
  return out;
}""",
    """Future<Map<String, String>> rankingAppointmentByEmployee() async {
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
}""",
    1,
)

p.write_text(s)
