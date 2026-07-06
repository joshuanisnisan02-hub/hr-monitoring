from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text


def find_matching_brace(src: str, open_brace: int) -> int:
    depth = 0
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    escape = False
    for i in range(open_brace, len(src)):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ''
        if in_line_comment:
            if ch == '\n':
                in_line_comment = False
            continue
        if in_block_comment:
            if ch == '*' and nxt == '/':
                in_block_comment = False
                continue
            continue
        if in_single:
            if ch == '\\' and not escape:
                escape = True
                continue
            if ch == "'" and not escape:
                in_single = False
            escape = False
            continue
        if in_double:
            if ch == '\\' and not escape:
                escape = True
                continue
            if ch == '"' and not escape:
                in_double = False
            escape = False
            continue
        if ch == '/' and nxt == '/':
            in_line_comment = True
            continue
        if ch == '/' and nxt == '*':
            in_block_comment = True
            continue
        if ch == "'":
            in_single = True
            continue
        if ch == '"':
            in_double = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def remove_void_function(src: str, name: str, predicate=None) -> str:
    pos = 0
    while True:
        idx = src.find(f'  void {name}()', pos)
        if idx < 0:
            idx = src.find(f'void {name}()', pos)
        if idx < 0:
            return src
        brace = src.find('{', idx)
        end = find_matching_brace(src, brace)
        if brace < 0 or end < 0:
            return src
        block = src[idx:end + 1]
        if predicate is None or predicate(block, idx):
            line_end = src.find('\n', end)
            if line_end < 0:
                line_end = end
            src = src[:idx] + src[line_end + 1:]
            pos = idx
        else:
            pos = end + 1


def function_bounds(src: str, signature: str):
    start = src.find(signature)
    if start < 0:
        return (-1, -1, -1)
    brace = src.find('{', start)
    end = find_matching_brace(src, brace)
    return (start, brace, end)

# Remove wrongly inserted submitDialog blocks that are not inside showRecordDialog.
rec_start, rec_brace, rec_end = function_bounds(text, 'Future<Map<String, dynamic>?> showRecordDialog')

def wrong_submit(block, idx):
    global rec_start, rec_end
    if rec_start <= idx <= rec_end:
        return False
    return 'for (final f in fields)' in block and 'controllers[f.key]' in block

text = remove_void_function(text, 'submitDialog', wrong_submit)

# Ensure buildDialogFieldWidgets accepts onDateSubmit.
start, brace, end = function_bounds(text, 'List<Widget> buildDialogFieldWidgets')
if start < 0:
    raise SystemExit('Could not find buildDialogFieldWidgets.')
params = text[start:brace]
if 'VoidCallback? onDateSubmit' not in params:
    # Replace the closing parameter pattern before the function body.
    old_tail = '  StateSetter setDialogState,\n) '
    new_tail = '  StateSetter setDialogState,\n  {VoidCallback? onDateSubmit}\n) '
    if old_tail in params:
        params2 = params.replace(old_tail, new_tail, 1)
        text = text[:start] + params2 + text[brace:]
    else:
        # More tolerant fallback.
        params2 = params.replace('  StateSetter setDialogState,\n', '  StateSetter setDialogState,\n  {VoidCallback? onDateSubmit}\n', 1)
        text = text[:start] + params2 + text[brace:]

# Recompute showRecordDialog bounds after edits.
rec_start, rec_brace, rec_end = function_bounds(text, 'Future<Map<String, dynamic>?> showRecordDialog')
if rec_start < 0:
    raise SystemExit('Could not find showRecordDialog.')
rec_block = text[rec_start:rec_end + 1]

submit_body = r'''  void submitDialog() {
    if (!formKey.currentState!.validate()) return;
    final out = <String, dynamic>{};
    for (final f in fields) {
      out[f.key] = f.kind == FieldKind.dropdown
          ? emptyToNull(selected[f.key])
          : parseFieldValue(controllers[f.key]!.text, f.kind);
    }
    Navigator.pop(context, out);
  }

'''

if 'void submitDialog() {' not in rec_block:
    insert_marker = '  final result = await showDialog<Map<String, dynamic>>('
    insert_rel = rec_block.find(insert_marker)
    if insert_rel < 0:
        raise SystemExit('Could not find showDialog in showRecordDialog.')
    rec_block = rec_block[:insert_rel] + submit_body + rec_block[insert_rel:]
    text = text[:rec_start] + rec_block + text[rec_end + 1:]

# Ensure the buildDialogFieldWidgets call is syntactically correct.
rec_start, rec_brace, rec_end = function_bounds(text, 'Future<Map<String, dynamic>?> showRecordDialog')
rec_block = text[rec_start:rec_end + 1]
if 'onDateSubmit: submitDialog' not in rec_block:
    old_call = '''...buildDialogFieldWidgets(
                    context, fields, controllers, selected, setDialogState),'''
    new_call = '''...buildDialogFieldWidgets(
                    context,
                    fields,
                    controllers,
                    selected,
                    setDialogState,
                    onDateSubmit: submitDialog),'''
    if old_call in rec_block:
        rec_block = rec_block.replace(old_call, new_call, 1)
    else:
        # Clean bad partial insertion if needed.
        rec_block = rec_block.replace('                  onDateSubmit: submitDialog,\n', '')
        rec_block = rec_block.replace('                ...buildDialogFieldWidgets(\n                    context, fields, controllers, selected, setDialogState),', new_call)
    text = text[:rec_start] + rec_block + text[rec_end + 1:]

# Ensure showRecordDialog Save button uses submitDialog and does not keep a duplicated inline block.
rec_start, rec_brace, rec_end = function_bounds(text, 'Future<Map<String, dynamic>?> showRecordDialog')
rec_block = text[rec_start:rec_end + 1]
# Replace the first FilledButton onPressed block inside showRecordDialog actions.
button_idx = rec_block.find('FilledButton(')
on_idx = rec_block.find('onPressed:', button_idx)
if button_idx >= 0 and on_idx >= 0 and 'onPressed: submitDialog' not in rec_block[button_idx:button_idx + 500]:
    brace = rec_block.find('{', on_idx)
    endb = find_matching_brace(rec_block, brace)
    if brace >= 0 and endb >= 0:
        comma = endb + 1
        while comma < len(rec_block) and rec_block[comma].isspace():
            comma += 1
        if comma < len(rec_block) and rec_block[comma] == ',':
            comma += 1
        rec_block = rec_block[:on_idx] + 'onPressed: submitDialog,' + rec_block[comma:]
        text = text[:rec_start] + rec_block + text[rec_end + 1:]

# Fix any remaining bad named argument layout around showRecordDialog call.
text = text.replace('                  onDateSubmit: submitDialog,\n                  ),', '                  onDateSubmit: submitDialog),')

path.write_text(text, encoding='utf-8')
print('Fixed compile errors from date Enter-to-save patch.')
