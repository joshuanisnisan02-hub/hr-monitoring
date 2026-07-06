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

# -----------------------------------------------------------------------------
# 1) Ensure TextInputFormatter import and DateSlashInputFormatter exist.
# -----------------------------------------------------------------------------
if "import 'package:flutter/services.dart';" not in text:
    text = text.replace(
        "import 'package:flutter/material.dart';\n",
        "import 'package:flutter/material.dart';\nimport 'package:flutter/services.dart';\n",
        1,
    )

if 'class DateSlashInputFormatter extends TextInputFormatter' not in text:
    formatter = r'''
class DateSlashInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    var digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (digits.length > 8) digits = digits.substring(0, 8);
    final buffer = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i == 2 || i == 4) buffer.write('/');
      buffer.write(digits[i]);
    }
    final out = buffer.toString();
    return TextEditingValue(
      text: out,
      selection: TextSelection.collapsed(offset: out.length),
    );
  }
}

'''
    marker = "SupabaseClient get db => Supabase.instance.client;\n"
    text = text.replace(marker, marker + "\n" + formatter, 1)

# Add compact MM/DD/YYYY parsing support when user types 01012026.
if "final compact = RegExp(r'^(\\d{2})(\\d{2})(\\d{4})$')" not in text:
    text = text.replace(
        """  if (text.isEmpty || text == '-') return null;
  final iso = RegExp(r'^(\\d{4})-(\\d{2})-(\\d{2})').firstMatch(text);""",
        """  if (text.isEmpty || text == '-') return null;
  final compact = RegExp(r'^(\\d{2})(\\d{2})(\\d{4})$').firstMatch(text);
  if (compact != null) {
    final m = int.tryParse(compact.group(1)!);
    final d = int.tryParse(compact.group(2)!);
    final y = int.tryParse(compact.group(3)!);
    if (m != null && d != null && y != null) {
      try {
        return DateFormat('MM/dd/yyyy').parseStrict(
            '${m.toString().padLeft(2, '0')}/${d.toString().padLeft(2, '0')}/${y.toString().padLeft(4, '0')}');
      } catch (_) {}
    }
  }
  final iso = RegExp(r'^(\\d{4})-(\\d{2})-(\\d{2})').firstMatch(text);""",
        1,
    )

# -----------------------------------------------------------------------------
# 2) Fix buildDialogFieldWidgets signature and make date fields typeable.
# -----------------------------------------------------------------------------
sig_start = text.find('List<Widget> buildDialogFieldWidgets(')
if sig_start >= 0:
    paren_start = text.find('(', sig_start)
    paren_end = find_matching(text, paren_start, '(', ')')
    brace_start = text.find('{', paren_end)
    new_sig = '''List<Widget> buildDialogFieldWidgets(
  BuildContext context,
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState, {
  VoidCallback? onDateSubmit,
}) '''
    if paren_end > 0 and brace_start > 0:
        text = text[:sig_start] + new_sig + text[brace_start:]

# Replace date TextFormField properties in generic dialog.
text = text.replace(
    """        readOnly: isDate,
        onTap: isDate
            ? () => pickDateIntoController(context, controllers[f.key]!)
            : null,
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer
            ? TextInputType.number
            : TextInputType.text,""",
    """        readOnly: false,
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: isDate
            ? TextInputType.datetime
            : (f.kind == FieldKind.number || f.kind == FieldKind.integer
                ? TextInputType.number
                : TextInputType.text),
        inputFormatters: isDate ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: isDate ? (_) => onDateSubmit?.call() : null,""",
)
text = text.replace("hintText: isDate ? 'Select date' : null,", "hintText: isDate ? 'MM/DD/YYYY' : null,")

# -----------------------------------------------------------------------------
# 3) Fix showRecordDialog: Enter in generic date fields triggers the same Save.
# -----------------------------------------------------------------------------
show_start = text.find('Future<Map<String, dynamic>?> showRecordDialog')
show_end = text.find('class AddEmployeeFullResult', show_start)
if show_start >= 0 and show_end > show_start:
    chunk = text[show_start:show_end]

    # Remove accidental bad standalone argument lines.
    chunk = re.sub(r'\n\s*onDateSubmit:\s*submitDialog,\s*', '\n', chunk)

    # Ensure submitDialog exists in the right function.
    if 'void submitDialog() {' not in chunk:
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
        insert = chunk.find('final result = await showDialog<Map<String, dynamic>>(')
        if insert >= 0:
            chunk = chunk[:insert] + submit_body + chunk[insert:]

    # Replace the buildDialogFieldWidgets call inside the spread.
    call = '...buildDialogFieldWidgets('
    call_start = chunk.find(call)
    if call_start >= 0:
        paren_start = chunk.find('(', call_start)
        paren_end = find_matching(chunk, paren_start, '(', ')')
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

    # Replace the showRecordDialog Save button onPressed with submitDialog.
    actions_i = chunk.find('actions:')
    filled_i = chunk.find('FilledButton(', actions_i)
    on_i = chunk.find('onPressed:', filled_i)
    if on_i >= 0 and 'onPressed: submitDialog' not in chunk[on_i:on_i + 80]:
        brace = chunk.find('{', on_i)
        if brace >= 0:
            body_end = find_matching(chunk, brace, '{', '}')
            if body_end >= 0:
                comma_end = body_end + 1
                while comma_end < len(chunk) and chunk[comma_end].isspace():
                    comma_end += 1
                if comma_end < len(chunk) and chunk[comma_end] == ',':
                    comma_end += 1
                chunk = chunk[:on_i] + 'onPressed: submitDialog,' + chunk[comma_end:]

    text = text[:show_start] + chunk + text[show_end:]

