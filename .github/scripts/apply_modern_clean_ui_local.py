from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# Safety fix from the previous fast-cache patch: ensure cache helper is only in
# _CrudTableState, not AuthGate or any other State class.
# -----------------------------------------------------------------------------
helper = """  String get cacheKey =>
      widget.key?.toString() ?? widget.reportTitle ?? widget.addLabel;

  Future<List<dynamic>> loadAndCache() async {
    final rows = await widget.load();
    _crudTableDataCache[cacheKey] = rows;
    return rows;
  }

"""
text = text.replace(helper, '')
state_marker = 'class _CrudTableState extends State<CrudTable> {'
state_start = text.find(state_marker)
if state_start >= 0 and helper not in text[text.find(state_marker):text.find('  @override\n  void dispose() {', state_start)]:
    insert_marker = '  @override\n  void dispose() {'
    insert_at = text.find(insert_marker, state_start)
    if insert_at >= 0:
        text = text[:insert_at] + helper + text[insert_at:]

# -----------------------------------------------------------------------------
# Design tokens: cleaner background, softer borders, better radius/shadows.
# -----------------------------------------------------------------------------
text = text.replace('const _accent = Color(0xFF4B5FA7);', 'const _accent = Color(0xFF4F63B6);')
text = text.replace('const _bg = Color(0xFFF8FAFC);', 'const _bg = Color(0xFFF4F7FB);')

if 'const _surface = Color(0xFFFFFFFF);' not in text:
    text = text.replace(
        'const _danger = Color(0xFFDC2626);\n',
        'const _danger = Color(0xFFDC2626);\nconst _surface = Color(0xFFFFFFFF);\nconst _surfaceSoft = Color(0xFFF8FAFC);\nconst _primarySoft = Color(0xFFEFF6FF);\nconst _shadowSoft = Color(0x140F172A);\n',
        1,
    )

# Theme modernization.
text = text.replace('fontFamily: \'Arial\',', 'fontFamily: \'Arial\',\n        visualDensity: VisualDensity.standard,')
text = text.replace(
    '''        cardTheme: CardThemeData(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(22),
              side: const BorderSide(color: _line)),
        ),''',
    '''        cardTheme: CardThemeData(
          elevation: 0,
          color: _surface,
          surfaceTintColor: Colors.transparent,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
              side: const BorderSide(color: _line)),
        ),''',
)
text = text.replace(
    '''            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(999)),''',
    '''            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 17),
            minimumSize: const Size(44, 44),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(18)),''',
)
text = text.replace(
    '''            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(999)),''',
    '''            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            minimumSize: const Size(44, 44),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(18)),''',
)
text = text.replace('fillColor: Colors.white,', 'fillColor: _surface,', 1)
text = text.replace('const EdgeInsets.symmetric(horizontal: 14, vertical: 14)', 'const EdgeInsets.symmetric(horizontal: 16, vertical: 15)', 1)
text = text.replace('BorderRadius.circular(16)', 'BorderRadius.circular(18)', 4)
if 'dialogTheme:' not in text[text.find('theme: ThemeData('):text.find('home: publicClientKey')]:
    text = text.replace(
        '''        inputDecorationTheme: InputDecorationTheme(''',
        '''        dialogTheme: DialogThemeData(
          backgroundColor: _surface,
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(28)),
        ),
        inputDecorationTheme: InputDecorationTheme(''',
        1,
    )

