from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

signature_start = text.find('List<Widget> buildDialogFieldWidgets(')
if signature_start < 0:
    raise SystemExit('Could not find buildDialogFieldWidgets signature.')

paren_start = text.find('(', signature_start)
if paren_start < 0:
    raise SystemExit('Could not parse buildDialogFieldWidgets signature.')

depth = 0
paren_end = -1
for i in range(paren_start, len(text)):
    if text[i] == '(':
        depth += 1
    elif text[i] == ')':
        depth -= 1
        if depth == 0:
            paren_end = i
            break
if paren_end < 0:
    raise SystemExit('Could not find end of buildDialogFieldWidgets parameters.')

brace_start = text.find('{', paren_end)
if brace_start < 0 or brace_start - paren_end > 20:
    raise SystemExit('Could not find buildDialogFieldWidgets opening brace.')

new_signature = '''List<Widget> buildDialogFieldWidgets(
  BuildContext context,
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState, {
  VoidCallback? onDateSubmit,
}) '''
text = text[:signature_start] + new_signature + text[brace_start:]

# Clean the showRecordDialog call in case the previous scripts left bad formatting.
show_start = text.find('Future<Map<String, dynamic>?> showRecordDialog')
show_end = text.find('class AddEmployeeFullResult', show_start)
if show_start >= 0 and show_end > show_start:
    chunk = text[show_start:show_end]
    # If a lone onDateSubmit line exists outside the call, remove it first.
    chunk = chunk.replace('                  onDateSubmit: submitDialog,\n                  ),', '                  onDateSubmit: submitDialog),')
    chunk = chunk.replace('                  onDateSubmit: submitDialog,\n                ),', '                  onDateSubmit: submitDialog,\n                ),')
    text = text[:show_start] + chunk + text[show_end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. buildDialogFieldWidgets may already accept onDateSubmit.')
else:
    print('Fixed buildDialogFieldWidgets onDateSubmit signature.')
