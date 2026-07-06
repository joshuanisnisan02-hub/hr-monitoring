from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def find_matching(src: str, start: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    in_single = False
    in_double = False
    escape = False
    for i in range(start, len(src)):
        ch = src[i]
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

def replace_function(src: str, signature: str, end_marker: str, new_block: str) -> str:
    start = src.find(signature)
    if start < 0:
        return src
    end = src.find(end_marker, start)
    if end < 0:
        return src
    return src[:start] + new_block + src[end:]

# -----------------------------------------------------------------------------
# 1) Make sure DateSlashInputFormatter exists and works while typing.
# -----------------------------------------------------------------------------
if "import 'package:flutter/services.dart';" not in text:
    text = text.replace(
        "import 'package:flutter/material.dart';\n",
        "import 'package:flutter/material.dart';\nimport 'package:flutter/services.dart';\n",
        1,
    )

formatter_start = text.find('class DateSlashInputFormatter extends TextInputFormatter')
if formatter_start >= 0:
    formatter_end = text.find('\n}\n', formatter_start)
    if formatter_end >= 0:
        formatter_end += 3
        text = text[:formatter_start] + text[formatter_end:]

formatter = r'''
class DateSlashInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    var digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (digits.length > 8) digits = digits.substring(0, 8);
    final out = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i == 2 || i == 4) out.write('/');
      out.write(digits[i]);
    }
    final value = out.toString();
    return TextEditingValue(
      text: value,
      selection: TextSelection.collapsed(offset: value.length),
    );
  }
}

'''
marker = "SupabaseClient get db => Supabase.instance.client;\n"
if marker in text:
    text = text.replace(marker, marker + "\n" + formatter, 1)

# -----------------------------------------------------------------------------
# 2) Strengthen date parsing. Accept typed 07062026 and auto-slashed 07/06/2026.
# -----------------------------------------------------------------------------
parse_start = text.find('DateTime? parseFlexibleDate(Object? value) {')
parse_end = text.find('String formatDateLong(Object? value)', parse_start)
if parse_start >= 0 and parse_end > parse_start:
    new_parse = r'''DateTime? parseFlexibleDate(Object? value) {
  if (value == null) return null;
  final text = value.toString().trim();
  if (text.isEmpty || text == '-') return null;

  final compact = RegExp(r'^(\d{2})(\d{2})(\d{4})$').firstMatch(text);
  if (compact != null) {
    try {
      return DateFormat('MM/dd/yyyy').parseStrict(
          '${compact.group(1)!}/${compact.group(2)!}/${compact.group(3)!}');
    } catch (_) {}
  }

  final iso = RegExp(r'^(\d{4})-(\d{2})-(\d{2})').firstMatch(text);
  if (iso != null) {
    return DateTime.tryParse('${iso.group(1)}-${iso.group(2)}-${iso.group(3)}');
  }
  for (final pattern in const [
    'MM/dd/yyyy',
    'M/d/yyyy',
    'MM-dd-yyyy',
    'M-d-yyyy',
    'MMMM dd, yyyy',
    'MMMM d, yyyy',
    'MMM dd, yyyy',
    'MMM d, yyyy',
  ]) {
    try {
      return DateFormat(pattern).parseStrict(text);
    } catch (_) {}
  }
  return null;
}

'''
    text = text[:parse_start] + new_parse + text[parse_end:]

# -----------------------------------------------------------------------------
# 3) Fix generic edit dialog date fields.
#    Important: text field must NOT open the calendar popup on tap.
#    Only the calendar icon opens the picker. Enter saves.
# -----------------------------------------------------------------------------
widgets_start = text.find('List<Widget> buildDialogFieldWidgets(')
widgets_end = text.find('Future<Map<String, dynamic>?> showRecordDialog', widgets_start)
if widgets_start >= 0 and widgets_end > widgets_start:
    block = text[widgets_start:widgets_end]
    sig_start = 0
    paren_start = block.find('(')
    paren_end = find_matching(block, paren_start, '(', ')')
    brace_start = block.find('{', paren_end)
    if paren_end >= 0 and brace_start >= 0:
        new_sig = '''List<Widget> buildDialogFieldWidgets(
  BuildContext context,
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState, {
  VoidCallback? onDateSubmit,
}) '''
        block = new_sig + block[brace_start:]

    # Remove any date onTap that opens showDatePicker when the field itself is clicked.
    block = re.sub(
        r'''\n\s*readOnly:\s*isDate,\s*\n\s*onTap:\s*isDate\s*\?\s*\(\)\s*=>\s*pickDateIntoController\(context,\s*controllers\[f\.key\]!\)\s*:\s*null,''',
        '''\n        readOnly: false,''',
        block,
        flags=re.S,
    )
    block = block.replace('        readOnly: isDate,', '        readOnly: false,')

    # Keyboard/input formatter/enter save.
    if 'inputFormatters: isDate ? [DateSlashInputFormatter()] : null,' not in block:
        block = block.replace(
            '''        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer
            ? TextInputType.number
            : TextInputType.text,''',
            '''        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: isDate
            ? TextInputType.datetime
            : (f.kind == FieldKind.number || f.kind == FieldKind.integer
                ? TextInputType.number
                : TextInputType.text),
        inputFormatters: isDate ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: isDate ? (_) => onDateSubmit?.call() : null,''',
        )
    block = block.replace("hintText: isDate ? 'Select date' : null,", "hintText: isDate ? 'MM/DD/YYYY' : null,")
    text = text[:widgets_start] + block + text[widgets_end:]

# showRecordDialog: ensure Enter calls same Save helper.
show_start = text.find('Future<Map<String, dynamic>?> showRecordDialog')
show_end = text.find('class AddEmployeeFullResult', show_start)
if show_start >= 0 and show_end > show_start:
    block = text[show_start:show_end]
    block = re.sub(r'\n\s*onDateSubmit:\s*submitDialog,\s*', '\n', block)
    if 'void submitDialog() {' not in block:
        submit = r'''  void submitDialog() {
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
        insert = block.find('final result = await showDialog<Map<String, dynamic>>(')
        if insert >= 0:
            block = block[:insert] + submit + block[insert:]
    call_start = block.find('...buildDialogFieldWidgets(')
    if call_start >= 0:
        paren = block.find('(', call_start)
        close = find_matching(block, paren, '(', ')')
        comma = close + 1
        while comma < len(block) and block[comma].isspace():
            comma += 1
        if comma < len(block) and block[comma] == ',':
            comma += 1
        replacement = '''...buildDialogFieldWidgets(
                    context,
                    fields,
                    controllers,
                    selected,
                    setDialogState,
                    onDateSubmit: submitDialog,
                  ),'''
        block = block[:call_start] + replacement + block[comma:]
    # Save button = submitDialog.
    actions = block.find('actions:')
    button = block.find('FilledButton(', actions)
    onp = block.find('onPressed:', button)
    if onp >= 0 and 'onPressed: submitDialog' not in block[onp:onp+90]:
        brace = block.find('{', onp)
        if brace >= 0:
            endb = find_matching(block, brace, '{', '}')
            comma = endb + 1
            while comma < len(block) and block[comma].isspace():
                comma += 1
            if comma < len(block) and block[comma] == ',':
                comma += 1
            block = block[:onp] + 'onPressed: submitDialog,' + block[comma:]
    text = text[:show_start] + block + text[show_end:]

# -----------------------------------------------------------------------------
# 4) Add Employee dialog date fields.
# -----------------------------------------------------------------------------
add_start = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
add_end = text.find('Future<void> addEmployeeFull', add_start)
if add_start >= 0 and add_end > add_start:
    block = text[add_start:add_end]

    if 'void submitAddEmployeeDialog() {' not in block:
        actions = block.find('actions:')
        button = block.find('FilledButton(', actions)
        onp = block.find('onPressed: () {', button)
        if onp >= 0:
            brace = block.find('{', onp)
            endb = find_matching(block, brace, '{', '}')
            body = block[brace+1:endb].strip('\n')
            helper = '  void submitAddEmployeeDialog() {\n' + body + '\n  }\n\n'
            insert = block.find('  Widget textBox(')
            if insert >= 0:
                block = block[:insert] + helper + block[insert:]

    # Local textBox: do not open date picker on field tap, type date directly.
    block = block.replace(
        '''        readOnly: date,
        keyboardType: keyboardType,
        onTap: date ? () => pickDateIntoController(context, controller) : null,''',
        '''        readOnly: false,
        keyboardType: date ? TextInputType.datetime : keyboardType,
        inputFormatters: date ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: date ? (_) => submitAddEmployeeDialog() : null,''',
    )
    block = block.replace('        readOnly: date,', '        readOnly: false,')
    block = block.replace("hintText: date ? 'Select date' : null,", "hintText: date ? 'MM/DD/YYYY' : null,")

    # Contract Start Date in Add Employee: remove onTap calendar popup from field itself.
    block = re.sub(
        r'''controller:\s*contractStart,\s*\n\s*readOnly:\s*true,\s*\n\s*onTap:\s*\(\)\s*=>\s*pickDateIntoController\(\s*context,\s*contractStart,\s*afterPick:\s*\(\)\s*=>\s*setDialogState\(recomputeContract\)\),''',
        '''controller: contractStart,
                          readOnly: false,
                          keyboardType: TextInputType.datetime,
                          inputFormatters: [DateSlashInputFormatter()],
                          onFieldSubmitted: (_) => submitAddEmployeeDialog(),''',
        block,
        flags=re.S,
    )
    block = block.replace("hintText: 'Select date',", "hintText: 'MM/DD/YYYY',")

    # Save button = helper.
    actions = block.find('actions:')
    button = block.find('FilledButton(', actions)
    onp = block.find('onPressed:', button)
    if onp >= 0 and 'onPressed: submitAddEmployeeDialog' not in block[onp:onp+120]:
        brace = block.find('{', onp)
        if brace >= 0:
            endb = find_matching(block, brace, '{', '}')
            comma = endb + 1
            while comma < len(block) and block[comma].isspace():
                comma += 1
            if comma < len(block) and block[comma] == ',':
                comma += 1
            block = block[:onp] + 'onPressed: submitAddEmployeeDialog,' + block[comma:]

    text = text[:add_start] + block + text[add_end:]

# -----------------------------------------------------------------------------
# 5) Contract dialog date field: typeable, calendar only through icon if present.
# -----------------------------------------------------------------------------
contract_start = text.find('Widget contractDatePickerBox(')
contract_end = text.find('Widget contractReadOnlyBox', contract_start)
if contract_start >= 0 and contract_end > contract_start:
    block = text[contract_start:contract_end]
    block = block.replace('        readOnly: true,', '        readOnly: false,')
    if 'inputFormatters: [DateSlashInputFormatter()],' not in block:
        block = block.replace(
            """        decoration: const InputDecoration(
          labelText: 'Start Date',""",
            """        keyboardType: TextInputType.datetime,
        inputFormatters: [DateSlashInputFormatter()],
        onFieldSubmitted: (_) => setDialogState(recomputeContract),
        decoration: const InputDecoration(
          labelText: 'Start Date',""",
            1,
        )
    block = block.replace("hintText: 'Select start date',", "hintText: 'MM/DD/YYYY',")
    # Remove old onTap showDatePicker block if still present.
    block = re.sub(r'''\n\s*onTap:\s*\(\)\s*async\s*\{[\s\S]*?setDialogState\(\(\)\s*\{[\s\S]*?recomputeContract\(\);[\s\S]*?\}\);[\s\S]*?\},''', '\n', block)
    text = text[:contract_start] + block + text[contract_end:]

# Calendar picker selected value should insert the fast format.
text = text.replace("DateFormat('MMMM dd, yyyy').format(picked)", "DateFormat('MM/dd/yyyy').format(picked)")
text = text.replace("DateFormat('MMMM dd, yyyy').format(computedEnd)", "DateFormat('MM/dd/yyyy').format(computedEnd)")
text = text.replace("DateFormat('MMMM dd, yyyy').format(end)", "DateFormat('MM/dd/yyyy').format(end)")

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Date fields may already be fixed.')
else:
    print('Fixed date fields: no popup on field click, auto-slash typing, and Enter-to-save.')
