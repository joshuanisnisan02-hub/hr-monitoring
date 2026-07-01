from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

needle = 'Excel Employee Matching'
pos = text.find(needle)
if pos == -1:
    print('Employee matching panel already removed.')
    raise SystemExit(0)

# Find the nearest widget statement before the title. This panel has been changed several
# times, so remove the whole preceding widget expression that contains the title.
line_start = text.rfind('\n', 0, pos) + 1
start_candidates = []
for token in ['Card(', 'Container(', 'Padding(', 'SizedBox(']:
    idx = text.rfind(token, 0, pos)
    if idx != -1:
        start_candidates.append(idx)
if not start_candidates:
    raise SystemExit('Could not locate the start of the Employee Matching panel.')
start = min(start_candidates)

# Move to the beginning of the line containing the widget.
start = text.rfind('\n', 0, start) + 1

# Balance parentheses/brackets from start until the widget statement ends with a comma.
depth_paren = 0
depth_bracket = 0
in_string = None
escape = False
end = None
i = start
while i < len(text):
    ch = text[i]
    if in_string:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == in_string:
            in_string = None
    else:
        if ch in ['"', "'"]:
            # Handle Dart triple strings lightly by treating as normal strings; panels do not use them.
            in_string = ch
        elif ch == '(':
            depth_paren += 1
        elif ch == ')':
            depth_paren -= 1
        elif ch == '[':
            depth_bracket += 1
        elif ch == ']':
            depth_bracket -= 1
        elif ch == ',' and depth_paren <= 0 and depth_bracket <= 0:
            end = i + 1
            break
    i += 1

if end is None:
    raise SystemExit('Could not locate the end of the Employee Matching panel.')

# Also remove a following SizedBox spacing if present.
rest = text[end:]
for spacing in [
    "\n          const SizedBox(height: 16),",
    "\n          const SizedBox(height: 18),",
    "\n          const SizedBox(height: 20),",
    "\n          const SizedBox(height: 22),",
    "\n          const SizedBox(height: 24),",
    "\n        const SizedBox(height: 16),",
    "\n        const SizedBox(height: 18),",
    "\n        const SizedBox(height: 20),",
    "\n        const SizedBox(height: 22),",
    "\n        const SizedBox(height: 24),",
]:
    if rest.startswith(spacing):
        end += len(spacing)
        break

removed = text[start:end]
if needle not in removed:
    raise SystemExit('Safety check failed: selected block does not contain Employee Matching title.')

text = text[:start] + text[end:]
path.write_text(text, encoding='utf-8')
print('Employee matching panel removed from Employees module.')
