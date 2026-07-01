from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# This v3 does NOT change CrudTable constructor. It reuses existing onApprove action slot
# for Employees only, then changes the icon/tooltip dynamically for employee rows.

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
    try {
      await db.from('employees').update({
        'employment_status': 'Resigned',
        'updated_at': now,
      }).eq('id', employeeId);
    } catch (_) {
      await db.from('employees').update({'employment_status': 'Resigned'}).eq('id', employeeId);
    }

    try {
      await db.from('employee_contracts').update({
        'status': 'Resigned',
        'updated_at': now,
      }).eq('employee_id', employeeId);
    } catch (_) {
      await db.from('employee_contracts').update({'status': 'Resigned'}).eq('employee_id', employeeId);
    }

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

# Add employee resign action through existing onApprove slot.
if 'onApprove: resignEmployee' not in text:
    emp_start = text.find('class EmployeesPage')
    emp_end = text.find('class ContractsPage', emp_start)
    if emp_start == -1 or emp_end == -1:
        raise SystemExit('EmployeesPage block was not found.')
    emp_block = text[emp_start:emp_end]
    if 'onEdit: editEmployee,' in emp_block:
        emp_block = emp_block.replace('onEdit: editEmployee,', 'onEdit: editEmployee,\n              onApprove: resignEmployee,', 1)
    else:
        raise SystemExit('Employees CrudTable onEdit handler was not found.')
    text = text[:emp_start] + emp_block + text[emp_end:]

# Change existing onApprove icon to show red resign icon for employee rows only.
old_line = "if (onApprove != null) IconButton(tooltip: 'Approve Applied Rank', onPressed: onApprove, icon: const Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 20)),"
new_block = """if (onApprove != null)
                IconButton(
                  tooltip: row.containsKey('employment_status') ? 'Mark as Resigned' : 'Approve Applied Rank',
                  onPressed: onApprove,
                  icon: Icon(
                    row.containsKey('employment_status') ? Icons.person_off_rounded : Icons.check_circle_rounded,
                    color: row.containsKey('employment_status') ? const Color(0xFFB91C1C) : const Color(0xFF16A34A),
                    size: 20,
                  ),
                ),"""
if old_line in text:
    text = text.replace(old_line, new_block, 1)
elif "tooltip: row.containsKey('employment_status') ? 'Mark as Resigned'" in text:
    pass
else:
    raise SystemExit('Existing onApprove action icon line was not found.')

path.write_text(text, encoding='utf-8')
print('Employee resign button v3 applied using existing table action slot.')
