from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# Locate CrudTable class only.
crud_start = text.find('class CrudTable extends StatefulWidget')
crud_state_start = text.find('class _CrudTableState', crud_start)
if crud_start == -1 or crud_state_start == -1:
    raise SystemExit('CrudTable class block was not found.')
crud_block = text[crud_start:crud_state_start]

# 1) Add onResign field to CrudTable.
if 'final EditHandler? onResign;' not in crud_block:
    if 'final EditHandler? onApprove;' in crud_block:
        crud_block = crud_block.replace('final EditHandler? onApprove;', 'final EditHandler? onApprove;\n  final EditHandler? onResign;', 1)
    elif 'final ViewHandler? onView;' in crud_block:
        crud_block = crud_block.replace('final ViewHandler? onView;', 'final ViewHandler? onView;\n  final EditHandler? onResign;', 1)
    else:
        raise SystemExit('Could not insert CrudTable onResign field.')

# 2) Add this.onResign to CrudTable constructor, regardless one-line/multiline formatting.
if 'this.onResign' not in crud_block:
    ctor_start = crud_block.find('const CrudTable({')
    if ctor_start == -1:
        raise SystemExit('CrudTable constructor was not found.')
    ctor_end = crud_block.find('});', ctor_start)
    if ctor_end == -1:
        raise SystemExit('CrudTable constructor end was not found.')
    ctor_end += 3
    ctor = crud_block[ctor_start:ctor_end]
    if 'this.onApprove,' in ctor:
        ctor = ctor.replace('this.onApprove,', 'this.onApprove, this.onResign,', 1)
    elif 'this.onView,' in ctor:
        ctor = ctor.replace('this.onView,', 'this.onView, this.onResign,', 1)
    elif 'required this.onEdit,' in ctor:
        ctor = ctor.replace('required this.onEdit,', 'required this.onEdit, this.onResign,', 1)
    else:
        raise SystemExit('Could not insert this.onResign in CrudTable constructor.')
    crud_block = crud_block[:ctor_start] + ctor + crud_block[ctor_end:]

text = text[:crud_start] + crud_block + text[crud_state_start:]

# 3) Add onResign to action width count.
if 'if (widget.onResign != null) count++;' not in text:
    if 'if (widget.onApprove != null) count++;' in text:
        text = text.replace('if (widget.onApprove != null) count++;', 'if (widget.onApprove != null) count++;\n    if (widget.onResign != null) count++;', 1)
    elif 'if (widget.onView != null) count++;' in text:
        text = text.replace('if (widget.onView != null) count++;', 'if (widget.onView != null) count++;\n    if (widget.onResign != null) count++;', 1)

# 4) Pass onResign to TableRowItem from CrudTable.
if 'onResign: widget.onResign == null ? null' not in text:
    target = 'onApprove: widget.onApprove == null ? null : () => widget.onApprove!(context, rows[i], refresh),'
    if target in text:
        text = text.replace(target, target + '\n                  onResign: widget.onResign == null ? null : () => widget.onResign!(context, rows[i], refresh),', 1)
    else:
        target = 'onEdit: () => widget.onEdit(context, rows[i], refresh),'
        if target not in text:
            raise SystemExit('TableRowItem call insertion point was not found.')
        text = text.replace(target, target + '\n                  onResign: widget.onResign == null ? null : () => widget.onResign!(context, rows[i], refresh),', 1)

# Locate TableRowItem class only.
table_start = text.find('class TableRowItem extends StatelessWidget')
table_end = text.find('Widget tableCell', table_start)
if table_start == -1 or table_end == -1:
    raise SystemExit('TableRowItem block was not found.')
table_block = text[table_start:table_end]

# 5) Add onResign field to TableRowItem.
if 'final VoidCallback? onResign;' not in table_block:
    if 'final VoidCallback? onApprove;' in table_block:
        table_block = table_block.replace('final VoidCallback? onApprove;', 'final VoidCallback? onApprove;\n  final VoidCallback? onResign;', 1)
    elif 'final VoidCallback? onDelete;' in table_block:
        table_block = table_block.replace('final VoidCallback? onDelete;', 'final VoidCallback? onResign;\n  final VoidCallback? onDelete;', 1)
    else:
        raise SystemExit('Could not insert TableRowItem onResign field.')

