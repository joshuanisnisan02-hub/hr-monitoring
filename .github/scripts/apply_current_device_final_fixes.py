from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / 'lib' / 'main.dart'
SCRIPTS = ROOT / '.github' / 'scripts'

# Apply the scripts from this chat in the correct order.
# Missing scripts are skipped so this can run safely on any device.
ordered_scripts = [
    'fix_reports_resigned_pages_and_employee_filter.py',
    'restore_live_employee_view_keep_display_names.py',
    'remove_employee_matching_make_table_taller.py',
    'show_minimum_five_table_rows.py',
    'repair_named_parameter_colon_damage.py',
    'move_resigned_to_resigned_module_only.py',
]

for script_name in ordered_scripts:
    script_path = SCRIPTS / script_name
    if script_path.exists():
        print(f'Running {script_name}...')
        runpy.run_path(str(script_path), run_name='__main__')
    else:
        print(f'Skipping missing {script_name}.')

text = MAIN.read_text(encoding='utf-8')

# Repair any exact orphan function header left by older scripts.
lines = text.splitlines()
for i, line in enumerate(lines):
    if line.strip() == ') async {':
        lines[i] = 'Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {'
        print(f'Fixed orphan loadResignedEmployees header at line {i + 1}.')
        break
text = '\n'.join(lines) + '\n'

# Repair named-parameter damage from older scripts.
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

signature = 'Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {'

def find_function_end(src, start):
    brace = src.find('{', start)
    if brace < 0:
        return -1
    depth = 0
    quote = None
    escape = False
    for idx in range(brace, len(src)):
        ch = src[idx]
        if quote is not None:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
            continue
        if ch == '"' or ch == "'":
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return idx + 1
    return -1

positions = []
start = 0
while True:
    pos = text.find(signature, start)
    if pos < 0:
        break
    positions.append(pos)
    start = pos + len(signature)

print(f'Found {len(positions)} loadResignedEmployees definitions.')

# Keep the first definition and delete every duplicate after it.
for pos in reversed(positions[1:]):
    end = find_function_end(text, pos)
    if end < 0:
        raise SystemExit('Could not locate duplicate loadResignedEmployees end.')
    while end < len(text) and text[end] in ' \t\r\n':
        end += 1
    text = text[:pos] + text[end:]
    print('Removed duplicate loadResignedEmployees definition.')

MAIN.write_text(text, encoding='utf-8')
print('Final current-device fixes applied. Run dart format lib/main.dart next.')
