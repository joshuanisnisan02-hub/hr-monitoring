from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# -----------------------------
# Imports needed by AuthGate
# -----------------------------
if "import 'dart:async';" not in text:
    if "import 'dart:html' as html;" in text:
        text = text.replace("import 'dart:html' as html;", "import 'dart:html' as html;\nimport 'dart:async';", 1)
    else:
        text = "import 'dart:async';\n" + text

# -----------------------------
# AuthGate/Login redirect fix
# -----------------------------
text = text.replace(
    "home: publicClientKey.isEmpty ? const SetupPage() : const ShellPage(),",
    "home: publicClientKey.isEmpty ? const SetupPage() : const AuthGate(),",
)

if 'class AuthGate extends StatefulWidget' not in text:
    marker = 'class SetupPage'
    if marker not in text:
        raise SystemExit('SetupPage marker was not found for AuthGate insertion.')
    auth_code = r'''
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  Session? session;
  StreamSubscription<AuthState>? authSub;

  @override
  void initState() {
    super.initState();
    session = db.auth.currentSession;
    authSub = db.auth.onAuthStateChange.listen((data) {
      if (!mounted) return;
      setState(() => session = data.session);
    });
  }

  @override
  void dispose() {
    authSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => session == null ? const LoginPage() : const ShellPage();
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool loading = false;
  bool obscurePassword = true;

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  Future<void> login() async {
    final email = emailController.text.trim();
    final password = passwordController.text;
    if (email.isEmpty || password.isEmpty) {
      showSnack(context, 'Please enter email and password.');
      return;
    }
    setState(() => loading = true);
    try {
      final result = await db.auth.signInWithPassword(email: email, password: password);
      if (result.session == null && mounted) showSnack(context, 'Login failed. Please check your credentials.');
    } catch (e) {
      if (mounted) showSnack(context, 'Login failed: $e');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: Center(
          child: SizedBox(
            width: 430,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(28),
                child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]),
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: const [BoxShadow(color: Color(0x332563EB), blurRadius: 18, offset: Offset(0, 8))],
                      ),
                      child: const Icon(Icons.school_rounded, color: Colors.white),
                    ),
                  ]),
                  const SizedBox(height: 18),
                  const Text('HR Monitoring', textAlign: TextAlign.center, style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: _ink)),
                  const SizedBox(height: 6),
                  const Text('Sign in to continue', textAlign: TextAlign.center, style: TextStyle(color: _muted, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 24),
                  TextField(
                    controller: emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined)),
                    onSubmitted: (_) => login(),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: passwordController,
                    obscureText: obscurePassword,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.lock_outline_rounded),
                      suffixIcon: IconButton(
                        onPressed: () => setState(() => obscurePassword = !obscurePassword),
                        icon: Icon(obscurePassword ? Icons.visibility_rounded : Icons.visibility_off_rounded),
                      ),
                    ),
                    onSubmitted: (_) => login(),
                  ),
                  const SizedBox(height: 22),
                  FilledButton.icon(
                    onPressed: loading ? null : login,
                    icon: loading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.login_rounded),
                    label: Text(loading ? 'Signing in...' : 'Login'),
                  ),
                ]),
              ),
            ),
          ),
        ),
      );
}

'''
    text = text.replace(marker, auth_code + marker, 1)

