from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

state_start = text.find('class _CrudTableState')
toolbar_start = text.find('class TableToolbar', state_start)
if state_start == -1 or toolbar_start == -1:
    raise SystemExit('_CrudTableState block was not found.')

state = text[state_start:toolbar_start]

# Ensure the table does not reset to first page when refresh is called after edit/delete/resign.
state = re.sub(
    r"void refresh\(\) => setState\(\(\) \{\s*future = widget\.load\(\);\s*page = 0;\s*\}\);",
    "void refresh() => setState(() {\n        future = widget.load();\n      });",
    state,
    count=1,
    flags=re.S,
)
state = re.sub(
    r"void refresh\(\) => setState\(\(\) => future = widget\.load\(\)\);",
    "void refresh() => setState(() {\n        future = widget.load();\n      });",
    state,
    count=1,
)

# If refresh already exists but still has page = 0 inside it, remove only that reset.
refresh_pos = state.find('void refresh()')
if refresh_pos != -1:
    next_func = state.find('\n\n', refresh_pos + 1)
    if next_func == -1:
        next_func = len(state)
    refresh_block = state[refresh_pos:next_func]
    if 'future = widget.load();' in refresh_block and 'page = 0;' in refresh_block:
        refresh_block = refresh_block.replace('        page = 0;\n', '').replace('    page = 0;\n', '').replace('page = 0;', '')
        state = state[:refresh_pos] + refresh_block + state[next_func:]

text = text[:state_start] + state + text[toolbar_start:]

# Keep current table state by avoiding accidental key changes on Employee CrudTable.
# The gender filter key can remain because changing gender should reset the table; normal edit/delete/resign will not change it.

path.write_text(text, encoding='utf-8')
print('Employee edit/delete/mark-resigned actions will keep the current table page instead of returning to A.')
