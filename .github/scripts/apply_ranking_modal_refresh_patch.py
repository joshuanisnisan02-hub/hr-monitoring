from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Prevent repeated clicks from stacking duplicate add/edit dialogs.
s = s.replace(
    """  bool sortAscending = true;
""",
    """  bool sortAscending = true;
  bool actionInProgress = false;
""",
    1,
)

old_refresh = """  void refresh() => setState(() {
        future = widget.load();
        page = 0;
      });
"""
new_refresh = """  void refresh() => setState(() {
        future = widget.load();
        page = 0;
      });

  Future<void> runAction(Future<void> Function() action) async {
    if (actionInProgress) return;
    setState(() => actionInProgress = true);
    try {
      await action();
    } finally {
      if (mounted) setState(() => actionInProgress = false);
    }
  }
"""
if old_refresh not in s and new_refresh not in s:
    raise SystemExit('CrudTable refresh block not found')
s = s.replace(old_refresh, new_refresh, 1)

s = s.replace(
    """              onAdd: widget.onAdd == null ? null : () => widget.onAdd!(context, refresh),
""",
    """              onAdd: widget.onAdd == null || actionInProgress ? null : () => runAction(() => widget.onAdd!(context, refresh)),
""",
    1,
)

old_actions = """                  onView: widget.onView == null ? null : () => widget.onView!(context, rows[i]),
                  onEdit: () => widget.onEdit(context, rows[i], refresh),
                  onApprove: widget.onApprove == null ? null : () => widget.onApprove!(context, rows[i], refresh),
                  onDelete: widget.showDelete ? () => confirmDelete(context, rows[i]) : null,
"""
new_actions = """                  onView: widget.onView == null || actionInProgress ? null : () => runAction(() => widget.onView!(context, rows[i])),
                  onEdit: actionInProgress ? () {} : () => runAction(() => widget.onEdit(context, rows[i], refresh)),
                  onApprove: widget.onApprove == null || actionInProgress ? null : () => runAction(() => widget.onApprove!(context, rows[i], refresh)),
                  onDelete: widget.showDelete && !actionInProgress ? () => runAction(() => confirmDelete(context, rows[i])) : null,
"""
if old_actions not in s and new_actions not in s:
    raise SystemExit('CrudTable row action block not found')
s = s.replace(old_actions, new_actions, 1)

# Make ranking save wait for the committed row and refresh the table immediately.
old_save = """    if (row == null) {
      await db.from('ranking_applications').insert(data);
      if (context.mounted) showSnack(context, 'Record Added.');
    } else {
      await db.from('ranking_applications').update(data).eq('id', row['id']);
      if (context.mounted) showSnack(context, 'Record Updated.');
    }
    safeRefresh(refresh);
"""
new_save = """    if (row == null) {
      await db.from('ranking_applications').insert(data).select('id').single();
      if (context.mounted) showSnack(context, 'Record Added.');
    } else {
      await db.from('ranking_applications').update(data).eq('id', row['id']).select('id').single();
      if (context.mounted) showSnack(context, 'Record Updated.');
    }
    refresh();
"""
if old_save not in s and new_save not in s:
    raise SystemExit('Ranking save block not found')
s = s.replace(old_save, new_save, 1)

s = s.replace(
    """  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));
""",
    """  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));
  bool submitting = false;
""",
    1,
)

# Close the ranking dialog through the local dialog navigator and disable buttons during submit.
old_dialog_actions = """        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              FocusManager.instance.primaryFocus?.unfocus();
              final out = <String, dynamic>{
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text),
                'previous_rank_text': emptyToNull(previousRank.text),
                'previous_salary': parseMoneyInput(previousSalary.text),
              };
              if (!isAdd) {
                out.addAll({
                  'applied_rank_text': emptyToNull(appliedRank.text),
                  'applied_salary': parseMoneyInput(appliedSalary.text),
                  'points_earned': num.tryParse(points.text.trim()),
                });
              }
              Navigator.of(context, rootNavigator: true).pop(out);
            },
            child: const Text('Save'),
          ),
        ],
"""
new_dialog_actions = """        actions: [
          TextButton(onPressed: submitting ? null : () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: submitting
                ? null
                : () {
                    if (!formKey.currentState!.validate()) return;
                    FocusManager.instance.primaryFocus?.unfocus();
                    final out = <String, dynamic>{
                      'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                      'cycle_id': emptyToNull(cycleId),
                      'appointment': emptyToNull(appointment.text),
                      'previous_rank_text': emptyToNull(previousRank.text),
                      'previous_salary': parseMoneyInput(previousSalary.text),
                    };
                    if (!isAdd) {
                      out.addAll({
                        'applied_rank_text': emptyToNull(appliedRank.text),
                        'applied_salary': parseMoneyInput(appliedSalary.text),
                        'points_earned': num.tryParse(points.text.trim()),
                      });
                    }
                    setDialogState(() => submitting = true);
                    Navigator.pop(context, out);
                  },
            child: submitting
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Save'),
          ),
        ],
"""
if old_dialog_actions not in s and new_dialog_actions not in s:
    raise SystemExit('Ranking dialog action block not found')
s = s.replace(old_dialog_actions, new_dialog_actions, 1)

p.write_text(s)