# Keep logout on AuthGate instead of hard reload to dashboard.
if 'Future<void> logoutUser(BuildContext context)' in text:
    start = text.find('Future<void> logoutUser(BuildContext context)')
    brace = text.find('{', start)
    depth = 0
    end = -1
    for i in range(brace, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    logout_code = r'''Future<void> logoutUser(BuildContext context) async {
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Log out?'),
      content: const Text('You will need to log in again to continue.'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
        FilledButton.icon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.logout_rounded),
          label: const Text('Logout'),
        ),
      ],
    ),
  );
  if (ok != true) return;
  try { await db.auth.signOut(); } catch (_) {}
  try { html.window.sessionStorage.clear(); } catch (_) {}
  try { html.window.localStorage.remove('supabase.auth.token'); } catch (_) {}
}'''
    if end != -1:
        text = text[:start] + logout_code + text[end:]

# -----------------------------
# CrudTable extension patches
# -----------------------------
crud_start = text.find('class CrudTable')
state_start = text.find('class _CrudTableState', crud_start)
toolbar_start = text.find('class TableToolbar', state_start)
if crud_start == -1 or state_start == -1 or toolbar_start == -1:
    raise SystemExit('CrudTable blocks were not found.')

crud = text[crud_start:state_start]
state = text[state_start:toolbar_start]

# Add CrudTable fields and constructor parameters if missing.
if 'final String initialSearch;' not in crud:
    crud = crud.replace('final String searchHint;', 'final String searchHint;\n  final String initialSearch;', 1)
if 'final List<int> pageSizeOptions;' not in crud:
    insert = '  final List<int> pageSizeOptions;\n  final int initialPageSize;\n'
    if 'final Future<dynamic> Function(Map<String, dynamic> row) onDelete;' in crud:
        crud = crud.replace('final Future<dynamic> Function(Map<String, dynamic> row) onDelete;', insert + '  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;', 1)
    elif 'final String? reportTitle;' in crud:
        crud = crud.replace('final String? reportTitle;', 'final String? reportTitle;\n' + insert, 1)

if 'this.initialSearch' not in crud:
    crud = crud.replace('required this.searchHint,', "required this.searchHint,\n    this.initialSearch = '',", 1)
if 'this.pageSizeOptions' not in crud:
    crud = crud.replace('required this.onDelete,', "this.pageSizeOptions = const [10],\n    this.initialPageSize = 10,\n    required this.onDelete,", 1)

text = text[:crud_start] + crud + text[state_start:]
state_start = text.find('class _CrudTableState')
toolbar_start = text.find('class TableToolbar', state_start)
state = text[state_start:toolbar_start]

# Add scroll controllers and page size state.
if 'final ScrollController tableScrollController' not in state:
    state = state.replace("String query = '';", "String query = '';\n  final ScrollController tableScrollController = ScrollController();\n  final ScrollController crudOuterScrollController = ScrollController();", 1)
elif 'final ScrollController crudOuterScrollController' not in state:
    state = state.replace('final ScrollController tableScrollController = ScrollController();', 'final ScrollController tableScrollController = ScrollController();\n  final ScrollController crudOuterScrollController = ScrollController();', 1)

if 'int pageSize = _pageSize;' not in state and 'int pageSize =' not in state:
    state = state.replace('  int page = 0;\n', '  int page = 0;\n  int pageSize = _pageSize;\n', 1)

if 'query = widget.initialSearch;' not in state:
    state = state.replace('    super.initState();\n', '    super.initState();\n    query = widget.initialSearch;\n', 1)
if 'pageSize = options.contains(widget.initialPageSize)' not in state and 'widget.pageSizeOptions.contains(widget.initialPageSize)' not in state:
    state = state.replace('    future = widget.load();\n', "    final options = widget.pageSizeOptions.isEmpty ? const [10] : widget.pageSizeOptions;\n    pageSize = options.contains(widget.initialPageSize) ? widget.initialPageSize : options.first;\n    future = widget.load();\n", 1)

# Dispose controllers.
if 'crudOuterScrollController.dispose();' not in state:
    if 'tableScrollController.dispose();' in state:
        state = state.replace('tableScrollController.dispose();', 'tableScrollController.dispose();\n    crudOuterScrollController.dispose();', 1)
    else:
        pos = state.find('  @override\n  void initState()')
        state = state[:pos] + "  @override\n  void dispose() {\n    tableScrollController.dispose();\n    crudOuterScrollController.dispose();\n    super.dispose();\n  }\n\n" + state[pos:]

# Refresh must not reset page/scroll.
state = re.sub(r"void refresh\(\) => setState\(\(\) \{\s*future = widget\.load\(\);\s*page = 0;\s*\}\);", "void refresh() => setState(() {\n        future = widget.load();\n      });", state, flags=re.S)
refresh_pos = state.find('void refresh()')
if refresh_pos != -1:
    refresh_end = state.find('\n\n', refresh_pos)
    if refresh_end != -1:
        block = state[refresh_pos:refresh_end].replace('        page = 0;\n', '').replace('    page = 0;\n', '').replace('page = 0;', '')
        state = state[:refresh_pos] + block + state[refresh_end:]

# Helpers for pagination scroll top.
if 'void scrollBothToTop()' not in state:
    marker = '  double get actionWidth {'
    helpers = r'''  void scrollBothToTop() {
    if (!mounted) return;
    if (tableScrollController.hasClients) tableScrollController.jumpTo(0);
    if (crudOuterScrollController.hasClients) crudOuterScrollController.jumpTo(0);
  }

  void goToTablePage(int nextPage) {
    setState(() => page = nextPage);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      scrollBothToTop();
      WidgetsBinding.instance.addPostFrameCallback((_) => scrollBothToTop());
    });
  }

'''
    if marker not in state:
        raise SystemExit('actionWidth marker was not found.')
    state = state.replace(marker, helpers + marker, 1)
elif 'void goToTablePage(int nextPage)' not in state:
    marker = '  double get actionWidth {'
    go = "  void goToTablePage(int nextPage) {\n    setState(() => page = nextPage);\n    WidgetsBinding.instance.addPostFrameCallback((_) {\n      scrollBothToTop();\n      WidgetsBinding.instance.addPostFrameCallback((_) => scrollBothToTop());\n    });\n  }\n\n"
    state = state.replace(marker, go + marker, 1)

# Dynamic page size in calculations.
state = state.replace('~/ _pageSize', '~/ pageSize')
state = state.replace('* _pageSize', '* pageSize')
state = state.replace('take(_pageSize)', 'take(pageSize)')

# Add Display Names dropdown if missing.
if "labelText: 'Display Names'" not in state:
    marker = '            const SizedBox(height: 14),\n            Expanded(child:'
    if marker not in state:
        marker = '            Expanded(child:'
        insert = r'''            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 220,
                  child: DropdownButtonFormField<int>(
                    value: pageSize,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Display Names'),
                    items: widget.pageSizeOptions.map((value) => DropdownMenuItem<int>(value: value, child: Text('$value per page'))).toList(),
                    onChanged: (value) => setState(() {
                      pageSize = value ?? pageSize;
                      page = 0;
                      WidgetsBinding.instance.addPostFrameCallback((_) => scrollBothToTop());
                    }),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),
'''
        state = state.replace(marker, insert + marker, 1)
    else:
        insert = r'''            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 220,
                  child: DropdownButtonFormField<int>(
                    value: pageSize,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Display Names'),
                    items: widget.pageSizeOptions.map((value) => DropdownMenuItem<int>(value: value, child: Text('$value per page'))).toList(),
                    onChanged: (value) => setState(() {
                      pageSize = value ?? pageSize;
                      page = 0;
                      WidgetsBinding.instance.addPostFrameCallback((_) => scrollBothToTop());
                    }),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),
            Expanded(child:'''
        state = state.replace(marker, insert, 1)

# Ensure pagination uses helper.
state = re.sub(r'onPrevious:\s*safePage > 0 \? \(\) => setState\(\(\) => page = safePage - 1\) : null,', 'onPrevious: safePage > 0 ? () => goToTablePage(safePage - 1) : null,', state)
state = re.sub(r'onNext:\s*safePage < pageCount - 1 \? \(\) => setState\(\(\) => page = safePage \+ 1\) : null,', 'onNext: safePage < pageCount - 1 ? () => goToTablePage(safePage + 1) : null,', state)
state = state.replace('onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null,', 'onPrevious: safePage > 0 ? () => goToTablePage(safePage - 1) : null,')
state = state.replace('onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null,', 'onNext: safePage < pageCount - 1 ? () => goToTablePage(safePage + 1) : null,')

# Inner list controller.
if 'controller: tableScrollController' not in state:
    state = state.replace('ListView.separated(', 'ListView.separated(\n                controller: tableScrollController,', 1)

# Wrap return tableContent with taller scrollable area if not already using crudOuterScrollController.
if 'controller: crudOuterScrollController' not in state:
    state = state.replace('return tableContent;', "return LayoutBuilder(\n            builder: (context, constraints) {\n              final availableHeight = constraints.maxHeight.isFinite ? constraints.maxHeight : 0.0;\n              final tableHeight = availableHeight < 820 ? 820.0 : availableHeight;\n              return SingleChildScrollView(\n                controller: crudOuterScrollController,\n                child: SizedBox(height: tableHeight, child: tableContent),\n              );\n            },\n          );", 1)
    state = state.replace('return SingleChildScrollView(\n                child:', 'return SingleChildScrollView(\n                controller: crudOuterScrollController,\n                child:')
    state = state.replace('return SingleChildScrollView(\n                  child:', 'return SingleChildScrollView(\n                  controller: crudOuterScrollController,\n                  child:')

text = text[:state_start] + state + text[toolbar_start:]

# Compact row/header so more employees are visible.
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),')
text = text.replace('constraints: const BoxConstraints(minHeight: 62),', 'constraints: const BoxConstraints(minHeight: 50),')
text = text.replace('padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),', 'padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),')

