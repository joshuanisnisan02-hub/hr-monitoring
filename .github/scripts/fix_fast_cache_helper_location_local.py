from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

helper = """  String get cacheKey =>
      widget.key?.toString() ?? widget.reportTitle ?? widget.addLabel;

  Future<List<dynamic>> loadAndCache() async {
    final rows = await widget.load();
    _crudTableDataCache[cacheKey] = rows;
    return rows;
  }

"""

# Remove helper from the wrong class/location and from any duplicate location.
removed = text.count(helper)
text = text.replace(helper, '')

# Insert helper inside _CrudTableState only.
state_marker = 'class _CrudTableState extends State<CrudTable> {'
state_start = text.find(state_marker)
if state_start < 0:
    raise SystemExit('Could not find _CrudTableState.')
insert_marker = '  @override\n  void dispose() {'
insert_at = text.find(insert_marker, state_start)
if insert_at < 0:
    raise SystemExit('Could not find dispose marker inside _CrudTableState.')
text = text[:insert_at] + helper + text[insert_at:]

# Ensure the global cache exists exactly near safeRefresh.
if 'final Map<String, List<dynamic>> _crudTableDataCache' not in text:
    safe_marker = 'void safeRefresh(VoidCallback refresh) {\n  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());\n}\n'
    if safe_marker not in text:
        raise SystemExit('Could not find safeRefresh marker for global cache.')
    text = text.replace(
        safe_marker,
        safe_marker + '\nfinal Map<String, List<dynamic>> _crudTableDataCache = <String, List<dynamic>>{};\n',
        1,
    )

# Ensure init and refresh use cache loader only in _CrudTableState.
text = text.replace('    future = widget.load();\n', '    future = loadAndCache();\n', 1)
text = text.replace('        future = widget.load();\n', '        future = loadAndCache();\n', 1)

path.write_text(text, encoding='utf-8')
print(f'Moved table cache helper into _CrudTableState. Removed {removed} previous helper block(s), inserted 1 correct block.')
