from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# -----------------------------------------------------------------------------
# 1) Keep visited modules mounted so returning to a module/tab is instant and its
#    table state/future is not recreated every click.
# -----------------------------------------------------------------------------
old_shell = r'''class _ShellPageState extends State<ShellPage> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardPage(onNavigate: (i) => setState(() => index = i)),
      const EmployeesPage(),
      const ContractsPage(),
      const CredentialsPage(),
      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
      const ReportsPage(),
      const ResignedEmployeesPage(),
    ];
    final safeIndex = index.clamp(0, pages.length - 1).toInt();
    return Scaffold(
      body: Row(children: [
        AppSidebar(
            selectedIndex: index, onChanged: (i) => setState(() => index = i)),
        const VerticalDivider(width: 1, color: _line),
        Expanded(child: pages[safeIndex]),
      ]),
    );
  }
}
'''
new_shell = r'''class _ShellPageState extends State<ShellPage> {
  int index = 0;
  final Set<int> visitedPages = {0};

  void selectPage(int nextIndex) {
    setState(() {
      index = nextIndex;
      visitedPages.add(nextIndex);
    });
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardPage(onNavigate: selectPage),
      const EmployeesPage(),
      const ContractsPage(),
      const CredentialsPage(),
      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
      const ReportsPage(),
      const ResignedEmployeesPage(),
    ];
    final safeIndex = index.clamp(0, pages.length - 1).toInt();
    visitedPages.add(safeIndex);
    return Scaffold(
      body: Row(children: [
        AppSidebar(selectedIndex: safeIndex, onChanged: selectPage),
        const VerticalDivider(width: 1, color: _line),
        Expanded(
          child: IndexedStack(
            index: safeIndex,
            children: [
              for (var i = 0; i < pages.length; i++)
                visitedPages.contains(i) ? pages[i] : const SizedBox.shrink(),
            ],
          ),
        ),
      ]),
    );
  }
}
'''
if old_shell in text:
    text = text.replace(old_shell, new_shell, 1)
elif 'final Set<int> visitedPages' not in text:
    print('Warning: ShellPage block did not match exactly; skip IndexedStack patch.')

# -----------------------------------------------------------------------------
# 2) Add a simple in-memory table data cache. When the user returns to a module,
#    the cached rows render immediately while the latest Supabase refresh runs.
# -----------------------------------------------------------------------------
if 'final Map<String, List<dynamic>> _crudTableDataCache' not in text:
    text = text.replace(
        'void safeRefresh(VoidCallback refresh) {\n  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());\n}\n',
        'void safeRefresh(VoidCallback refresh) {\n  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());\n}\n\nfinal Map<String, List<dynamic>> _crudTableDataCache = <String, List<dynamic>>{};\n',
        1,
    )

# Add cache helpers in _CrudTableState.
if 'String get cacheKey' not in text:
    marker = '  @override\n  void dispose() {'
    helper = r'''
  String get cacheKey =>
      widget.key?.toString() ?? widget.reportTitle ?? widget.addLabel;

  Future<List<dynamic>> loadAndCache() async {
    final rows = await widget.load();
    _crudTableDataCache[cacheKey] = rows;
    return rows;
  }

'''
    if marker in text:
        text = text.replace(marker, helper + marker, 1)
    else:
        print('Warning: Could not insert CrudTable cache helpers.')

text = text.replace('    future = widget.load();\n', '    future = loadAndCache();\n', 1)
text = text.replace('        future = widget.load();\n', '        future = loadAndCache();\n', 1)

# Make FutureBuilder use cached initialData and render cached rows while refreshing.
text = text.replace(
    '  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(\n        future: future,\n        builder: (context, snap) {\n          if (snap.connectionState != ConnectionState.done)\n            return const Center(child: CircularProgressIndicator());\n          if (snap.hasError) return ErrorBox(\'${snap.error}\');',
    '  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(\n        future: future,\n        initialData: _crudTableDataCache[cacheKey],\n        builder: (context, snap) {\n          final hasUsableData = snap.data != null;\n          if (snap.connectionState != ConnectionState.done && !hasUsableData) {\n            return const Center(child: CircularProgressIndicator());\n          }\n          if (snap.hasError && !hasUsableData) return ErrorBox(\'${snap.error}\');',
    1,
)

path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. Fast module navigation/cache may already be applied.')
else:
    print('Applied fast module navigation and table cache. Visited modules stay mounted and cached rows show instantly while refreshing.')
