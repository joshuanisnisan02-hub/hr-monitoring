from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')

emp = text[emp_start:emp_end]

# Remove the Excel Employee Matching card from Employee module only.
marker_text = "Excel Employee Matching"
if marker_text in emp:
    marker_pos = emp.find(marker_text)
    card_start = emp.rfind('          Card(', 0, marker_pos)
    if card_start == -1:
        raise SystemExit('Could not locate Employee Matching Card start.')

    # Find the matching end of Card(...), plus the following SizedBox spacer.
    paren_start = emp.find('(', card_start)
    depth = 0
    quote = None
    escape = False
    card_end = -1
    for i in range(paren_start, len(emp)):
        ch = emp[i]
        if quote:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    # Include trailing comma/newline after Card(...),
                    card_end = i + 1
                    break
    if card_end == -1:
        raise SystemExit('Could not locate Employee Matching Card end.')

    # Include trailing comma and whitespace.
    j = card_end
    while j < len(emp) and emp[j] in ' \t\r\n,':
        j += 1

    # Remove immediately following spacer if it exists.
    spacer = 'const SizedBox(height: 14),'
    if emp[j:j + len(spacer)] == spacer:
        j += len(spacer)
        while j < len(emp) and emp[j] in ' \t\r\n,':
            j += 1

    emp = emp[:card_start] + emp[j:]

# Tighten top spacing after employee filters so the table gets more room.
emp = emp.replace('          const SizedBox(height: 14),\n          Card(', '          const SizedBox(height: 10),\n          Card(', 1)
emp = emp.replace('          const SizedBox(height: 14),\n          Expanded(', '          const SizedBox(height: 10),\n          Expanded(', 1)

text = text[:emp_start] + emp + text[emp_end:]

# Make the generic CrudTable table area taller and more visible.
# This reduces wasted outer scroll height and gives the data table more vertical room.
text = text.replace('final tableHeight = availableHeight < 820 ? 820.0 : availableHeight;', 'final tableHeight = availableHeight;')
text = text.replace('return SingleChildScrollView(\n                controller: crudOuterScrollController,\n                child: SizedBox(\n                  height: tableHeight,\n                  child: tableContent,\n                ),\n              );', 'return SizedBox(\n                height: tableHeight,\n                child: tableContent,\n              );')
text = text.replace('return SingleChildScrollView(\n                  controller: crudOuterScrollController,\n                  child: SizedBox(\n                    height: tableHeight,\n                    child: tableContent,\n                  ),\n                );', 'return SizedBox(\n                  height: tableHeight,\n                  child: tableContent,\n                );')
text = text.replace('return SingleChildScrollView(\n                controller: crudOuterScrollController,\n                child: SizedBox(height: tableHeight, child: tableContent),\n              );', 'return SizedBox(height: tableHeight, child: tableContent);')

# Compact table toolbar/display dropdown and rows slightly.
text = text.replace('const SizedBox(height: 14),\n            Expanded(child:', 'const SizedBox(height: 8),\n            Expanded(child:')
text = text.replace('const SizedBox(height: 14),\n            PaginationFooter(', 'const SizedBox(height: 8),\n            PaginationFooter(')
text = text.replace('const SizedBox(height: 10),\n              Align(', 'const SizedBox(height: 6),\n              Align(')
text = text.replace('width: 220,\n                  child: DropdownButtonFormField<int>(', 'width: 220,\n                  height: 50,\n                  child: DropdownButtonFormField<int>(')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 7),')
text = text.replace('constraints: const BoxConstraints(minHeight: 50),', 'constraints: const BoxConstraints(minHeight: 46),')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),')

path.write_text(text, encoding='utf-8')
print('Removed Employee Matching card and made table area taller/more visible while keeping Display Names.')