# 6) Add this.onResign to TableRowItem constructor.
if 'this.onResign' not in table_block:
    ctor_start = table_block.find('const TableRowItem({')
    ctor_end = table_block.find('});', ctor_start)
    if ctor_start == -1 or ctor_end == -1:
        raise SystemExit('TableRowItem constructor was not found.')
    ctor_end += 3
    ctor = table_block[ctor_start:ctor_end]
    if 'this.onApprove,' in ctor:
        ctor = ctor.replace('this.onApprove,', 'this.onApprove, this.onResign,', 1)
    elif 'this.onDelete' in ctor:
        ctor = ctor.replace('this.onDelete', 'this.onResign, this.onDelete', 1)
    else:
        raise SystemExit('Could not insert this.onResign in TableRowItem constructor.')
    table_block = table_block[:ctor_start] + ctor + table_block[ctor_end:]

# 7) Add resign icon button after approve or after edit.
if "tooltip: 'Mark as Resigned'" not in table_block:
    approve_btn = "if (onApprove != null) IconButton(tooltip: 'Approve Applied Rank', onPressed: onApprove, icon: const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 20)),"
    resign_btn = "if (onResign != null) IconButton(tooltip: 'Mark as Resigned', onPressed: onResign, icon: const Icon(Icons.person_off_rounded, color: Color(0xFFB91C1C), size: 20)),"
    if approve_btn in table_block:
        table_block = table_block.replace(approve_btn, approve_btn + '\n              ' + resign_btn, 1)
    else:
        edit_btn = "IconButton(tooltip: 'Edit', onPressed: onEdit, icon: const Icon(Icons.edit_rounded, color: _primary, size: 20)),"
        if edit_btn not in table_block:
            raise SystemExit('Action button insertion point was not found.')
        table_block = table_block.replace(edit_btn, edit_btn + '\n              ' + resign_btn, 1)

text = text[:table_start] + table_block + text[table_end:]

# 8) Add resignEmployee function before viewEmployee or editEmployee.
resign_function = r'''
Future<void> resignEmployee(BuildContext context, Map<String, dynamic> row, VoidCallback refresh) async {
  final employeeId = row['id'];
  final employeeName = formatValue(row['full_name']);
  if (employeeId == null) {
    showSnack(context, 'Unable to mark as resigned: missing employee ID.');
    return;
  }

  final currentStatus = formatValue(row['employment_status']).toLowerCase();
  if (currentStatus.contains('resign')) {
    showSnack(context, '$employeeName is already marked as resigned.');
    return;
  }

  final ok = await showDialog<bool>(
    context: context,
    barrierDismissible: false,
    builder: (_) => AlertDialog(
      title: const Text('Mark Employee as Resigned?'),
      content: SizedBox(
        width: 520,
        child: Text('This will set $employeeName as RESIGNED and will also mark the employee contract record as Resigned.\n\nClick OK to continue.'),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton.tonalIcon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.person_off_rounded),
          label: const Text('OK, Mark as Resigned'),
        ),
      ],
    ),
  );

  if (ok != true) return;

  try {
    final now = DateTime.now().toIso8601String();
    await db.from('employees').update({
      'employment_status': 'resigned',
      'updated_at': now,
    }).eq('id', employeeId);

    await db.from('employee_contracts').update({
      'status': 'Resigned',
      'updated_at': now,
    }).eq('employee_id', employeeId);

    refresh();
    if (context.mounted) showSnack(context, '$employeeName has been marked as resigned.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Mark as resigned failed: $e');
  }
}

'''
if 'Future<void> resignEmployee(' not in text:
    insertion = text.find('Future<void> viewEmployee(BuildContext context, Map<String, dynamic> row)')
    if insertion == -1:
        insertion = text.find('Future<void> editEmployee(BuildContext context,')
    if insertion == -1:
        raise SystemExit('Could not find employee function insertion point.')
    text = text[:insertion] + resign_function + text[insertion:]

# 9) Wire only Employees CrudTable.
if 'onResign: resignEmployee' not in text:
    emp_start = text.find('class EmployeesPage')
    emp_end = text.find('class ContractsPage', emp_start)
    if emp_start == -1 or emp_end == -1:
        raise SystemExit('EmployeesPage block was not found.')
    emp_block = text[emp_start:emp_end]
    if 'onEdit: editEmployee,' in emp_block:
        emp_block = emp_block.replace('onEdit: editEmployee,', 'onEdit: editEmployee,\n              onResign: resignEmployee,', 1)
    else:
        raise SystemExit('Employees CrudTable onEdit handler was not found.')
    text = text[:emp_start] + emp_block + text[emp_end:]

path.write_text(text, encoding='utf-8')
print('Employee resign action button v2 applied to lib/main.dart')
