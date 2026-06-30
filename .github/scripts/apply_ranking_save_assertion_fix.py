from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Add a small safe refresh helper to prevent table rebuild during dialog teardown.
if 'void safeRefresh(VoidCallback refresh)' not in s:
    s = s.replace(
        """SupabaseClient get db => Supabase.instance.client;
""",
        """SupabaseClient get db => Supabase.instance.client;

void safeRefresh(VoidCallback refresh) {
  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());
}
""",
        1,
    )

# Ranking save should unfocus before closing the dialog to prevent Flutter inherited/focus assertion.
s = s.replace(
    """              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, {
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],""",
    """              if (!formKey.currentState!.validate()) return;
              FocusManager.instance.primaryFocus?.unfocus();
              Navigator.of(context, rootNavigator: true).pop({
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],""",
    1,
)

# Allow dialog widgets to unmount before disposing ranking text controllers.
s = s.replace(
    """  for (final c in [appointment, previousRank, previousSalary, appliedRank, appliedSalary, points]) {
    c.dispose();
  }
  return result;
}""",
    """  await Future<void>.delayed(Duration.zero);
  for (final c in [appointment, previousRank, previousSalary, appliedRank, appliedSalary, points]) {
    c.dispose();
  }
  return result;
}""",
    1,
)

# Save ranking directly so refresh runs after the dialog route has fully closed.
s = s.replace(
    """  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'ranking_applications', data['employee_id'], 'ranking')) return;
  await saveRow(context, 'ranking_applications', row?['id'], data, refresh);
}
""",
    """  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'ranking_applications', data['employee_id'], 'ranking')) return;
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (row == null) {
      await db.from('ranking_applications').insert(data);
      if (context.mounted) showSnack(context, 'Record Added.');
    } else {
      await db.from('ranking_applications').update(data).eq('id', row['id']);
      if (context.mounted) showSnack(context, 'Record Updated.');
    }
    safeRefresh(refresh);
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Failed: $e');
  }
}
""",
    1,
)

p.write_text(s)
