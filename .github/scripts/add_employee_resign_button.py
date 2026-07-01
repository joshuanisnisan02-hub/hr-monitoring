from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# 1) Add optional resign handler to CrudTable.
if 'final EditHandler? onResign;' not in text:
    text = text.replace('  final EditHandler? onApprove;\n', '  final EditHandler? onApprove;\n  final EditHandler? onResign;\n', 1)

if 'this.onResign' not in text:
    old_ctor = 'this.onView, this.onApprove, this.showDelete = true'
    if old_ctor in text:
        text = text.replace(old_ctor, 'this.onView, this.onApprove, this.onResign, this.showDelete = true', 1)
    else:
        raise SystemExit('CrudTable constructor parameter area was not found.')

if 'if (widget.onResign != null) count++;' not in text:
    marker = '    if (widget.onApprove != null) count++;\n'
    if marker not in text:
        raise SystemExit('CrudTable actionWidth block was not found.')
    text = text.replace(marker, marker + '    if (widget.onResign != null) count++;\n', 1)

if 'onResign: widget.onResign == null ? null' not in text:
    marker = '                  onApprove: widget.onApprove == null ? null : () => widget.onApprove!(context, rows[i], refresh),\n'
    if marker not in text:
        raise SystemExit('TableRowItem call block was not found.')
    text = text.replace(marker, marker + '                  onResign: widget.onResign == null ? null : () => widget.onResign!(context, rows[i], refresh),\n', 1)

# 2) Add optional resign button to TableRowItem.
if 'final VoidCallback? onResign;' not in text:
    text = text.replace('  final VoidCallback? onApprove;\n  final VoidCallback? onDelete;\n', '  final VoidCallback? onApprove;\n  final VoidCallback? onResign;\n  final VoidCallback? onDelete;\n', 1)

if 'this.onResign' not in text[text.find('class TableRowItem'):text.find('Widget tableCell', text.find('class TableRowItem'))]:
    text = text.replace('this.onView, required this.onEdit, this.onApprove, this.onDelete', 'this.onView, required this.onEdit, this.onApprove, this.onResign, this.onDelete', 1)

if "tooltip: 'Mark as Resigned'" not in text:
    marker = "              if (onApprove != null) IconButton(tooltip: 'Approve Applied Rank', onPressed: onApprove, icon: const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 20)),\n"
    if marker not in text:
        raise SystemExit('Action buttons block was not found.')
    text = text.replace(marker, marker + "              if (onResign != null) IconButton(tooltip: 'Mark as Resigned', onPressed: onResign, icon: const Icon(Icons.person_off_rounded, color: Color(0xFFB91C1C), size: 20)),\n", 1)

# 3) Add employee resign function.
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
    marker = 'Future<void> viewEmployee(BuildContext context, Map<String, dynamic> row) async {'
    if marker not in text:
        marker = 'Future<void> editEmployee(BuildContext context,'
    if marker not in text:
        raise SystemExit('Employee function insertion point was not found.')
    text = text.replace(marker, resign_function + marker, 1)

# 4) Wire button only in Employees CrudTable.
if 'onResign: resignEmployee' not in text:
    employees_start = text.find('class EmployeesPage')
    contracts_start = text.find('class ContractsPage', employees_start)
    if employees_start == -1 or contracts_start == -1:
        raise SystemExit('EmployeesPage block was not found.')
    block = text[employees_start:contracts_start]
    marker = "              onView: viewEmployee,\n              onEdit: editEmployee,\n"
    if marker not in block:
        raise SystemExit('Employees CrudTable action handlers were not found.')
    block = block.replace(marker, "              onView: viewEmployee,\n              onEdit: editEmployee,\n              onResign: resignEmployee,\n", 1)
    text = text[:employees_start] + block + text[contracts_start:]

path.write_text(text, encoding='utf-8')
print('Employee resign action button added to lib/main.dart')
