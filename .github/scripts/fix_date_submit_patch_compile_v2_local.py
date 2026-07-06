from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text


def find_matching(src: str, start: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    escape = False
    for i in range(start, len(src)):
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
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
    return -1


def remove_named_void_functions(src: str, name: str) -> str:
    pos = 0
    while True:
        m = re.search(r'\n[ \t]*void\s+' + re.escape(name) + r'\s*\(\)\s*\{', src[pos:])
        if not m:
            return src
        start = pos + m.start() + 1
        brace = src.find('{', start)
        end = find_matching(src, brace, '{', '}')
        if end < 0:
            return src
        line_end = src.find('\n', end)
        if line_end < 0:
            line_end = end
        src = src[:start] + src[line_end + 1:]
        pos = start

# Remove every misplaced submitDialog. A correct one is recreated below inside showRecordDialog.
text = remove_named_void_functions(text, 'submitDialog')

# Fix buildDialogFieldWidgets signature to accept the optional onDateSubmit callback.
if 'VoidCallback? onDateSubmit' not in text:
    text = re.sub(
        r'(List<Widget>\s+buildDialogFieldWidgets\s*\([\s\S]*?StateSetter\s+setDialogState,)\s*\)\s*\{',
        r'\1 {\n  VoidCallback? onDateSubmit,\n}) {',
        text,
        count=1,
    )

# Locate showRecordDialog by the next class boundary instead of brace parsing.
start = text.find('Future<Map<String, dynamic>?> showRecordDialog')
end = text.find('class AddEmployeeFullResult', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate showRecordDialog block.')
chunk = text[start:end]

# Remove any accidental standalone named argument line left inside Wrap children.
chunk = re.sub(r'\n\s*onDateSubmit:\s*submitDialog,\s*', '\n', chunk)

# Replace the buildDialogFieldWidgets spread call with a clean, valid call.
call_start = chunk.find('...buildDialogFieldWidgets(')
if call_start < 0:
    raise SystemExit('Could not find buildDialogFieldWidgets call in showRecordDialog.')
paren_start = chunk.find('(', call_start)
paren_end = find_matching(chunk, paren_start, '(', ')')
if paren_end < 0:
    raise SystemExit('Could not parse buildDialogFieldWidgets call.')
comma_end = paren_end + 1
while comma_end < len(chunk) and chunk[comma_end].isspace():
    comma_end += 1
if comma_end < len(chunk) and chunk[comma_end] == ',':
    comma_end += 1
clean_call = '''...buildDialogFieldWidgets(
                    context,
                    fields,
                    controllers,
                    selected,
                    setDialogState,
                    onDateSubmit: submitDialog,
                  ),'''
chunk = chunk[:call_start] + clean_call + chunk[comma_end:]

# Insert the correct submitDialog inside showRecordDialog, after controllers/selected setup and before showDialog.
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
show_idx = chunk.find('showDialog<Map<String, dynamic>>')
if show_idx < 0:
    raise SystemExit('Could not find showDialog<Map<String, dynamic>> in showRecordDialog.')
insert_at = chunk.rfind('\n', 0, show_idx) + 1
# Include the line containing final result / await when present.
prev_line_start = chunk.rfind('\n', 0, max(0, insert_at - 1)) + 1
if 'final result' in chunk[prev_line_start:insert_at] or 'return' in chunk[prev_line_start:insert_at]:
    insert_at = prev_line_start
chunk = chunk[:insert_at] + submit_body + chunk[insert_at:]

# Ensure the Save button calls the helper. If already changed, this is harmless.
button_idx = chunk.find('FilledButton(', chunk.find('actions:'))
if button_idx >= 0:
    on_idx = chunk.find('onPressed:', button_idx)
    if on_idx >= 0:
        if chunk[on_idx:on_idx + 80].strip().startswith('onPressed: ()'):
            brace = chunk.find('{', on_idx)
            body_end = find_matching(chunk, brace, '{', '}')
            if body_end >= 0:
                comma_end = body_end + 1
                while comma_end < len(chunk) and chunk[comma_end].isspace():
                    comma_end += 1
                if comma_end < len(chunk) and chunk[comma_end] == ',':
                    comma_end += 1
                chunk = chunk[:on_idx] + 'onPressed: submitDialog,' + chunk[comma_end:]

text = text[:start] + chunk + text[end:]

path.write_text(text, encoding='utf-8')
print('Fixed remaining date submit compile errors.')
