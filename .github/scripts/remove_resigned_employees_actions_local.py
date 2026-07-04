from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Make CrudTable able to fully hide the Actions column for read-only tables.
if '  final bool showActions;' not in text:
    text = text.replace(
        '  final bool showDelete;\n',
        '  final bool showDelete;\n  final bool showActions;\n',
        1,
    )
    text = text.replace(
        '      this.showDelete = true,\n',
        '      this.showDelete = true,\n      this.showActions = true,\n',
        1,
    )

# Ensure edit action is nullable so a read-only table does not require it.
text = text.replace('  final EditHandler onEdit;\n', '  final EditHandler? onEdit;\n', 1)
text = text.replace('      required this.onEdit,\n', '      this.onEdit,\n', 1)
text = text.replace('  final VoidCallback onEdit;\n', '  final VoidCallback? onEdit;\n', 1)
text = text.replace('      required this.onEdit,\n', '      this.onEdit,\n', 1)

text = text.replace(
    '  double get actionWidth {\n    var count = 1; // Edit button\n',
    '  double get actionWidth {\n    if (!widget.showActions) return 0;\n    var count = widget.onEdit == null ? 0 : 1; // Edit button\n',
    1,
)
text = text.replace(
    '  double get actionWidth {\n    var count = widget.onEdit == null ? 0 : 1; // Edit button\n',
    '  double get actionWidth {\n    if (!widget.showActions) return 0;\n    var count = widget.onEdit == null ? 0 : 1; // Edit button\n',
    1,
)

text = text.replace(
    '                showActions: true,\n                actionWidth: actionWidth,',
    '                showActions: widget.showActions,\n                actionWidth: actionWidth,',
    1,
)
text = text.replace(
    '                  onView: widget.onView == null\n                      ? null\n                      : () => widget.onView!(context, rows[i]),\n                  onEdit: () => widget.onEdit(context, rows[i], refresh),',
    '                  onView: !widget.showActions || widget.onView == null\n                      ? null\n                      : () => widget.onView!(context, rows[i]),\n                  onEdit: !widget.showActions || widget.onEdit == null\n                      ? null\n                      : () => widget.onEdit!(context, rows[i], refresh),',
    1,
)
text = text.replace(
    '                  onView: widget.onView == null\n                      ? null\n                      : () => widget.onView!(context, rows[i]),\n                  onEdit: widget.onEdit == null\n                      ? null\n                      : () => widget.onEdit!(context, rows[i], refresh),',
    '                  onView: !widget.showActions || widget.onView == null\n                      ? null\n                      : () => widget.onView!(context, rows[i]),\n                  onEdit: !widget.showActions || widget.onEdit == null\n                      ? null\n                      : () => widget.onEdit!(context, rows[i], refresh),',
    1,
)
text = text.replace(
    '                  onApprove: widget.onApprove == null\n                      ? null\n                      : () => widget.onApprove!(context, rows[i], refresh),\n                  extraAction: widget.extraAction == null\n                      ? null\n                      : widget.extraAction!(context, rows[i], refresh),\n                  onDelete: widget.showDelete',
    '                  onApprove: !widget.showActions || widget.onApprove == null\n                      ? null\n                      : () => widget.onApprove!(context, rows[i], refresh),\n                  extraAction: !widget.showActions || widget.extraAction == null\n                      ? null\n                      : widget.extraAction!(context, rows[i], refresh),\n                  onDelete: widget.showActions && widget.showDelete',
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

# Add showActions: false to the Resigned Employees CrudTable only.
page_title = "title: 'Resigned Employees'"
idx = text.find(page_title)
if idx < 0:
    raise SystemExit('Could not find Resigned Employees page.')
crud_idx = text.find('CrudTable(', idx)
if crud_idx < 0:
    raise SystemExit('Could not find Resigned Employees CrudTable.')
end_idx = text.find('),', crud_idx)
if end_idx < 0:
    end_idx = text.find(');', crud_idx)
block = text[crud_idx:end_idx]
if 'showActions: false' not in block:
    insert_at = text.find('columns:', crud_idx)
    if insert_at < 0 or insert_at > end_idx:
        raise SystemExit('Could not find columns marker in Resigned Employees CrudTable.')
    text = text[:insert_at] + 'showActions: false,\n              ' + text[insert_at:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Resigned Employees actions column may already be hidden.')
else:
    print('Removed Actions column from Resigned Employees table.')
