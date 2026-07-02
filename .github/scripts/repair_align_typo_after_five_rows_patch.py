from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# Previous compact-layout script accidentally replaced Align( with Align: inside CrudTable.
# Repair that syntax error first.
text = text.replace('              Align:\n', '              Align(\n')
text = text.replace('Align:\n', 'Align(\n')
text = text.replace('Align:', 'Align(')

# Make sure the Display Names control is compact and valid.
text = text.replace(
    "width: 220,\n                  height: 44,\n                  height: 44,",
    "width: 220,\n                  height: 44,",
)

# Enforce a compact but readable table layout so around 5 rows are visible.
text = text.replace(
    'padding: const EdgeInsets.fromLTRB(28, 24, 28, 28),',
    'padding: const EdgeInsets.fromLTRB(28, 18, 28, 18),',
)
text = text.replace(
    'const SizedBox(height: 22),\n          Expanded(child: child),',
    'const SizedBox(height: 14),\n          Expanded(child: child),',
)
text = text.replace(
    'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),',
    'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),',
)
text = text.replace(
    'constraints: const BoxConstraints(minHeight: 50),',
    'constraints: const BoxConstraints(minHeight: 42),',
)
text = text.replace(
    'constraints: const BoxConstraints(minHeight: 46),',
    'constraints: const BoxConstraints(minHeight: 42),',
)
text = text.replace(
    'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),',
    'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 7),',
)
text = text.replace(
    'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),',
    'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),',
)
text = text.replace(
    'padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),',
    'padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),',
)

# Keep table using available height, not forced oversized outer scroll.
text = text.replace(
    'final tableHeight = availableHeight < 820 ? 820.0 : availableHeight;',
    'final tableHeight = availableHeight;',
)

path.write_text(text, encoding='utf-8')
print('Repaired Align syntax and kept compact 5-row table layout.')
