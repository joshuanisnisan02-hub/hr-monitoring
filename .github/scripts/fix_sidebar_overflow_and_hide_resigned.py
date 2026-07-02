from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# ------------------------------------------------------------
# 1) Fix sidebar vertical overflow by replacing AppSidebar with
#    a compact layout where the menu is scrollable.
# ------------------------------------------------------------
start = text.find('class AppSidebar extends StatelessWidget')
end = text.find('class SidebarItem', start)
if start == -1 or end == -1:
    raise SystemExit('Could not locate AppSidebar block.')

new_sidebar = r'''class AppSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  const AppSidebar({super.key, required this.selectedIndex, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    const items = [
      NavItem('Dashboard', Icons.dashboard_rounded),
      NavItem('Employees', Icons.groups_rounded),
      NavItem('Contracts', Icons.assignment_rounded),
      NavItem('Credentials', Icons.badge_rounded),
      NavItem('Evaluations', Icons.rate_review_rounded),
      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Reports', Icons.summarize_rounded),
      NavItem('Resigned Employees', Icons.person_off_rounded),
    ];

    return Container(
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
      child: SafeArea(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]),
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [BoxShadow(color: Color(0x332563EB), blurRadius: 18, offset: Offset(0, 8))],
              ),
              child: const Icon(Icons.school_rounded, color: Colors.white),
            ),
            const SizedBox(width: 12),
            const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
          ]),
          const SizedBox(height: 6),
          const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 18),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: items.length,
              itemBuilder: (context, i) => SidebarItem(
                label: items[i].label,
                icon: items[i].icon,
                selected: selectedIndex == i,
                onTap: () => onChanged(i),
              ),
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: () => logoutUser(context),
              icon: const Icon(Icons.logout_rounded, size: 18),
              label: const Text('Logout'),
            ),
          ),
        ]),
      ),
    );
  }
}

'''
text = text[:start] + new_sidebar + text[end:]

# ------------------------------------------------------------
# 2) Make SidebarItem more compact if it has large vertical padding.
# ------------------------------------------------------------
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),', 'padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),', 'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),')
text = text.replace('const SizedBox(height: 12)', 'const SizedBox(height: 8)')

# ------------------------------------------------------------
# 3) Hide resigned employees from Employees module more robustly.
#    Some rows use employment_status, some use status/latest_status.
# ------------------------------------------------------------
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')

emp = text[emp_start:emp_end]

helper = r'''
  bool isResignedEmployeeRow(Map<String, dynamic> row) {
    final values = [
      row['employment_status'],
      row['employee_status'],
      row['status'],
      row['latest_status'],
      row['contract_status'],
    ];
    return values.any((value) => formatValue(value).toLowerCase().contains('resign'));
  }

'''
if 'bool isResignedEmployeeRow(Map<String, dynamic> row)' not in emp:
    # Insert inside EmployeesPage class before build() if possible.
    build_pos = emp.find('  @override\n  Widget build')
    if build_pos == -1:
        build_pos = emp.find('Widget build')
    if build_pos == -1:
        raise SystemExit('Could not find EmployeesPage build method.')
    emp = emp[:build_pos] + helper + emp[build_pos:]

# If matchesGenderFilter exists, make it reject resigned rows first.
if 'if (isResignedEmployeeRow(row)) return false;' not in emp:
    pos = emp.find('bool matchesGenderFilter(Map<String, dynamic> row)')
    if pos != -1:
        brace = emp.find('{', pos)
        if brace != -1:
            emp = emp[:brace + 1] + '\n    if (isResignedEmployeeRow(row)) return false;' + emp[brace + 1:]

# Also patch common list filtering chains.
if '.where(matchesGenderFilter).toList()' in emp and 'where((row) => !isResignedEmployeeRow(row)).where(matchesGenderFilter)' not in emp:
    emp = emp.replace('.where(matchesGenderFilter).toList()', '.where((row) => !isResignedEmployeeRow(row)).where(matchesGenderFilter).toList()', 1)

# Patch inline CrudTable load if possible by wrapping final loaded list.
# This handles cases where matchesGenderFilter is not the active filter path.
if 'Future<List<dynamic>> loadEmployeesForTable()' not in emp:
    # Avoid deeper invasive rewrites; the matchesGenderFilter/list-chain patches above are usually enough.
    pass

text = text[:emp_start] + emp + text[emp_end:]

path.write_text(text, encoding='utf-8')
print('Fixed sidebar overflow and strengthened Employees resigned filtering.')
