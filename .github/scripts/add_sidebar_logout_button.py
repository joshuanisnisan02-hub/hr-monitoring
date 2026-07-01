from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

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
          label: const Text('Log Out'),
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

if "label: const Text('Logout')" not in text and "label: const Text('Log Out')" not in text:
    sidebar_start = text.find('class AppSidebar extends StatelessWidget')
    sidebar_end = text.find('class SidebarItem', sidebar_start)
    if sidebar_start == -1 or sidebar_end == -1:
        raise SystemExit('AppSidebar block was not found.')
    block = text[sidebar_start:sidebar_end]

    logout_button = r'''
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () => logoutUser(context),
            icon: const Icon(Icons.logout_rounded),
            label: const Text('Logout'),
          ),
        ),
        const SizedBox(height: 10),
'''

    if 'const Spacer(),' in block:
        block = block.replace('const Spacer(),', 'const Spacer(),\n' + logout_button, 1)
    else:
        # If the sidebar has already been made scrollable and no Spacer exists, put it before the bottom HR note.
        note_pos = block.find("Container(", block.rfind('child: Column'))
        if note_pos == -1:
            raise SystemExit('Could not find sidebar insertion point for logout button.')
        line_start = block.rfind('\n', 0, note_pos) + 1
        block = block[:line_start] + logout_button + block[line_start:]

    text = text[:sidebar_start] + block + text[sidebar_end:]

path.write_text(text, encoding='utf-8')
print('Sidebar Logout button added to lib/main.dart')
