from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# Ensure dart:html is available for reload/session clearing.
if "import 'dart:html' as html;" not in text:
    text = "// ignore: avoid_web_libraries_in_flutter\nimport 'dart:html' as html;\n" + text

logout_function = r'''
Future<void> logoutUser(BuildContext context) async {
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
  try {
    await db.auth.signOut();
  } catch (_) {}
  try {
    html.window.sessionStorage.clear();
  } catch (_) {}
  try {
    html.window.localStorage.remove('supabase.auth.token');
  } catch (_) {}
  html.window.location.reload();
}

'''

if 'Future<void> logoutUser(BuildContext context)' not in text:
    marker = 'class AppSidebar extends StatelessWidget {'
    if marker not in text:
        raise SystemExit('AppSidebar marker was not found.')
    text = text.replace(marker, logout_function + marker, 1)

# Put logout in the top HR Monitoring row so it is always visible.
sidebar_start = text.find('class AppSidebar extends StatelessWidget')
sidebar_end = text.find('class SidebarItem', sidebar_start)
if sidebar_start == -1 or sidebar_end == -1:
    raise SystemExit('AppSidebar block was not found.')
sidebar = text[sidebar_start:sidebar_end]

if "tooltip: 'Logout'" not in sidebar and "tooltip: 'Log out'" not in sidebar:
    old = "const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),"
    new = """const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
          IconButton(
            tooltip: 'Logout',
            onPressed: () => logoutUser(context),
            icon: const Icon(Icons.logout_rounded, color: _danger),
          ),"""
    if old in sidebar:
        sidebar = sidebar.replace(old, new, 1)
    else:
        # More flexible fallback: insert before the first closing bracket of the top Row.
        title_pos = sidebar.find("HR Monitoring")
        if title_pos == -1:
            raise SystemExit('Could not find HR Monitoring title in sidebar.')
        row_start = sidebar.rfind('Row(children: [', 0, title_pos)
        if row_start == -1:
            raise SystemExit('Could not find sidebar header Row.')
        insert_after = sidebar.find(']),', title_pos)
        if insert_after == -1:
            raise SystemExit('Could not find end of sidebar header Row.')
        sidebar = sidebar[:insert_after] + """
          IconButton(
            tooltip: 'Logout',
            onPressed: () => logoutUser(context),
            icon: const Icon(Icons.logout_rounded, color: _danger),
          ),
""" + sidebar[insert_after:]

text = text[:sidebar_start] + sidebar + text[sidebar_end:]
path.write_text(text, encoding='utf-8')
print('Visible sidebar logout button added beside HR Monitoring title.')
