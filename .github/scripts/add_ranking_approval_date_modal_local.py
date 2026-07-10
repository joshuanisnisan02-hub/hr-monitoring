from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

def find_matching_brace(src: str, brace_index: int) -> int:
    depth = 0
    in_single = False
    in_double = False
    escaped = False
    for i in range(brace_index, len(src)):
        ch = src[i]
        if in_single:
            if ch == '\\' and not escaped:
                escaped = True
                continue
            if ch == "'" and not escaped:
                in_single = False
            escaped = False
            continue
        if in_double:
            if ch == '\\' and not escaped:
                escaped = True
                continue
            if ch == '"':
                in_double = False
            escaped = False
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

replacement = r'''Future<void> approveRanking(BuildContext context, Map<String, dynamic> row,
    VoidCallback refresh) async {
  final normalized = normalizeRow(row);
  final formKey = GlobalKey<FormState>();
  final todayText = DateFormat('MMMM dd, yyyy').format(DateTime.now());
  final dateController = TextEditingController(
      text: formatEditValue(normalized['approved_date']).isEmpty
          ? todayText
          : formatEditValue(normalized['approved_date']));
  bool useToday = formatEditValue(normalized['approved_date']).isEmpty;

  final approvedDate = await showDialog<String>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Approve Ranking'),
        content: SizedBox(
          width: 520,
          child: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ReadOnlyEmployeeBox(formatValue(normalized['employee_name'])),
                const SizedBox(height: 16),
                TextFormField(
                  controller: dateController,
                  readOnly: useToday,
                  decoration: const InputDecoration(
                    labelText: 'Approved Date',
                    hintText: 'January 02, 2026',
                    suffixIcon: Icon(Icons.calendar_month_rounded),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Approved date is required';
                    }
                    if (parseFlexibleDate(value.trim()) == null) {
                      return 'Use January 02, 2026 or MM/DD/YYYY';
                    }
                    return null;
                  },
                  onTap: useToday
                      ? null
                      : () async {
                          final selected = await showDatePicker(
                            context: context,
                            initialEntryMode: DatePickerEntryMode.calendarOnly,
                            initialDate:
                                parseFlexibleDate(dateController.text) ??
                                    DateTime.now(),
                            firstDate: DateTime(2000),
                            lastDate: DateTime(2100),
                          );
                          if (selected != null) {
                            setDialogState(() => dateController.text =
                                DateFormat('MMMM dd, yyyy').format(selected));
                          }
                        },
                ),
                const SizedBox(height: 10),
                CheckboxListTile(
                  value: useToday,
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  controlAffinity: ListTileControlAffinity.leading,
                  title: const Text('Today'),
                  subtitle: const Text(
                      'Check this to automatically use today as the approved date.'),
                  onChanged: (value) => setDialogState(() {
                    useToday = value == true;
                    if (useToday) dateController.text = todayText;
                  }),
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton.icon(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, dateController.text.trim());
            },
            icon: const Icon(Icons.check_circle_rounded),
            label: const Text('Approve'),
          ),
        ],
      ),
    ),
  );

  dateController.dispose();
  if (approvedDate == null) return;

  try {
    await db.from('ranking_applications').update(upperCaseDataMap({
      'approved_rank_text': normalized['applied_rank_text'],
      'approved_salary': normalized['applied_salary'],
      'approved_date': toIsoDateInput(approvedDate),
      'updated_at': DateTime.now().toIso8601String(),
    })).eq('id', row['id']);
    refresh();
    if (context.mounted) showSnack(context, 'Ranking approved.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Approve Ranking Failed: $e');
  }
}

'''

start = text.find('Future<void> approveRanking(')
if start < 0:
    # Insert before the RankingPage class if the old function is missing.
    insert_at = text.find('class RankingPage')
    if insert_at < 0:
        raise SystemExit('Could not find approveRanking function or RankingPage insertion point.')
    text = text[:insert_at] + replacement + text[insert_at:]
else:
    brace = text.find('{', start)
    end = find_matching_brace(text, brace)
    if end < 0:
        raise SystemExit('Could not locate end of approveRanking function.')
    line_end = text.find('\n', end)
    if line_end < 0:
        line_end = end + 1
    text = text[:start] + replacement + text[line_end + 1:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Ranking approval modal may already be present.')
else:
    print('Added Ranking approval modal with Approved Date and Today checkbox.')
