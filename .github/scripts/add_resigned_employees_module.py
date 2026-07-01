from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

loader = r'''
Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {
  final rows = await loadContracts(limit: limit);
  return rows.where((item) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final status = formatValue(row['status']).toLowerCase();
    return status.contains('resign');
  }).toList();
}

'''
if 'Future<List<dynamic>> loadResignedEmployees' not in text:
    marker = 'Future<List<dynamic>> loadLicenses({int limit = 1500})'
    if marker not in text:
        raise SystemExit('Loader insertion point not found.')
    text = text.replace(marker, loader + marker, 1)

page = r'''
class ResignedEmployeesPage extends StatelessWidget {
  const ResignedEmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Resigned Employees',
        subtitle: 'Employees with contract status marked as Resigned. Update contract status from the Contracts module or edit here.',
        child: CrudTable(
          load: () => loadResignedEmployees(),
          searchHint: 'Search resigned employee, contract type, date, or status',
          addLabel: 'Add Contract',
          allowAdd: false,
          reportTitle: 'Resigned Employees Report',
          columns: const [
            GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            GridCol('contract_type', 'Contract Type', flex: 2),
            GridCol('status', 'Status', isStatus: true),
            GridCol('contract_start_date', 'Start'),
            GridCol('duration_months', 'Months', isNumber: true),
            GridCol('contract_end_date', 'End'),
            GridCol('days_left', 'Days Left', isNumber: true),
          ],
          onEdit: editContract,
          onDelete: (row) => db.from('employee_contracts').delete().eq('id', row['id']),
        ),
      );
}

'''
if 'class ResignedEmployeesPage' not in text:
    marker = 'class CredentialsPage extends StatelessWidget {'
    if marker not in text:
        raise SystemExit('Page insertion point not found.')
    text = text.replace(marker, page + marker, 1)

# Add page at the end of ShellPage pages list without shifting existing indices.
if 'ResignedEmployeesPage()' not in text:
    shell_start = text.find('class _ShellPageState extends State<ShellPage>')
    nav_start = text.find('class NavItem', shell_start)
    if shell_start == -1 or nav_start == -1:
        raise SystemExit('ShellPage block not found.')
    block = text[shell_start:nav_start]
    last_list_end = block.rfind('    ];')
    if last_list_end == -1:
        raise SystemExit('Pages list end not found.')
    block = block[:last_list_end] + '      const ResignedEmployeesPage(),\n' + block[last_list_end:]
    text = text[:shell_start] + block + text[nav_start:]

# Add sidebar item at the end to match appended page index.
if "NavItem('Resigned Employees'" not in text:
    nav_items_start = text.find('    const items = [')
    nav_items_end = text.find('    ];', nav_items_start)
    if nav_items_start == -1 or nav_items_end == -1:
        raise SystemExit('Sidebar items list not found.')
    text = text[:nav_items_end] + "      NavItem('Resigned Employees', Icons.person_off_rounded),\n" + text[nav_items_end:]

# Ensure Contract status dropdown contains Resigned.
old_status = "EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')"
new_status = "EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived'), EditOption('Resigned', 'Resigned')"
if old_status in text and "EditOption('Resigned', 'Resigned')" not in text:
    text = text.replace(old_status, new_status, 1)

path.write_text(text, encoding='utf-8')
print('Resigned Employees module patch applied to lib/main.dart')
