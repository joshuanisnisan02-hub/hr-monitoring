from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

crud_start = text.find('class CrudTable')
state_start = text.find('class _CrudTableState', crud_start)
if crud_start == -1 or state_start == -1:
    raise SystemExit('CrudTable block was not found.')

crud = text[crud_start:state_start]

if 'final List<int> pageSizeOptions;' not in crud:
    if 'final String? reportTitle;' in crud:
        crud = crud.replace('final String? reportTitle;', 'final String? reportTitle;\n  final List<int> pageSizeOptions;\n  final int initialPageSize;', 1)
    elif 'final Future<dynamic> Function(Map<String, dynamic> row) onDelete;' in crud:
        crud = crud.replace('final Future<dynamic> Function(Map<String, dynamic> row) onDelete;', 'final List<int> pageSizeOptions;\n  final int initialPageSize;\n  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;', 1)
    else:
        raise SystemExit('Could not add pageSizeOptions fields.')

# Locate the CrudTable constructor and add missing named parameters robustly.
ctor_pos = crud.find('const CrudTable')
if ctor_pos == -1:
    raise SystemExit('CrudTable constructor was not found.')

open_paren = crud.find('(', ctor_pos)
if open_paren == -1:
    raise SystemExit('CrudTable constructor opening parenthesis was not found.')

depth = 0
quote = None
escape = False
close_paren = -1
for i in range(open_paren, len(crud)):
    ch = crud[i]
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
                close_paren = i
                break

if close_paren == -1:
    raise SystemExit('CrudTable constructor closing parenthesis was not found.')

ctor = crud[ctor_pos:close_paren + 1]

if 'this.pageSizeOptions' not in ctor:
    insert = "    this.pageSizeOptions = const [10],\n    this.initialPageSize = 10,\n"
    if 'required this.onDelete,' in ctor:
        ctor = ctor.replace('required this.onDelete,', insert + '    required this.onDelete,', 1)
    elif 'required this.onDelete' in ctor:
        ctor = ctor.replace('required this.onDelete', insert + '    required this.onDelete', 1)
    elif 'this.reportTitle,' in ctor:
        ctor = ctor.replace('this.reportTitle,', 'this.reportTitle,\n' + insert, 1)
    else:
        # Add before the closing parenthesis inside the named parameter list.
        ctor = ctor[:-1].rstrip()
        if not ctor.endswith(','):
            ctor += ','
        ctor += '\n' + insert.rstrip() + '\n  )'

crud = crud[:ctor_pos] + ctor + crud[close_paren + 1:]
text = text[:crud_start] + crud + text[state_start:]

path.write_text(text, encoding='utf-8')
print('CrudTable constructor repaired: pageSizeOptions and initialPageSize are initialized.')
