from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# ---------- Helpers ----------
def replace_once(source: str, old: str, new: str, label: str) -> str:
    if old not in source:
        raise SystemExit(f'{label} was not found.')
    return source.replace(old, new, 1)

# ---------- 1) Patch CrudTable with page-size options ----------
crud_start = text.find('class CrudTable')
state_start = text.find('class _CrudTableState', crud_start)
if crud_start == -1 or state_start == -1:
    raise SystemExit('CrudTable class block was not found.')
crud = text[crud_start:state_start]

if 'final List<int> pageSizeOptions;' not in crud:
    if 'final String? reportTitle;' in crud:
        crud = crud.replace('final String? reportTitle;', 'final String? reportTitle;\n  final List<int> pageSizeOptions;\n  final int initialPageSize;', 1)
    elif 'final Future<dynamic> Function(Map<String, dynamic> row) onDelete;' in crud:
        crud = crud.replace('final Future<dynamic> Function(Map<String, dynamic> row) onDelete;', 'final List<int> pageSizeOptions;\n  final int initialPageSize;\n  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;', 1)
    else:
        raise SystemExit('CrudTable field insertion point was not found.')

if 'this.pageSizeOptions' not in crud:
    ctor_start = crud.find('CrudTable({')
    if ctor_start == -1:
        ctor_start = crud.find('CrudTable (')
    if ctor_start == -1:
        raise SystemExit('CrudTable constructor was not found. Send the CrudTable constructor section for manual patching.')
    ctor_end = crud.find('});', ctor_start)
    if ctor_end == -1:
        raise SystemExit('CrudTable constructor end was not found.')
    ctor_end += 3
    ctor = crud[ctor_start:ctor_end]
    insert_param = 'this.pageSizeOptions = const [10], this.initialPageSize = 10,'
    if 'required this.onDelete' in ctor:
        ctor = ctor.replace('required this.onDelete', insert_param + ' required this.onDelete', 1)
    elif 'this.reportTitle,' in ctor:
        ctor = ctor.replace('this.reportTitle,', 'this.reportTitle, ' + insert_param, 1)
    else:
        ctor = ctor[:-3].rstrip()
        if ctor.endswith(','):
            ctor += ' ' + insert_param[:-1]
        else:
            ctor += ', ' + insert_param[:-1]
        ctor += '});'
    crud = crud[:ctor_start] + ctor + crud[ctor_end:]

text = text[:crud_start] + crud + text[state_start:]

# ---------- 2) Patch _CrudTableState page handling ----------
state_start = text.find('class _CrudTableState')
next_class = text.find('class TableToolbar', state_start)
if state_start == -1 or next_class == -1:
    raise SystemExit('_CrudTableState block was not found.')
state = text[state_start:next_class]

if 'int pageSize = _pageSize;' not in state and 'int pageSize =' not in state:
    state = replace_once(state, '  int page = 0;\n', '  int page = 0;\n  int pageSize = _pageSize;\n', 'CrudTable page field')

if 'pageSize = widget.pageSizeOptions.contains(widget.initialPageSize)' not in state:
    state = replace_once(
        state,
        '    super.initState();\n',
        '    super.initState();\n    pageSize = widget.pageSizeOptions.contains(widget.initialPageSize) ? widget.initialPageSize : widget.pageSizeOptions.first;\n',
        'CrudTable initState super call',
    )

# Keep current page after save/edit/refresh; safePage already clamps if count changes.
state = re.sub(
    r"void refresh\(\) => setState\(\(\) \{\s*future = widget\.load\(\);\s*page = 0;\s*\}\);",
    "void refresh() => setState(() {\n        future = widget.load();\n      });",
    state,
    count=1,
    flags=re.S,
)

# Replace hardcoded _pageSize only inside CrudTable state.
state = state.replace('~/ _pageSize', '~/ pageSize')
state = state.replace('* _pageSize', '* pageSize')
state = state.replace('take(_pageSize)', 'take(pageSize)')

# Add selector between toolbar and table.
if "labelText: 'Display Names'" not in state:
    marker = '            const SizedBox(height: 14),\n            Expanded(child:'
    if marker not in state:
        raise SystemExit('Toolbar-to-table marker was not found in CrudTable state.')
    selector = r'''            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 220,
                  child: DropdownButtonFormField<int>(
                    value: pageSize,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Display Names'),
                    items: widget.pageSizeOptions.map((value) => DropdownMenuItem<int>(value: value, child: Text('$value per page'))).toList(),
                    onChanged: (value) => setState(() {
                      pageSize = value ?? pageSize;
                      page = 0;
                    }),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),
            Expanded(child:'''
    state = state.replace(marker, selector, 1)

text = text[:state_start] + state + text[next_class:]

# ---------- 3) Update footer wording if it is hardcoded to 10 per page ----------
text = text.replace(" - 10 Per Page'", " Per Page'")
text = text.replace(" - 10 per page'", " Per Page'")

# ---------- 4) Employees module only: 1/10/100 and hide resigned ----------
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')
emp = text[emp_start:emp_end]

if 'pageSizeOptions: const [1, 10, 100]' not in emp:
    search_pos = emp.find('searchHint:')
    if search_pos == -1:
        raise SystemExit('Employees CrudTable searchHint was not found.')
    line_start = emp.rfind('\n', 0, search_pos) + 1
    indent = emp[line_start:search_pos]
    emp = emp[:line_start] + indent + 'pageSizeOptions: const [1, 10, 100],\n' + indent + 'initialPageSize: 10,\n' + emp[line_start:]

if "status.contains('resign')" not in emp:
    func_pos = emp.find('bool matchesGenderFilter(Map<String, dynamic> row)')
    if func_pos != -1:
        brace = emp.find('{', func_pos)
        insert_at = brace + 1
        emp = emp[:insert_at] + "\n    final status = formatValue(row['employment_status']).toLowerCase();\n    if (status.contains('resign')) return false;" + emp[insert_at:]
    else:
        # Fallback: filter in loadFilteredEmployees where pipeline exists.
        old = '.where(matchesGenderFilter).toList()'
        new = ".where((row) => !formatValue(row['employment_status']).toLowerCase().contains('resign')).where(matchesGenderFilter).toList()"
        if old not in emp:
            raise SystemExit('Could not find employee filter insertion point.')
        emp = emp.replace(old, new, 1)

text = text[:emp_start] + emp + text[emp_end:]

path.write_text(text, encoding='utf-8')
print('Employee module paging/resigned flow v2 applied successfully.')
