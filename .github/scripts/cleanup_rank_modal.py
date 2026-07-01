from pathlib import Path
p = Path('lib/main.dart')
s = p.read_text()
s = s.replace('  bool actionInProgress = false;\n  bool actionInProgress = false;\n', '  bool actionInProgress = false;\n')
s = s.replace('  bool submitting = false;\n  bool submitting = false;\n', '  bool submitting = false;\n')
needle = '  Future<void> runAction(Future<void> Function() action) async {'
first = s.find(needle)
second = s.find(needle, first + 1) if first >= 0 else -1
if first >= 0 and second >= 0:
    end = s.find('\n\n  double get actionWidth', second)
    if end >= 0:
        s = s[:second] + s[end + 2:]
p.write_text(s)
