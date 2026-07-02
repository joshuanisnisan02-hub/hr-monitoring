from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

old_load = """Future<List<dynamic>> loadContracts({int limit = 1500}) => db.from('employee_contracts').select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name)').order('contract_end_date', ascending: true).limit(limit);
"""
new_load = """Future<List<dynamic>> loadContracts({int limit = 1500}) async {
  final rows = await db.from('employee_contracts').select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name, employment_status)').order('contract_end_date', ascending: true).limit(limit);
  return rows.where((item) {
    final row = Map<String, dynamic>.from(item as Map);
    if ('${row['status'] ?? ''}'.toLowerCase().contains('resigned')) return false;
    final employee = row['employees'];
    if (employee is Map && '${employee['employment_status'] ?? ''}'.toLowerCase().contains('resigned')) return false;
    return true;
  }).toList();
}
"""
if old_load in s:
    s = s.replace(old_load, new_load, 1)
elif new_load not in s:
    raise SystemExit('loadContracts block not found')

marker = """Future<List<String>> licenseNameOptions() async {
"""
helper = """Future<List<EditOption>> activeEmployeeOptions() async {
  final rows = await db.from('employees').select('id, full_name, employment_status').order('full_name').limit(3000);
  final out = <EditOption>[];
  for (final r in rows) {
    final status = '${r['employment_status'] ?? ''}'.toLowerCase();
    if (status.contains('resigned')) continue;
    out.add(EditOption(r['id'].toString(), formatValue(r['full_name'])));
  }
  out.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return out;
}

"""
if 'Future<List<EditOption>> activeEmployeeOptions() async' not in s:
    if marker not in s:
        raise SystemExit('employee options insertion marker not found')
    s = s.replace(marker, helper + marker, 1)

old_contract_employees = """  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
"""
new_contract_employees = """  final employees = isAdd ? await activeEmployeeOptions() : const <EditOption>[];
"""
idx = s.find('Future<void> editContract')
if idx < 0:
    raise SystemExit('editContract not found')
next_part = s[idx:idx+500]
if old_contract_employees in next_part:
    s = s[:idx] + next_part.replace(old_contract_employees, new_contract_employees, 1) + s[idx+500:]
elif new_contract_employees not in next_part:
    raise SystemExit('editContract employee options line not found')

p.write_text(s)
