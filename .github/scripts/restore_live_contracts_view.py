from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

old_load = """Future<List<dynamic>> loadContracts({int limit = 1500}) async {
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
new_load = """Future<List<dynamic>> loadContracts({int limit = 1500}) => db.from('employee_contracts').select('id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name)').order('contract_end_date', ascending: true).limit(limit);
"""
if old_load in s:
    s = s.replace(old_load, new_load, 1)
elif new_load not in s:
    raise SystemExit('loadContracts block not found or already different')

old_emp = """  final employees = isAdd ? await activeEmployeeOptions() : const <EditOption>[];
"""
new_emp = """  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
"""
idx = s.find('Future<void> editContract')
if idx < 0:
    raise SystemExit('editContract not found')
section = s[idx:idx + 900]
if old_emp in section:
    s = s[:idx] + section.replace(old_emp, new_emp, 1) + s[idx + 900:]
elif new_emp not in section:
    raise SystemExit('editContract employee options line not found')

p.write_text(s)