# -----------------------------
# Employees module settings
# -----------------------------
emp_start = text.find('class EmployeesPage')
emp_end = text.find('class ContractsPage', emp_start)
if emp_start != -1 and emp_end != -1:
    emp = text[emp_start:emp_end]
    if 'pageSizeOptions: const [1, 10, 100]' not in emp:
        m = re.search(r'CrudTable\s*\(', emp)
        if m:
            emp = emp[:m.end()] + "\n              pageSizeOptions: const [1, 10, 100],\n              initialPageSize: 10," + emp[m.end():]
    if "status.contains('resign')" not in emp:
        pos = emp.find('bool matchesGenderFilter(Map<String, dynamic> row)')
        if pos != -1:
            brace = emp.find('{', pos)
            emp = emp[:brace+1] + "\n    final status = formatValue(row['employment_status']).toLowerCase();\n    if (status.contains('resign')) return false;" + emp[brace+1:]
        elif '.where(matchesGenderFilter).toList()' in emp:
            emp = emp.replace('.where(matchesGenderFilter).toList()', ".where((row) => !formatValue(row['employment_status']).toLowerCase().contains('resign')).where(matchesGenderFilter).toList()", 1)
    text = text[:emp_start] + emp + text[emp_end:]

path.write_text(text, encoding='utf-8')
print('Final chat fixes applied: AuthGate logout/login, employee display count, table height, scroll behavior, and resigned filtering.')
