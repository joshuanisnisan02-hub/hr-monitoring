from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')

emp = text[emp_start:emp_end]

# Restore live behavior: Employees table should show all employees, including resigned,
# but retain the Display Names page size selector.
method_start = emp.find('  Future<List<dynamic>> _loadEmployees() async {')
if method_start == -1:
    raise SystemExit('_loadEmployees method was not found.')
brace = emp.find('{', method_start)
depth = 0
method_end = -1
for i in range(brace, len(emp)):
    if emp[i] == '{':
        depth += 1
    elif emp[i] == '}':
        depth -= 1
        if depth == 0:
            method_end = i + 1
            break
if method_end == -1:
    raise SystemExit('Could not find _loadEmployees method end.')

new_load = r'''  Future<List<dynamic>> _loadEmployees() async {
    final rows = await loadEmployees();
    if (genderFilter == 'All') return rows;
    return rows
        .where((item) => _matchesGenderFilter(
            normalizeRow(Map<String, dynamic>.from(item as Map))))
        .toList();
  }'''
emp = emp[:method_start] + new_load + emp[method_end:]

# Ensure Employee Matching import card exists above the gender filter.
if 'Excel Employee Matching' not in emp:
    marker = '        child: Column(children: ['
    if marker not in emp:
        raise SystemExit('Employee Column marker was not found.')
    card = r'''        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                Expanded(
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [
                    Text('Excel Employee Matching', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                    SizedBox(height: 4),
                    Text('Import tbl_employee CSV to fill missing profile fields for existing employees only. No new records are added.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600)),
                  ]),
                ),
                FilledButton.icon(
                  onPressed: () async {
                    await importEmployeeCsvInfo(context);
                    if (mounted) refreshEmployees();
                  },
                  icon: const Icon(Icons.upload_file_rounded),
                  label: const Text('Import Employee Info'),
                ),
              ]),
            ),
          ),
          const SizedBox(height: 14),'''
    emp = emp.replace(marker, card, 1)

# Retain the Display Names dropdown by making sure CrudTable has 1/10/100 options.
if 'pageSizeOptions: const [1, 10, 100]' not in emp:
    crud_pos = emp.find('CrudTable(')
    if crud_pos == -1:
        raise SystemExit('Employees CrudTable call was not found.')
    insert_at = crud_pos + len('CrudTable(')
    emp = emp[:insert_at] + '\n              pageSizeOptions: const [1, 10, 100],\n              initialPageSize: 10,' + emp[insert_at:]

text = text[:emp_start] + emp + text[emp_end:]
path.write_text(text, encoding='utf-8')
print('Restored live Employees view locally while keeping Display Names 1/10/100.')
