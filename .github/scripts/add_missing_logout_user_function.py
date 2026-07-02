from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

if "import 'dart:html' as html;" not in text:
    # Add html import near the top; this app already uses Flutter web.
    if "import 'dart:async';" in text:
        text = text.replace("import 'dart:async';", "import 'dart:async';\nimport 'dart:html' as html;", 1)
    else:
        text = "import 'dart:html' as html;\n" + text

logout_code = r'''
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
}

'''

if 'Future<void> logoutUser(BuildContext context)' not in text:
    marker = 'class AppSidebar extends StatelessWidget'
    if marker not in text:
        marker = 'class ShellPage'
    if marker not in text:
        raise SystemExit('Could not find a safe place to insert logoutUser.')
    text = text.replace(marker, logout_code + marker, 1)

path.write_text(text, encoding='utf-8')
print('Added missing logoutUser function.')
