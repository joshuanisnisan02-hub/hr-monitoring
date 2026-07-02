from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8')
original = text


def matching_brace(s, open_i):
    depth = 0
    for i in range(open_i, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    raise SystemExit('Could not find matching closing brace in lib/main.dart.')


def line_end(s, i):
    if i < len(s) and s[i:i + 2] == '\r\n':
        return i + 2
    if i < len(s) and s[i] == '\n':
        return i + 1
    return i

# Remove orphaned blocks like this, caused by the old repair script:
# ) async {
#   final resignedIds = await loadResignedEmployeeIdSet();
#   final employees = await loadEmployees(limit: limit);
#   ...
# }
orphan_count = 0
for m in reversed(list(re.finditer(r'(?m)^\s*\)\s*async\s*\{\s*\n', text))):
    preview = text[m.start():m.start() + 800]
    if 'loadResignedEmployeeIdSet' not in preview or 'loadEmployees(limit: limit)' not in preview:
        continue
    open_i = text.find('{', m.start(), m.end())
    close_i = matching_brace(text, open_i)
    end_i = line_end(text, close_i + 1)
    text = text[:m.start()] + text[end_i:]
    orphan_count += 1

# Remove duplicate full loadResignedEmployees definitions. Keep the first complete one.
blocks = []
for m in re.finditer(r'(?m)^\s*Future<[^\n]*>\s+loadResignedEmployees\s*\(', text):
    open_i = text.find('{', m.end())
    if open_i == -1:
        continue
    close_i = matching_brace(text, open_i)
    blocks.append((m.start(), line_end(text, close_i + 1)))

duplicate_count = 0
for start, end in reversed(blocks[1:]):
    text = text[:start] + text[end:]
    duplicate_count += 1

if text != original:
    path.write_text(text, encoding='utf-8')

print(f'Found {len(blocks)} loadResignedEmployees definitions.')
print(f'Removed {duplicate_count} duplicate loadResignedEmployees definition(s).')
print(f'Removed {orphan_count} orphaned async block(s).')
print('Duplicate repair complete.')
