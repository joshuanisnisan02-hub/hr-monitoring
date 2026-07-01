from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

state_start = text.find('class _CrudTableState')
toolbar_start = text.find('class TableToolbar', state_start)
if state_start == -1 or toolbar_start == -1:
    raise SystemExit('_CrudTableState block was not found.')
state = text[state_start:toolbar_start]

# Ensure table scroll controller exists.
if 'final ScrollController tableScrollController' not in state:
    if "String query = '';" in state:
        state = state.replace("String query = '';", "String query = '';\n  final ScrollController tableScrollController = ScrollController();", 1)
    else:
        raise SystemExit('CrudTable query field was not found.')

# Ensure dispose exists.
if 'tableScrollController.dispose();' not in state:
    init_pos = state.find('  @override\n  void initState()')
    if init_pos == -1:
        raise SystemExit('CrudTable initState was not found.')
    dispose_block = r'''  @override
  void dispose() {
    tableScrollController.dispose();
    super.dispose();
  }

'''
    state = state[:init_pos] + dispose_block + state[init_pos:]

# Add helper to change page and scroll to top of that page.
if 'void goToTablePage(int nextPage)' not in state:
    marker = '  void printRows(List<Map<String, dynamic>> rows) {'
    if marker not in state:
        raise SystemExit('printRows marker was not found.')
    helper = r'''  void goToTablePage(int nextPage) {
    setState(() => page = nextPage);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || !tableScrollController.hasClients) return;
      tableScrollController.jumpTo(0);
    });
  }

'''
    state = state.replace(marker, helper + marker, 1)

# Attach controller to table list if missing.
if 'controller: tableScrollController' not in state:
    list_pos = state.find('ListView.separated(')
    if list_pos == -1:
        raise SystemExit('Table ListView.separated was not found.')
    insert_at = list_pos + len('ListView.separated(')
    state = state[:insert_at] + '\n                controller: tableScrollController,' + state[insert_at:]

# Replace pagination setState with helper.
state = re.sub(
    r'onPrevious:\s*safePage > 0 \? \(\) => setState\(\(\) => page = safePage - 1\) : null,',
    'onPrevious: safePage > 0 ? () => goToTablePage(safePage - 1) : null,',
    state,
    count=1,
)
state = re.sub(
    r'onNext:\s*safePage < pageCount - 1 \? \(\) => setState\(\(\) => page = safePage \+ 1\) : null,',
    'onNext: safePage < pageCount - 1 ? () => goToTablePage(safePage + 1) : null,',
    state,
    count=1,
)

# Handle multiline variants.
state = state.replace('onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null,', 'onPrevious: safePage > 0 ? () => goToTablePage(safePage - 1) : null,')
state = state.replace('onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null,', 'onNext: safePage < pageCount - 1 ? () => goToTablePage(safePage + 1) : null,')

text = text[:state_start] + state + text[toolbar_start:]
path.write_text(text, encoding='utf-8')
print('Next/Previous now scrolls to the top of the selected table page.')