# -----------------------------------------------------------------------------
# 4) Add Employee date fields: typeable MM/DD/YYYY and Enter = Save.
# -----------------------------------------------------------------------------
add_start = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
add_end = text.find('Future<void> addEmployeeFull', add_start)
if add_start >= 0 and add_end > add_start:
    chunk = text[add_start:add_end]
    if 'void submitAddEmployeeDialog() {' not in chunk:
        # Reuse the body of the existing Save button to avoid duplicate logic drift.
        save_i = chunk.find('FilledButton(', chunk.find('actions:'))
        on_i = chunk.find('onPressed: () {', save_i)
        if on_i >= 0:
            brace = chunk.find('{', on_i)
            body_end = find_matching(chunk, brace, '{', '}')
            body = chunk[brace + 1:body_end].strip('\n')
            helper = '  void submitAddEmployeeDialog() {\n' + body + '\n  }\n\n'
            insert = chunk.find('  Widget textBox(')
            if insert >= 0:
                chunk = chunk[:insert] + helper + chunk[insert:]
    # Make local textBox date field typeable and enter-save.
    chunk = chunk.replace(
        """        readOnly: date,
        keyboardType: keyboardType,
        onTap: date ? () => pickDateIntoController(context, controller) : null,""",
        """        readOnly: false,
        keyboardType: date ? TextInputType.datetime : keyboardType,
        inputFormatters: date ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: date ? (_) => submitAddEmployeeDialog() : null,""",
    )
    chunk = chunk.replace("hintText: date ? 'Select date' : null,", "hintText: date ? 'MM/DD/YYYY' : null,")
    # Contract start date in Add Employee.
    chunk = chunk.replace('''                          controller: contractStart,
                          readOnly: true,
                          onTap: () => pickDateIntoController(
                              context, contractStart,
                              afterPick: () =>
                                  setDialogState(recomputeContract)),''',
        '''                          controller: contractStart,
                          readOnly: false,
                          keyboardType: TextInputType.datetime,
                          inputFormatters: [DateSlashInputFormatter()],
                          onFieldSubmitted: (_) => submitAddEmployeeDialog(),''')
    chunk = chunk.replace("hintText: 'Select date',", "hintText: 'MM/DD/YYYY',")

    # Replace Add Employee Save button with the helper.
    save_i = chunk.find('FilledButton(', chunk.find('actions:'))
    on_i = chunk.find('onPressed:', save_i)
    if on_i >= 0 and 'onPressed: submitAddEmployeeDialog' not in chunk[on_i:on_i + 100]:
        brace = chunk.find('{', on_i)
        if brace >= 0:
            body_end = find_matching(chunk, brace, '{', '}')
            comma_end = body_end + 1
            while comma_end < len(chunk) and chunk[comma_end].isspace():
                comma_end += 1
            if comma_end < len(chunk) and chunk[comma_end] == ',':
                comma_end += 1
            chunk = chunk[:on_i] + 'onPressed: submitAddEmployeeDialog,' + chunk[comma_end:]

    text = text[:add_start] + chunk + text[add_end:]

# -----------------------------------------------------------------------------
# 5) Date picker selection should also use MM/DD/YYYY.
# -----------------------------------------------------------------------------
text = text.replace("DateFormat('MMMM dd, yyyy').format(picked)", "DateFormat('MM/dd/yyyy').format(picked)")
text = text.replace("DateFormat('MMMM dd, yyyy').format(computedEnd)", "DateFormat('MM/dd/yyyy').format(computedEnd)")
text = text.replace("DateFormat('MMMM dd, yyyy').format(end)", "DateFormat('MM/dd/yyyy').format(end)")

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Fast date input may already be installed.')
else:
    print('Applied final fast date input: MM/DD/YYYY, auto slash, and Enter-to-save for date fields.')
