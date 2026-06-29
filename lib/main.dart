import 'dart:async';

import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'hr_logged_in_app.dart';

const projectUrl = String.fromEnvironment(
  'SUPABASE_URL',
  defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co',
);
const publicClientKey = String.fromEnvironment(
  'SUPABASE_PUBLIC_CLIENT_KEY',
  defaultValue: 'sb_publishable_QJuRm0RkkQfbgAnBPPxbYw_AtG0BK3o',
);

SupabaseClient get db => Supabase.instance.client;

const adminEmail = 'admin@hr-monitoring.local';
const hrEmail = 'hr@hr-monitoring.local';

bool isAllowedEmail(String? email) {
  final normalized = (email ?? '').toLowerCase();
  return normalized == adminEmail || normalized == hrEmail;
}

String roleForEmail(String? email) {
  return (email ?? '').toLowerCase() == adminEmail ? 'Admin' : 'HR';
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: projectUrl, anonKey: publicClientKey);
  runApp(const HrSecureApp());
}

class HrSecureApp extends StatelessWidget {
  const HrSecureApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HR Monitoring',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2563EB)),
        fontFamily: 'Arial',
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF4B5FA7),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.6)),
        ),
      ),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  Session? session;
  late final StreamSubscription<AuthState> sub;

  @override
  void initState() {
    super.initState();
    session = db.auth.currentSession;
    sub = db.auth.onAuthStateChange.listen((event) {
      final next = event.session;
      if (next != null && !isAllowedEmail(next.user.email)) {
        db.auth.signOut();
        if (mounted) setState(() => session = null);
        return;
      }
      if (mounted) setState(() => session = next);
    });
  }

  @override
  void dispose() {
    sub.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final current = session;
    if (current == null || !isAllowedEmail(current.user.email)) {
      return const LoginPage();
    }
    return HrLoggedInApp(
      role: roleForEmail(current.user.email),
      onLogout: () {
        db.auth.signOut();
      },
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  String email = adminEmail;
  final password = TextEditingController();
  bool obscure = true;
  bool loading = false;
  String? error;

  @override
  void dispose() {
    password.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (password.text.trim().isEmpty) {
      setState(() => error = 'Please enter your password.');
      return;
    }
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final result = await db.auth.signInWithPassword(
        email: email,
        password: password.text.trim(),
      );
      if (!isAllowedEmail(result.user?.email)) {
        await db.auth.signOut();
        throw const AuthException('This account is not allowed.');
      }
    } on AuthException catch (e) {
      setState(() => error = e.message);
    } catch (e) {
      setState(() => error = 'Login failed. Please try again.');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final selectedRole = email == adminEmail ? 'Admin' : 'HR';
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFFF8FAFC), Color(0xFFEFF6FF)]),
        ),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: Card(
              elevation: 0,
              color: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24), side: const BorderSide(color: Color(0xFFE2E8F0))),
              child: Padding(
                padding: const EdgeInsets.all(28),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 52,
                          height: 52,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(colors: [Color(0xFF2563EB), Color(0xFF4F46E5)]),
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: const Icon(Icons.school_rounded, color: Colors.white),
                        ),
                        const SizedBox(width: 14),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('HR Monitoring', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                              SizedBox(height: 3),
                              Text('Secure login', style: TextStyle(color: Color(0xFF64748B), fontWeight: FontWeight.w600)),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 28),
                    DropdownButtonFormField<String>(
                      value: email,
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Account Type', prefixIcon: Icon(Icons.person_rounded)),
                      items: const [
                        DropdownMenuItem(value: adminEmail, child: Text('Admin')),
                        DropdownMenuItem(value: hrEmail, child: Text('HR')),
                      ],
                      onChanged: loading
                          ? null
                          : (value) => setState(() {
                                email = value ?? adminEmail;
                                error = null;
                                password.clear();
                              }),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(13),
                      decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFFE2E8F0))),
                      child: Text(email, style: const TextStyle(color: Color(0xFF64748B), fontWeight: FontWeight.w800)),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: password,
                      obscureText: obscure,
                      enabled: !loading,
                      onSubmitted: (_) => submit(),
                      decoration: InputDecoration(
                        labelText: '$selectedRole Password',
                        prefixIcon: const Icon(Icons.lock_rounded),
                        suffixIcon: IconButton(
                          onPressed: loading ? null : () => setState(() => obscure = !obscure),
                          icon: Icon(obscure ? Icons.visibility_rounded : Icons.visibility_off_rounded),
                        ),
                      ),
                    ),
                    if (error != null) ...[
                      const SizedBox(height: 14),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFFFECACA))),
                        child: Text(error!, style: const TextStyle(color: Color(0xFFDC2626), fontWeight: FontWeight.w700)),
                      ),
                    ],
                    const SizedBox(height: 22),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: loading ? null : submit,
                        icon: loading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.login_rounded),
                        label: Text(loading ? 'Signing in...' : 'Login'),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Passwords are checked by Supabase Auth, not by the browser. Admin and HR have the same full access.', style: TextStyle(color: Color(0xFF64748B), height: 1.35, fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
