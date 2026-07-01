from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# Add timer import.
if "import 'dart:async';" not in text:
    first_import = text.find("import 'dart:html' as html;")
    if first_import != -1:
        line_end = text.find('\n', first_import) + 1
        text = text[:line_end] + "import 'dart:async';\n" + text[line_end:]
    else:
        text = "import 'dart:async';\n" + text

idle_widget = r'''
class IdleLogoutGuard extends StatefulWidget {
  final Widget child;
  const IdleLogoutGuard({super.key, required this.child});

  @override
  State<IdleLogoutGuard> createState() => _IdleLogoutGuardState();
}

class _IdleLogoutGuardState extends State<IdleLogoutGuard> {
  static const Duration idleLimit = Duration(minutes: 5);
  Timer? _idleTimer;
  bool _loggingOut = false;

  @override
  void initState() {
    super.initState();
    _resetIdleTimer();
  }

  @override
  void dispose() {
    _idleTimer?.cancel();
    super.dispose();
  }

  void _resetIdleTimer() {
    if (_loggingOut) return;
    _idleTimer?.cancel();
    _idleTimer = Timer(idleLimit, _logoutDueToIdle);
  }

  Future<void> _logoutDueToIdle() async {
    if (_loggingOut) return;
    _loggingOut = true;
    try {
      await db.auth.signOut();
    } catch (_) {}
    try {
      html.window.sessionStorage.clear();
    } catch (_) {}
    try {
      html.window.localStorage.remove('supabase.auth.token');
    } catch (_) {}
    if (!mounted) {
      html.window.location.reload();
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Session expired because of 5 minutes of inactivity. Please log in again.')),
    );
    await Future<void>.delayed(const Duration(milliseconds: 700));
    html.window.location.reload();
  }

  @override
  Widget build(BuildContext context) => Focus(
        autofocus: true,
        onKeyEvent: (_, __) {
          _resetIdleTimer();
          return KeyEventResult.ignored;
        },
        child: Listener(
          behavior: HitTestBehavior.translucent,
          onPointerDown: (_) => _resetIdleTimer(),
          onPointerMove: (_) => _resetIdleTimer(),
          onPointerHover: (_) => _resetIdleTimer(),
          onPointerSignal: (_) => _resetIdleTimer(),
          child: widget.child,
        ),
      );
}

'''

if 'class IdleLogoutGuard extends StatefulWidget' not in text:
    marker = 'class ShellPage extends StatefulWidget {'
    if marker not in text:
        raise SystemExit('ShellPage marker was not found.')
    text = text.replace(marker, idle_widget + marker, 1)

# Wrap ShellPage build return with IdleLogoutGuard. This keeps the timeout active only after login/main shell is shown.
shell_start = text.find('class _ShellPageState')
if shell_start == -1:
    raise SystemExit('_ShellPageState was not found.')
if 'return IdleLogoutGuard(' not in text[shell_start:text.find('class NavItem', shell_start) if text.find('class NavItem', shell_start) != -1 else len(text)]:
    return_start = text.find('return Scaffold', shell_start)
    if return_start == -1:
        raise SystemExit('ShellPage return Scaffold was not found.')
    scaffold_start = text.find('Scaffold', return_start)
    paren_start = text.find('(', scaffold_start)
    if scaffold_start == -1 or paren_start == -1:
        raise SystemExit('ShellPage Scaffold call was not found.')

    depth = 0
    quote = None
    escape = False
    end_paren = -1
    i = paren_start
    while i < len(text):
        ch = text[i]
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
                    end_paren = i
                    break
        i += 1

    if end_paren == -1:
        raise SystemExit('Could not find end of ShellPage Scaffold call.')
    semi = text.find(';', end_paren)
    if semi == -1:
        raise SystemExit('Could not find semicolon after ShellPage Scaffold call.')
    old_statement = text[return_start:semi + 1]
    scaffold_call = old_statement[len('return '):-1].strip()
    new_statement = 'return IdleLogoutGuard(\n      child: ' + scaffold_call + ',\n    );'
    text = text[:return_start] + new_statement + text[semi + 1:]

path.write_text(text, encoding='utf-8')
print('Idle logout after 5 minutes of inactivity added to lib/main.dart')