# -----------------------------------------------------------------------------
# Sidebar: cleaner width, separator, spacing, selected state.
# -----------------------------------------------------------------------------
text = text.replace(
    '''    return Container(
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),''',
    '''    return Container(
      width: 252,
      decoration: const BoxDecoration(
        color: _surface,
        border: Border(right: BorderSide(color: _line)),
      ),
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 14),''',
    1,
)
text = text.replace('const VerticalDivider(width: 1, color: _line),', 'const SizedBox.shrink(),', 1)
text = text.replace('const SizedBox(height: 18),\n          Expanded(', 'const SizedBox(height: 24),\n          Expanded(', 1)
text = text.replace('padding: const EdgeInsets.only(bottom: 9),', 'padding: const EdgeInsets.only(bottom: 8),')
text = text.replace('borderRadius: BorderRadius.circular(16),\n          onTap: onTap,', 'borderRadius: BorderRadius.circular(18),\n          onTap: onTap,', 1)
text = text.replace('duration: const Duration(milliseconds: 160),', 'duration: const Duration(milliseconds: 180),')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),', 'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),')
text = text.replace('color: selected ? const Color(0xFFEFF6FF) : Colors.transparent,', 'color: selected ? _primarySoft : Colors.transparent,')
text = text.replace('borderRadius: BorderRadius.circular(16),', 'borderRadius: BorderRadius.circular(18),')
text = text.replace('selected ? const Color(0xFFDBEAFE) : Colors.transparent', 'selected ? const Color(0xFFBFDBFE) : Colors.transparent')

# -----------------------------------------------------------------------------
# Page frame: more balanced spacing and page width rhythm.
# -----------------------------------------------------------------------------
text = text.replace('padding: const EdgeInsets.fromLTRB(28, 18, 28, 18),', 'padding: const EdgeInsets.fromLTRB(32, 24, 32, 24),')
text = text.replace('fontSize: 30,\n                   height: 1.08,', 'fontSize: 31,\n                   height: 1.06,')
text = text.replace('const SizedBox(height: 14),\n          Expanded(child: child),', 'const SizedBox(height: 20),\n          Expanded(child: child),')

# -----------------------------------------------------------------------------
# Table toolbar and table visual polish.
# -----------------------------------------------------------------------------
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),', 'padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),')
text = text.replace('width: compact ? constraints.maxWidth : 360,', 'width: compact ? constraints.maxWidth : 390,')
text = text.replace('fillColor: const Color(0xFFF8FAFC)', 'fillColor: _surfaceSoft')
text = text.replace('width: 188,', 'width: 200,')
text = text.replace('const SizedBox(width: 10), w', 'const SizedBox(width: 12), w')
text = text.replace('spacing: 10,\n                   runSpacing: 10,', 'spacing: 12,\n                   runSpacing: 12,')

text = text.replace('color: const Color(0xFFF8FAFC),\n         padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),', 'color: _surfaceSoft,\n         padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),')
text = text.replace('fontSize: 12.5)))', 'fontSize: 13)))')

text = text.replace('color: index.isEven ? Colors.white : const Color(0xFFFBFDFF),', 'color: index.isEven ? _surface : _surfaceSoft,')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 7),', 'padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),')
text = text.replace('constraints: const BoxConstraints(minHeight: 42),', 'constraints: const BoxConstraints(minHeight: 54),')
text = text.replace('fontSize: 12.5,\n               height: 1.15', 'fontSize: 13,\n               height: 1.25')

# Compact icon buttons in action columns.
text = text.replace('color: Color(0xFF0E7490), size: 20', 'color: Color(0xFF0E7490), size: 19')
text = text.replace('color: _primary, size: 20', 'color: _primary, size: 19')
text = text.replace('color: Color(0xFF16A34A), size: 20', 'color: Color(0xFF16A34A), size: 19')
text = text.replace('color: _danger, size: 20', 'color: _danger, size: 19')

# Pagination footer spacing.
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),')

# Dashboard cards and login card get a touch more breathing room.
text = text.replace('padding: const EdgeInsets.all(28),', 'padding: const EdgeInsets.all(32),')
text = text.replace('const SizedBox(height: 24),\n                      TextField(', 'const SizedBox(height: 28),\n                      TextField(', 1)

# Dialog section titles: give sections better breathing room if present.
text = text.replace('margin: const EdgeInsets.symmetric(vertical: 10),', 'margin: const EdgeInsets.symmetric(vertical: 14),')

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Modern UI patch may already be applied.')
else:
    print('Applied modern clean UI spacing, margins, sidebar, tables, buttons, and dialogs.')
