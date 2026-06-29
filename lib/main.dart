// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'hr_modern_app_v2.dart';

const projectUrl = String.fromEnvironment(
  'SUPABASE_URL',
  defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co',
);
const publicClientKey = String.fromEnvironment(
  'SUPABASE_PUBLIC_CLIENT_KEY',
  defaultValue: 'sb_publishable_QJuRm0RkkQfbgAnBPPxbYw_AtG0BK3o',
);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: projectUrl, anonKey: publicClientKey);
  runApp(const LoginGateApp());
}

class LoginGateApp extends StatefulWidget {
  const LoginGateApp({super.key});

  @override
  State<LoginGateApp> createState() => _LoginGateAppState();
}

class _LoginGateAppState extends State<LoginGateApp> {
  String? role;

  @override
  void initState() {
    super.initState();
    role = html.window.localStorage['hr_role'];
  }

  void login(String newRole) {
    html.window.localStorage['hr_role'] = newRole;
    setState(() => role = newRole);
  }

  void logout() {
    html.window.localStorage.remove('hr_role');
    setState(() => role = null);
  }

  @override
  Widget build(BuildContext context) {
    if (role == null) return LoginPage(onLogin: login);
    return Stack(
      children: [
        const HrModernAppV2(),
        Positioned(
          top: 18,
          right: 24,
          child: Material(
            color: Colors.transparent,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: const [BoxShadow(color: Color(0x14000000), blurRadius: 18, offset: Offset(0, 8))],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircleAvatar(
                    radius: 15,
                    backgroundColor: const Color(0xFFEFF6FF),
                    child: Icon(role == 'Admin' ? Icons.admin_panel_settings_rounded : Icons.badge_rounded, color: const Color(0xFF2563EB), size: 17),
                  ),
                  const SizedBox(width: 8),
                  Text(role!, style: const TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.w900, fontSize: 13)),
                  const SizedBox(width: 10),
                  TextButton.icon(
                    onPressed: logout,
                    icon: const Icon(Icons.logout_rounded, size: 17),
                    label: const Text('Logout'),
                    style: TextButton.styleFrom(foregroundColor: const Color(0xFFDC2626), padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8), minimumSize: Size.zero),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class LoginPage extends StatefulWidget {
  final ValueChanged<String> onLogin;
  const LoginPage({super.key, required this.onLogin});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  String account = 'Admin';
  final password = TextEditingController();
  bool obscure = true;
  String? error;

  @override
  void dispose() {
    password.dispose();
    super.dispose();
  }

  void submit() {
    final pass = password.text.trim();
    final ok = (account == 'Admin' && pass == 'Admin@12345') || (account == 'HR' && pass == 'Hr@12345');
    if (!ok) {
      setState(() => error = 'Invalid password for $account.');
      return;
    }
    widget.onLogin(account);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HR Monitoring Login',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2563EB)),
        fontFamily: 'Arial',
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.6)),
        ),
      ),
      home: Scaffold(
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
                                Text('Login to continue', style: TextStyle(color: Color(0xFF64748B), fontWeight: FontWeight.w600)),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 28),
                      DropdownButtonFormField<String>(
                        value: account,
                        isExpanded: true,
                        decoration: const InputDecoration(labelText: 'Account Type', prefixIcon: Icon(Icons.person_rounded)),
                        items: const [
                          DropdownMenuItem(value: 'Admin', child: Text('Admin')),
                          DropdownMenuItem(value: 'HR', child: Text('HR')),
                        ],
                        onChanged: (value) => setState(() {
                          account = value ?? 'Admin';
                          error = null;
                          password.clear();
                        }),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        controller: password,
                        obscureText: obscure,
                        onSubmitted: (_) => submit(),
                        decoration: InputDecoration(
                          labelText: 'Password',
                          prefixIcon: const Icon(Icons.lock_rounded),
                          suffixIcon: IconButton(
                            onPressed: () => setState(() => obscure = !obscure),
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
                        child: FilledButton.icon(onPressed: submit, icon: const Icon(Icons.login_rounded), label: const Text('Login')),
                      ),
                      const SizedBox(height: 16),
                      const Text('Admin and HR have the same full system access.', style: TextStyle(color: Color(0xFF64748B), height: 1.35, fontWeight: FontWeight.w600)),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
