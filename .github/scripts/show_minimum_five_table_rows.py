from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# The goal is to make the visible table body show at least about 5 rows
# on normal desktop browser height while keeping Display Names 1/10/100.

# 1) Compact the global page frame so more vertical space goes to tables.
text = text.replace(
    'padding: const EdgeInsets.fromLTRB(28, 24, 28, 28),',
    'padding: const EdgeInsets.fromLTRB(28, 18, 28, 18),'
)
text = text.replace('const SizedBox(height: 22),\n          Expanded(child: child),', 'const SizedBox(height: 14),\n          Expanded(child: child),')
text = text.replace('const SizedBox(height: 8),\n          Text(subtitle,', 'const SizedBox(height: 5),\n          Text(subtitle,')

# 2) Compact the Employees filter cards and spacing.
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')
emp = text[emp_start:emp_end]
emp = emp.replace('padding: const EdgeInsets.all(12),', 'padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),')
emp = emp.replace('          const SizedBox(height: 14),', '          const SizedBox(height: 8),')
emp = emp.replace('          const SizedBox(height: 10),', '          const SizedBox(height: 8),')
text = text[:emp_start] + emp + text[emp_end:]

# 3) Compact table toolbar/card/dropdown spacing.
replacements = {
    'padding: const EdgeInsets.all(12),': 'padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),',
    'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),': 'padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),',
    'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),': 'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),',
    'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),': 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),',
    'constraints: const BoxConstraints(minHeight: 46),': 'constraints: const BoxConstraints(minHeight: 42),',
    'constraints: const BoxConstraints(minHeight: 50),': 'constraints: const BoxConstraints(minHeight: 42),',
    'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),': 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 7),',
    'const SizedBox(height: 14),\n            Expanded(child:': 'const SizedBox(height: 6),\n            Expanded(child:',
    'const SizedBox(height: 8),\n            Expanded(child:': 'const SizedBox(height: 6),\n            Expanded(child:',
    'const SizedBox(height: 14),\n            PaginationFooter(': 'const SizedBox(height: 6),\n            PaginationFooter(',
    'const SizedBox(height: 8),\n            PaginationFooter(': 'const SizedBox(height: 6),\n            PaginationFooter(',
    'const SizedBox(height: 10),\n              Align(': 'const SizedBox(height: 4),\n              Align:',
    'const SizedBox(height: 6),\n              Align(': 'const SizedBox(height: 4),\n              Align:',
}
for old, new in replacements.items():
    text = text.replace(old, new)

# 4) Make the Display Names dropdown shorter while preserving the same choices.
text = text.replace('width: 220,\n                  height: 50,', 'width: 220,\n                  height: 44,')
text = text.replace('width: 220,\n                  child: DropdownButtonFormField<int>(', 'width: 220,\n                  height: 44,\n                  child: DropdownButtonFormField<int>(')

# 5) Reduce table status chips and text slightly so five rows fit comfortably.
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),', 'padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),')
text = text.replace('fontSize: 13,\n              height: 1.25', 'fontSize: 12.5,\n              height: 1.15')
text = text.replace('fontSize: 13))),', 'fontSize: 12.5))),')

# 6) If previous scripts created an outer forced table height, remove it and use the actual available height.
text = text.replace('final tableHeight = availableHeight < 820 ? 820.0 : availableHeight;', 'final tableHeight = availableHeight;')
text = text.replace('final tableHeight = availableHeight < 760 ? 760.0 : availableHeight;', 'final tableHeight = availableHeight;')

# 7) The footer text should reflect selected page size, not always 10.
text = text.replace(
    "'Showing $start-$end Of $total - Page ${page + 1} Of $pageCount - 10 Per Page'",
    "'Showing $start-$end Of $total - Page ${page + 1} Of $pageCount'",
)

path.write_text(text, encoding='utf-8')
print('Table layout compacted: Employees table should show about 5 rows while keeping Display Names 1/10/100.')
