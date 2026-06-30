from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Add helper that maps employee_id to the current appointment from ranking records.
if 'Future<Map<String, String>> rankingAppointmentByEmployee() async' not in s:
    s = s.replace(
        """Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['name']))).toList();
}
""",
        """Future<Map<String, String>> rankingAppointmentByEmployee() async {
  final rows = await db.from('ranking_applications').select('employee_id, appointment').limit(5000);
  final out = <String, String>{};
  for (final r in rows) {
    final id = r['employee_id']?.toString();
    final appointment = formatEditValue(r['appointment']);
    if (id != null && id.isNotEmpty && appointment.isNotEmpty) out[id] = appointment;
  }
  return out;
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['name']))).toList();
}
""",
        1,
    )

# Load the appointment map only for Add Ranking and pass it into the dialog.
s = s.replace(
    """Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showRankingDialog(context, isAdd ? await employeeOptions() : const <EditOption>[], await cycleOptions(), await rankOptions(), row);""",
    """Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showRankingDialog(context, isAdd ? await employeeOptions() : const <EditOption>[], await cycleOptions(), await rankOptions(), row, isAdd ? await rankingAppointmentByEmployee() : const <String, String>{});""",
    1,
)

# Update dialog signature and default employee selection.
s = s.replace(
    """Future<Map<String, dynamic>?> showRankingDialog(BuildContext context, List<EditOption> employees, List<EditOption> cycles, List<EditOption> ranks, Map<String, dynamic>? initial) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? optionValueOrFirst(null, employees, true) : initial?['employee_id']?.toString();""",
    """Future<Map<String, dynamic>?> showRankingDialog(BuildContext context, List<EditOption> employees, List<EditOption> cycles, List<EditOption> ranks, Map<String, dynamic>? initial, Map<String, String> appointmentByEmployee) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();""",
    1,
)

# Make the employee dropdown show Select Employee by default, and auto-fill appointment on selection.
s = s.replace(
    """                    child: DropdownButtonFormField<String>(
                      value: optionValueOrFirst(employeeId, employees, true),
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Employee Name'),
                      items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                      onChanged: (v) => setDialogState(() => employeeId = v),
                    ),""",
    """                    child: DropdownButtonFormField<String>(
                      value: employeeId,
                      isExpanded: true,
                      hint: const Text('Select Employee'),
                      decoration: const InputDecoration(labelText: 'Employee Name'),
                      items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                      validator: (v) => v == null || v.isEmpty ? 'Please select employee' : null,
                      onChanged: (v) => setDialogState(() {
                        employeeId = v;
                        appointment.text = v == null ? '' : (appointmentByEmployee[v] ?? '');
                      }),
                    ),""",
    1,
)

# Update helper note.
s = s.replace(
    """Text(isAdd ? 'Select an employee for the new ranking record. Duplicate employees are not allowed.' : 'Employee name is locked here. Type ranks manually or use Pick to auto-fill salary.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600))""",
    """Text(isAdd ? 'Select Employee first. The Appointment field will be filled automatically when an existing appointment is found for the selected employee.' : 'Employee name is locked here. Type ranks manually or use Pick to auto-fill salary.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600))""",
    1,
)

p.write_text(s)
