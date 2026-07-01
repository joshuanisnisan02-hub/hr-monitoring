from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# 1) Add per-page support to CrudTable.
crud_start = text.find('class CrudTable extends StatefulWidget')
crud_state_start = text.find('class _CrudTableState', crud_start)
if crud_start == -1 or crud_state_start == -1:
    raise SystemExit('CrudTable class was not found.')
crud = text[crud_start:crud_state_start]

if 'final List<int> pageSizeOptions;' not in crud:
    insert_after = '  final String? reportTitle;\n'
    if insert_after not in crud:
        raise SystemExit('CrudTable reportTitle field was not found.')
    crud = crud.replace(insert_after, insert_after + '  final List<int> pageSizeOptions;\n  final int initialPageSize;\n', 1)

if 'this.pageSizeOptions' not in crud:
    ctor_start = crud.find('const CrudTable({')
    ctor_end = crud.find('});', ctor_start)
    if ctor_start == -1 or ctor_end == -1:
        raise SystemExit('CrudTable constructor was not found.')
    ctor_end += 3
    ctor = crud[ctor_start:ctor_end]
    # Add before required onDelete when possible so trailing formatting stays valid.
    if 'required this.onDelete' in ctor:
        ctor = ctor.replace('required this.onDelete', 'this.pageSizeOptions = const [10], this.initialPageSize = 10, required this.onDelete', 1)
    else:
        ctor = ctor[:-3] + ', this.pageSizeOptions = const [10], this.initialPageSize = 10});'
    crud = crud[:ctor_start] + ctor + crud[ctor_end:]

text = text[:crud_start] + crud + text[crud_state_start:]

# 2) Add pageSize state and initialize it.
state_start = text.find('class _CrudTableState')
state_end = text.find('class TableToolbar', state_start)
if state_start == -1 or state_end == -1:
    raise SystemExit('_CrudTableState block was not found.')
state = text[state_start:state_end]

if 'int pageSize = _pageSize;' not in state:
    state = state.replace('  int page = 0;\n', '  int page = 0;\n  int pageSize = _pageSize;\n', 1)

if 'pageSize = widget.pageSizeOptions.contains(widget.initialPageSize)' not in state:
    state = state.replace(
        '    super.initState();\n',
        '    super.initState();\n    pageSize = widget.pageSizeOptions.contains(widget.initialPageSize) ? widget.initialPageSize : widget.pageSizeOptions.first;\n',
        1,
    )

# 3) Keep current page after edit/refresh instead of returning to first page / A.
state = re.sub(
    r"void refresh\(\) => setState\(\(\) \{\s*future = widget\.load\(\);\s*page = 0;\s*\}\);",
    "void refresh() => setState(() {\n        future = widget.load();\n      });",
    state,
    count=1,
)

# 4) Use dynamic pageSize in calculations.
state = state.replace('((sorted.length - 1) ~/ _pageSize) + 1', '((sorted.length - 1) ~/ pageSize) + 1')
state = state.replace('safePage * _pageSize', 'safePage * pageSize')
state = state.replace('take(_pageSize)', 'take(pageSize)')

# 5) Add per-page dropdown under toolbar only when options are provided.
if "labelText: 'Display Names'" not in state:
    toolbar_end = '            ),\n            const SizedBox(height: 14),'
    if toolbar_end not in state:
        raise SystemExit('Could not find CrudTable toolbar spacing insertion point.')
    page_size_widget = r'''            ),
            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 210,
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
            const SizedBox(height: 14),'''
    state = state.replace(toolbar_end, page_size_widget, 1)

text = text[:state_start] + state + text[state_end:]

# 6) Update footer text to avoid hardcoded 10 Per Page.
text = text.replace(" - 10 Per Page'", " Per Page'")

# 7) Enable 1/10/100 page display only in Employees table.
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start == -1 or emp_end == -1:
    raise SystemExit('EmployeesPage block was not found.')
emp = text[emp_start:emp_end]

if 'pageSizeOptions: const [1, 10, 100]' not in emp:
    marker = "              searchHint: 'Search employee"
    if marker not in emp:
        raise SystemExit('Employees CrudTable searchHint marker was not found.')
    emp = emp.replace(marker, "              pageSizeOptions: const [1, 10, 100],\n              initialPageSize: 10,\n" + marker, 1)

# 8) Hide resigned employees from Employees module. They remain visible in Resigned Employees module.
if "status.contains('resign')" not in emp:
    match_marker = '  bool matchesGenderFilter(Map<String, dynamic> row) {\n'
    if match_marker not in emp:
        raise SystemExit('matchesGenderFilter function was not found.')
    emp = emp.replace(
        match_marker,
        match_marker + "    final status = formatValue(row['employment_status']).toLowerCase();\n    if (status.contains('resign')) return false;\n",
        1,
    )

text = text[:emp_start] + emp + text[emp_end:]

path.write_text(text, encoding='utf-8')
print('Employee module updated: 1/10/100 display option, edit refresh keeps current page, resigned employees hidden from Employees and kept in Resigned Employees.')
