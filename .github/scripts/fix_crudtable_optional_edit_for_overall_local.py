from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Make CrudTable edit handler optional so read-only tabs/modules can show View only.
text = text.replace(
    '  final EditHandler onEdit;\n',
    '  final EditHandler? onEdit;\n',
    1,
)
text = text.replace(
    '      required this.onEdit,\n',
    '      this.onEdit,\n',
    1,
)

# Action width should no longer reserve space for Edit when edit is hidden.
text = text.replace(
    '  double get actionWidth {\n    var count = 1; // Edit button\n',
    '  double get actionWidth {\n    var count = widget.onEdit == null ? 0 : 1; // Edit button\n',
    1,
)

# Pass a nullable edit callback to rows.
text = text.replace(
    '                  onEdit: () => widget.onEdit(context, rows[i], refresh),\n',
    '                  onEdit: widget.onEdit == null\n                      ? null\n                      : () => widget.onEdit!(context, rows[i], refresh),\n',
    1,
)

# TableRowItem should accept and render nullable edit action.
text = text.replace(
    '  final VoidCallback onEdit;\n',
    '  final VoidCallback? onEdit;\n',
    1,
)
text = text.replace(
    '      required this.onEdit,\n',
    '      this.onEdit,\n',
    1,
)
text = text.replace(
    """              IconButton(
                  tooltip: 'Edit',
                  onPressed: onEdit,
                  icon: const Icon(Icons.edit_rounded,
                      color: _primary, size: 20)),""",
    """              if (onEdit != null)
                IconButton(
                    tooltip: 'Edit',
                    onPressed: onEdit,
                    icon: const Icon(Icons.edit_rounded,
                        color: _primary, size: 20)),""",
    1,
)

if text == original:
    print('No changes applied. CrudTable optional edit support may already be present.')
else:
    path.write_text(text, encoding='utf-8')
    print('Fixed CrudTable so Overall Evaluation can be View-only with no Edit action.')
