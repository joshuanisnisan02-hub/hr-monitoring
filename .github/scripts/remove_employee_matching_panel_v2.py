from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')
needle = 'Excel Employee Matching'
pos = text.find(needle)
if pos == -1:
    print('Employee matching panel already removed.')
    raise SystemExit(0)

string_quote = None
escape = False

def find_block_end(start):
    depth_paren = 0
    depth_bracket = 0
    quote = None
    esc = False
    i = start
    while i < len(text):
        ch = text[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch == '"' or ch == "'":
                quote = ch
            elif ch == '(':
                depth_paren += 1
            elif ch == ')':
                depth_paren -= 1
            elif ch == '[':
                depth_bracket += 1
            elif ch == ']':
                depth_bracket -= 1
            elif ch == ',' and depth_paren <= 0 and depth_bracket <= 0:
                return i + 1
        i += 1
    return -1

# Try enclosing widgets from nearest to farthest, but only accept a block that
# contains the title and one of the panel actions/texts.
candidates = []
for token in ['Card(', 'Container(', 'Padding(', 'SizedBox(', 'Row(', 'Column(']:
    search_from = pos
    while True:
        idx = text.rfind(token, 0, search_from)
        if idx == -1:
            break
        end = find_block_end(idx)
        if end != -1:
            block = text[idx:end]
            if needle in block and ('Import Employee Info' in block or 'Fix Names' in block or 'tbl_employee CSV' in block):
                line_start = text.rfind('\n', 0, idx) + 1
                candidates.append((line_start, end, token, len(block)))
        search_from = idx

if not candidates:
    raise SystemExit('Could not safely locate the Employee Matching panel block. Please send the EmployeesPage section for manual patching.')

# Prefer a large outer block so the whole panel disappears, not just a text row.
candidates.sort(key=lambda x: (-x[3], x[0]))
start, end, token, _ = candidates[0]
removed = text[start:end]
if needle not in removed:
    raise SystemExit('Safety check failed: chosen block does not contain the Employee Matching title.')

# Remove immediate vertical spacing after the panel.
for spacing in [
    '\n          const SizedBox(height: 24),',
    '\n          const SizedBox(height: 22),',
    '\n          const SizedBox(height: 20),',
    '\n          const SizedBox(height: 18),',
    '\n          const SizedBox(height: 16),',
    '\n          const SizedBox(height: 14),',
    '\n        const SizedBox(height: 24),',
    '\n        const SizedBox(height: 22),',
    '\n        const SizedBox(height: 20),',
    '\n        const SizedBox(height: 18),',
    '\n        const SizedBox(height: 16),',
    '\n        const SizedBox(height: 14),',
]:
    if text[end:].startswith(spacing):
        end += len(spacing)
        break

text = text[:start] + text[end:]
path.write_text(text, encoding='utf-8')
print(f'Employee matching panel removed using {token} block.')
