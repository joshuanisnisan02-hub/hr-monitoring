from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# The resigned-filter script can leave an orphan function header like:
# ) async {
#   final resignedIds = await loadResignedEmployeeIdSet();
# Repair it into the intended loadResignedEmployees function signature.
text = text.replace(
    "\n) async {\n  final resignedIds = await loadResignedEmployeeIdSet();",
    "\nFuture<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {\n  final resignedIds = await loadResignedEmployeeIdSet();",
    1,
)

# Fix any broad named-parameter damage that may still exist from older repairs.
for name in [
    'textAlign',
    'alignment',
    'mainAxisAlignment',
    'crossAxisAlignment',
    'verticalDirection',
    'textDirection',
    'clipBehavior',
]:
    text = text.replace(f'{name}(', f'{name}:')
text = text.replace('textAlign( TextAlign.', 'textAlign: TextAlign.')
text = text.replace('mainAxisAlignment( MainAxisAlignment.', 'mainAxisAlignment: MainAxisAlignment.')
text = text.replace('crossAxisAlignment( CrossAxisAlignment.', 'crossAxisAlignment: CrossAxisAlignment.')
text = text.replace('alignment( Alignment.', 'alignment: Alignment.')
text = text.replace('Align:\n', 'Align(\n')
text = text.replace('              Align:\n', '              Align(\n')

# Remove duplicate loadResignedEmployees functions if older scripts created more than one.
def find_function_end(src: str, start: int) -> int:
    brace = src.find('{', start)
    if brace == -1:
        return -1
    depth = 0
    quote = None
    escape = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i + 1
    return -1

sig = 'Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {'
positions = []
start = 0
while True:
    pos = text.find(sig, start)
    if pos == -1:
        break
    positions.append(pos)
    start = pos + len(sig)

if len(positions) > 1:
    # Keep the first valid implementation and delete later duplicates.
    for pos in reversed(positions[1:]):
        end = find_function_end(text, pos)
        if end != -1:
            # Include following blank lines.
            while end < len(text) and text[end] in ' \t\r\n':
                end += 1
            text = text[:pos] + text[end:]

# If the function is still missing, add a safe implementation before loadAppointments.
if sig not in text:
    marker = 'Future<List<dynamic>> loadAppointments({int limit = 5000})'
    pos = text.find(marker)
    if pos == -1:
        raise SystemExit('Could not find loadAppointments insertion point.')
    fn = r'''
Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {
  final resignedIds = await loadResignedEmployeeIdSet();
  final employees = await loadEmployees(limit: limit);
  final rows = employees
      .map((item) => normalizeRow(Map<String, dynamic>.from(item as Map)))
      .where((row) {
    final id = '${row['id'] ?? ''}'.trim();
    return (id.isNotEmpty && resignedIds.contains(id)) || rowHasResignedStatus(row);
  }).toList();
  rows.sort((a, b) => formatValue(a['full_name']).compareTo(formatValue(b['full_name'])));
  return rows;
}

'''
    text = text[:pos] + fn + text[pos:]

path.write_text(text, encoding='utf-8')
print('Repaired orphan loadResignedEmployees function and cleaned duplicate definitions.')
