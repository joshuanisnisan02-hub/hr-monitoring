from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old_state_header = """class _EmployeesPageState extends State<EmployeesPage> {
  int refreshToken = 0;

  void refreshEmployees() => setState(() => refreshToken++);

  @override
"""
new_state_header = """class _EmployeesPageState extends State<EmployeesPage> {
  int refreshToken = 0;
  String genderFilter = 'All';

  void refreshEmployees() => setState(() => refreshToken++);

  String _genderKey(Object? value) {
    final gender = '${value ?? ''}'.trim().toLowerCase();
    if (gender == 'male' || gender == 'm') return 'Male';
    if (gender == 'female' || gender == 'f') return 'Female';
    return 'Unspecified';
  }

  bool _matchesGenderFilter(Map<String, dynamic> row) => genderFilter == 'All' || _genderKey(row['gender']) == genderFilter;

  Future<List<dynamic>> _loadEmployees() async {
    final rows = await loadEmployees();
    if (genderFilter == 'All') return rows;
    return rows.where((item) => _matchesGenderFilter(normalizeRow(Map<String, dynamic>.from(item as Map)))).toList();
  }

  String _employeeReportTitle() => genderFilter == 'All' ? 'Employee Report' : 'Employee Report - $genderFilter';

  @override
"""

if old_state_header in text:
    text = text.replace(old_state_header, new_state_header, 1)
elif "String genderFilter = 'All';" in text:
    print('Employee gender filter state is already present.')
else:
    raise SystemExit('EmployeesPage state header was not found.')

old_between_cards = """          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey('employees-$refreshToken'),
              load: () => loadEmployees(),
"""
new_between_cards = """          const SizedBox(height: 14),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                const Text('Filter:', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 10),
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
                      DropdownMenuItem(value: 'Unspecified', child: Text('Unspecified / Other')),
                    ],
                    onChanged: (value) => setState(() => genderFilter = value ?? 'All'),
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text('The table and Print button will follow the selected gender filter.', style: TextStyle(color: _muted, fontWeight: FontWeight.w600)),
                ),
              ]),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey('employees-$refreshToken-$genderFilter'),
              load: () => _loadEmployees(),
"""

if old_between_cards in text:
    text = text.replace(old_between_cards, new_between_cards, 1)
elif "labelText: 'Gender'" in text and "employees-$refreshToken-$genderFilter" in text:
    print('Employee gender filter UI is already present.')
else:
    raise SystemExit('Employees CrudTable block was not found.')

old_report_anchor = """              addLabel: 'Add Employee',
              columns: const [
"""
new_report_anchor = """              addLabel: 'Add Employee',
              reportTitle: _employeeReportTitle(),
              columns: const [
"""
if old_report_anchor in text and "reportTitle: _employeeReportTitle()," not in text:
    text = text.replace(old_report_anchor, new_report_anchor, 1)

path.write_text(text, encoding='utf-8')
print('Employee gender filter patch applied to lib/main.dart')
