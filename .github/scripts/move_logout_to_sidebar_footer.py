from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# Ensure logout function exists.
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

sidebar_start = text.find('class AppSidebar extends StatelessWidget')
sidebar_end = text.find('class SidebarItem', sidebar_start)
if sidebar_start == -1 or sidebar_end == -1:
    raise SystemExit('AppSidebar block was not found.')
sidebar = text[sidebar_start:sidebar_end]

# Remove the top red logout icon previously inserted beside HR Monitoring.
def remove_icon_button_with_tooltip(block: str, tooltip: str) -> str:
    pos = block.find(tooltip)
    while pos != -1:
        start = block.rfind('IconButton(', 0, pos)
        if start == -1:
            break
        line_start = block.rfind('\n', 0, start) + 1
        depth = 0
        quote = None
        escape = False
        end = -1
        i = start
        while i < len(block):
            ch = block[i]
            if quote:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == quote:
                    quote = None
            else:
                if ch == '"' or ch == "'":
                    quote = ch
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        if end < len(block) and block[end] == ',':
                            end += 1
                        break
            i += 1
        if end == -1:
            break
        block = block[:line_start] + block[end:]
        pos = block.find(tooltip)
    return block

sidebar = remove_icon_button_with_tooltip(sidebar, "tooltip: 'Logout'")
sidebar = remove_icon_button_with_tooltip(sidebar, "tooltip: 'Log out'")

logout_footer = r'''SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: () => logoutUser(context),
            icon: const Icon(Icons.logout_rounded),
            label: const Text('Logout'),
          ),
        )'''

# Remove/replace the bottom HR records note container.
def find_enclosing_widget(block: str, pos: int, tokens) -> tuple[int, int] | None:
    candidates = []
    for token in tokens:
        search_from = pos
        while True:
            start = block.rfind(token, 0, search_from)
            if start == -1:
                break
            depth = 0
            quote = None
            escape = False
            end = -1
            i = start
            while i < len(block):
                ch = block[i]
                if quote:
                    if escape:
                        escape = False
                    elif ch == '\\':
                        escape = True
                    elif ch == quote:
                        quote = None
                else:
                    if ch == '"' or ch == "'":
                        quote = ch
                    elif ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            if end < len(block) and block[end] == ',':
                                end += 1
                            break
                i += 1
            if end != -1:
                piece = block[start:end]
                if 'HR records and printable' in piece:
                    line_start = block.rfind('\n', 0, start) + 1
                    candidates.append((line_start, end, len(piece)))
            search_from = start
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[2])
    return candidates[0][0], candidates[0][1]

note_pos = sidebar.find('HR records and printable')
if note_pos != -1:
    found = find_enclosing_widget(sidebar, note_pos, ['Container(', 'Card(', 'Padding('])
    if found is None:
        raise SystemExit('Could not locate sidebar HR records note container.')
    start, end = found
    sidebar = sidebar[:start] + '        ' + logout_footer + ',\n' + sidebar[end:]
elif 'label: const Text(\'Logout\')' not in sidebar and 'label: const Text("Logout")' not in sidebar:
    # Fallback: insert after Spacer.
    if 'const Spacer(),' in sidebar:
        sidebar = sidebar.replace('const Spacer(),', 'const Spacer(),\n        ' + logout_footer + ',\n', 1)
    else:
        raise SystemExit('Could not find HR records note or fallback sidebar insertion point.')

text = text[:sidebar_start] + sidebar + text[sidebar_end:]
path.write_text(text, encoding='utf-8')
print('Sidebar footer note removed and Logout button moved there.')
