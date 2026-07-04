from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

old_signature = """List<Widget> buildDialogFieldWidgets(
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState,
) {"""
new_signature = """List<Widget> buildDialogFieldWidgets(
  BuildContext context,
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState,
) {"""

old_call = """...buildDialogFieldWidgets(
                    fields, controllers, selected, setDialogState),"""
new_call = """...buildDialogFieldWidgets(
                    context, fields, controllers, selected, setDialogState),"""

text = text.replace(old_signature, new_signature, 1)
text = text.replace(old_call, new_call, 1)

if text == original:
    print('No changes applied. The BuildContext fix may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Fixed date picker BuildContext in employee/edit record dialogs.')
