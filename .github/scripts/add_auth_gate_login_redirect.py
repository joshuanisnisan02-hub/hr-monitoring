from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

if "import 'dart:async';" not in text:
    html_import = "import 'dart:html' as html;"
    if html_import in text:
        text = text.replace(html_import, html_import + "\nimport 'dart:async';", 1)
    else:
        text = "import 'dart:async';\n" + text

# Route app through AuthGate instead of always opening ShellPage.
text = text.replace(
    "home: publicClientKey.isEmpty ? const SetupPage() : const ShellPage(),",
    "home: publicClientKey.isEmpty ? const SetupPage() : const AuthGate(),",
)

login_code = r'''
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  Session? session;
  StreamSubscription<AuthState>? _authSub;

  @override
  void initState() {
    super.initState();
    session = db.auth.currentSession;
    _authSub = db.auth.onAuthStateChange.listen((data) {
      if (!mounted) return;
      setState(() => session = data.session);
    });
  }

  @override
  void dispose() {
    _authSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return session == null ? const LoginPage() : const ShellPage();
  }
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
      final res = await db.auth.signInWithPassword(email: email, password: password);
      if (res.session == null) {
        if (mounted) showSnack(context, 'Login failed. Please check your credentials.');
      }
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

if 'class AuthGate extends StatefulWidget' not in text:
    marker = 'class SetupPage extends StatelessWidget {'
    if marker not in text:
        raise SystemExit('SetupPage marker was not found.')
    text = text.replace(marker, login_code + marker, 1)

# Make logout rely on AuthGate instead of going back to dashboard.
if 'html.window.location.reload();' in text and 'Future<void> logoutUser(BuildContext context)' in text:
    start = text.find('Future<void> logoutUser(BuildContext context)')
    end = text.find('\n}\n', start)
    if start != -1 and end != -1:
        end += len('\n}\n')
        logout_function = r'''Future<void> logoutUser(BuildContext context) async {
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
        text = text[:start] + logout_function + text[end:]

path.write_text(text, encoding='utf-8')
print('AuthGate added. Logout now redirects to LoginPage instead of Dashboard.')
