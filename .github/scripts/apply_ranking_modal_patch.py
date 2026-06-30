from pathlib import Path
import textwrap

p = Path('lib/main.dart')
s = p.read_text()

# Ranking table: add Approved Rank after Points Earned.
s = s.replace(
    """GridCol('points_earned', 'Points Earned', isNumber: true),
          ],
          onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),""",
    """GridCol('points_earned', 'Points Earned', isNumber: true),
            GridCol('approved_rank_text', 'Approved Rank', flex: 2),
          ],
          onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),""",
    1,
)

# Ranking report: add Approved Rank after Points Earned.
s = s.replace(
    """GridCol('points_earned', 'Points Earned', isNumber: true),
        ]),""",
    """GridCol('points_earned', 'Points Earned', isNumber: true),
          GridCol('approved_rank_text', 'Approved Rank', flex: 2),
        ]),""",
    1,
)

# Choose Rank modal: remove SG from the rank label.
s = s.replace(
    """final rows = await db.from('ranks').select('name, default_salary, salary_grade').order('sort_order').order('name').limit(500);""",
    """final rows = await db.from('ranks').select('name, default_salary').order('sort_order').order('name').limit(500);""",
    1,
)
s = s.replace("""      final sg = r['salary_grade'] == null ? '' : ' - SG ${r['salary_grade']}';
      final pay = salary == null ? '' : ' - ${formatMoney(salary)}';
      out.add(EditOption(name, '$name$sg$pay', salary: salary));""", """      final pay = salary == null ? '' : ' - ${formatMoney(salary)}';
      out.add(EditOption(name, '$name$pay', salary: salary));""", 1)

# Salary controller display should use PHP 12,760.00 style.
s = s.replace("""  final previousSalary = TextEditingController(text: formatEditValue(initial?['previous_salary']));
  final appliedRank = TextEditingController(text: formatEditValue(initial?['applied_rank_text']));
  final appliedSalary = TextEditingController(text: formatEditValue(initial?['applied_salary']));
  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));
  final approvedRank = TextEditingController(text: formatEditValue(initial?['approved_rank_text']));
  final approvedSalary = TextEditingController(text: formatEditValue(initial?['approved_salary']));""", """  final previousSalary = TextEditingController(text: formatMoneyEdit(initial?['previous_salary']));
  final appliedRank = TextEditingController(text: formatEditValue(initial?['applied_rank_text']));
  final appliedSalary = TextEditingController(text: formatMoneyEdit(initial?['applied_salary']));
  final points = TextEditingController(text: formatEditValue(initial?['points_earned']));
  final approvedRank = TextEditingController(text: formatEditValue(initial?['approved_rank_text']));
  final approvedSalary = TextEditingController(text: formatMoneyEdit(initial?['approved_salary']));""", 1)

# Picking a rank should write formatted money into the salary box.
s = s.replace("""    if (selected.salary != null) salary.text = selected.salary!.toStringAsFixed(2);""", """    if (selected.salary != null) salary.text = formatMoney(selected.salary);""", 1)

# Remove Ranking Cycle dropdown from the visible modal, but keep hidden cycle_id value for saving.
cycle_block = """                SizedBox(
                  width: 354,
                  child: DropdownButtonFormField<String>(
                    value: optionValueOrFirst(cycleId, cycles, true),
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Ranking Cycle'),
                    items: uniqueOptions(cycles).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                    validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                    onChanged: (v) => setDialogState(() => cycleId = v),
                  ),
                ),
"""
s = s.replace(cycle_block, "", 1)

# Previous Rank and Previous Salary are read-only.
s = s.replace("""                rankTextBox('Previous Rank', previousRank, () => pickRank(previousRank, previousSalary)),
                textBox('Previous Salary', previousSalary, kind: FieldKind.number),""", """                textBox('Previous Rank', previousRank, readOnly: true),
                textBox('Previous Salary', previousSalary, kind: FieldKind.number, readOnly: true),""", 1)

# Save salary values by stripping PHP prefix and commas.
s = s.replace("""                'previous_salary': num.tryParse(previousSalary.text.trim()),
                'applied_rank_text': emptyToNull(appliedRank.text),
                'applied_salary': num.tryParse(appliedSalary.text.trim()),
                'points_earned': num.tryParse(points.text.trim()),
                'approved_rank_text': emptyToNull(approvedRank.text),
                'approved_salary': num.tryParse(approvedSalary.text.trim()),""", """                'previous_salary': parseMoneyInput(previousSalary.text),
                'applied_rank_text': emptyToNull(appliedRank.text),
                'applied_salary': parseMoneyInput(appliedSalary.text),
                'points_earned': num.tryParse(points.text.trim()),
                'approved_rank_text': emptyToNull(approvedRank.text),
                'approved_salary': parseMoneyInput(approvedSalary.text),""", 1)

# Upgrade the generic ranking textBox helper to support read-only display.
old_textbox = """Widget textBox(String label, TextEditingController controller, {FieldKind kind = FieldKind.text}) => SizedBox(width: 354, child: TextFormField(controller: controller, keyboardType: kind == FieldKind.number || kind == FieldKind.integer ? TextInputType.number : TextInputType.text, maxLines: kind == FieldKind.multiline ? 3 : 1, decoration: InputDecoration(labelText: label)));"""
new_textbox = """Widget textBox(String label, TextEditingController controller, {FieldKind kind = FieldKind.text, bool readOnly = false}) => SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: readOnly,
        keyboardType: kind == FieldKind.number || kind == FieldKind.integer ? TextInputType.number : TextInputType.text,
        maxLines: kind == FieldKind.multiline ? 3 : 1,
        style: TextStyle(color: readOnly ? _muted : _ink, fontWeight: readOnly ? FontWeight.w800 : FontWeight.w500),
        decoration: InputDecoration(labelText: label, fillColor: readOnly ? const Color(0xFFF8FAFC) : Colors.white),
      ),
    );"""
s = s.replace(old_textbox, new_textbox, 1)

# Add helpers for formatted money edit display and parsing formatted money input.
if 'String formatMoneyEdit(Object? value)' not in s:
    s = s.replace("""String formatEditValue(Object? value) => value == null ? '' : formatValue(value) == '-' ? '' : formatValue(value);
""", """String formatEditValue(Object? value) => value == null ? '' : formatValue(value) == '-' ? '' : formatValue(value);

String formatMoneyEdit(Object? value) {
  final text = formatMoney(value);
  return text == '-' ? '' : text;
}

num? parseMoneyInput(String text) {
  final cleaned = text.replaceAll(RegExp(r'[^0-9.\-]'), '');
  if (cleaned.trim().isEmpty) return null;
  return num.tryParse(cleaned);
}
""", 1)

p.write_text(s)
