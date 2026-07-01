from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

start = text.find('class EmployeesPage extends StatefulWidget')
end = text.find('class ContractsPage', start)
if start == -1 or end == -1:
    raise SystemExit('Could not locate EmployeesPage to ContractsPage block.')

has_crud_initial_search = 'final String initialSearch;' in text
has_employee_initial_search = 'EmployeesPage({super.key, this.initialSearch}' in text or 'EmployeesPage({super.key, this.initialSearch});' in text

initial_search_class = "  final String? initialSearch;\n  const EmployeesPage({super.key, this.initialSearch});" if has_crud_initial_search else "  const EmployeesPage({super.key});"
initial_search_arg = "              initialSearch: widget.initialSearch ?? '',\n" if has_crud_initial_search else ""

new_block = f'''class EmployeesPage extends StatefulWidget {{
{initial_search_class}

  @override
  State<EmployeesPage> createState() => _EmployeesPageState();
}}

class _EmployeesPageState extends State<EmployeesPage> {{
  String genderFilter = 'All';

  bool matchesGenderFilter(Map<String, dynamic> row) {{
    if (genderFilter == 'All') return true;
    return summaryGenderLabel(row['gender']) == genderFilter;
  }}

  Future<List<dynamic>> loadFilteredEmployees() async {{
    final rows = await loadEmployees(limit: 5000);
    return rows.map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).where(matchesGenderFilter).toList();
  }}

  String employeeReportTitle() => genderFilter == 'All' ? 'Employee Master List' : 'Employee Master List - $genderFilter';

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle: 'Add full employee information, contract, credentials, and view complete records.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                const Text('Filter:', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 12),
                SizedBox(
                  width: 260,
                  child: DropdownButtonFormField<String>(
                    value: genderFilter,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Gender'),
                    items: const [
                      DropdownMenuItem(value: 'All', child: Text('All Genders')),
                      DropdownMenuItem(value: 'Male', child: Text('Male')),
                      DropdownMenuItem(value: 'Female', child: Text('Female')),
                    ],
                    onChanged: (value) => setState(() => genderFilter = value ?? 'All'),
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'The table and Print button will follow the selected gender filter.',
                    style: TextStyle(color: _muted, fontWeight: FontWeight.w600),
                  ),
                ),
              ]),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey('employees-$genderFilter'),
              load: () => loadFilteredEmployees(),
              searchHint: 'Search employee, bio number, gender, education, status, or date hired',
{initial_search_arg}              addLabel: 'Add Employee',
              reportTitle: employeeReportTitle(),
              columns: const [
                GridCol('full_name', 'Employee Name', flex: 3, primary: true),
                GridCol('bio_number', 'Bio Number'),
                GridCol('gender', 'Gender'),
                GridCol('education_level', 'Educational Attainment', flex: 2),
                GridCol('date_hired_display', 'Date Hired'),
                GridCol('employment_status', 'Status', isStatus: true),
              ],
              onAdd: (ctx, refresh) => editEmployee(ctx, null, refresh),
              onView: viewEmployee,
              onEdit: editEmployee,
              onDelete: (row) => db.from('employees').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}}

'''

text = text[:start] + new_block + text[end:]
path.write_text(text, encoding='utf-8')
print('EmployeesPage repaired and employee matching panel removed.')
