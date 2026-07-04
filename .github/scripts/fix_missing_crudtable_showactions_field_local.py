from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

class_marker = 'class CrudTable extends StatefulWidget {'
ctor_marker = '  const CrudTable('
class_start = text.find(class_marker)
ctor_start = text.find(ctor_marker, class_start)
if class_start < 0 or ctor_start < 0:
    raise SystemExit('Could not find CrudTable class/constructor.')

crud_fields = text[class_start:ctor_start]
if 'final bool showActions;' not in crud_fields:
    text = text[:ctor_start] + '  final bool showActions;\n' + text[ctor_start:]

# Keep edit optional for read-only tables such as Resigned Employees and Overall Evaluation.
text = text.replace('  final EditHandler onEdit;\n', '  final EditHandler? onEdit;\n', 1)
text = text.replace('      required this.onEdit,\n', '      this.onEdit,\n', 1)
text = text.replace('  final VoidCallback onEdit;\n', '  final VoidCallback? onEdit;\n', 1)
text = text.replace('      required this.onEdit,\n', '      this.onEdit,\n', 1)

# If the constructor somehow still does not have the default, add it after showDelete.
class_start = text.find(class_marker)
ctor_start = text.find(ctor_marker, class_start)
ctor_end = text.find('})', ctor_start)
ctor_block = text[ctor_start:ctor_end]
if 'this.showActions' not in ctor_block:
    text = text[:ctor_end] + '      this.showActions = true,\n' + text[ctor_end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. CrudTable showActions field may already be fixed.')
else:
    print('Fixed missing CrudTable showActions field.')
