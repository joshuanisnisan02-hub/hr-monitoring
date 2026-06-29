import 'package:flutter/material.dart';
import 'hr_modern_app.dart' as modern;
import 'hr_modern_app_v2.dart' as app2;
import 'hr_rebuilt_app.dart' as base;

const _primary = Color(0xFF2563EB);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _line = Color(0xFFE2E8F0);
const _danger = Color(0xFFDC2626);

class HrLoggedInApp extends StatelessWidget {
  final String role;
  final VoidCallback onLogout;
  const HrLoggedInApp({super.key, required this.role, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HR Monitoring',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        colorScheme: ColorScheme.fromSeed(seedColor: _primary),
        fontFamily: 'Arial',
        cardTheme: CardThemeData(
          elevation: 0,
          color: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(22),
            side: const BorderSide(color: _line),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF4B5FA7),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFF4B5FA7),
            side: const BorderSide(color: Color(0xFFCBD5E1)),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
          labelStyle: const TextStyle(color: Color(0xFF1E40AF), fontWeight: FontWeight.w700, fontSize: 13),
          hintStyle: const TextStyle(color: _muted),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _line)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _line)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: _primary, width: 1.5)),
        ),
      ),
      home: _HrShell(role: role, onLogout: onLogout),
    );
  }
}

class _HrShell extends StatefulWidget {
  final String role;
  final VoidCallback onLogout;
  const _HrShell({required this.role, required this.onLogout});

  @override
  State<_HrShell> createState() => _HrShellState();
}

class _HrShellState extends State<_HrShell> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      base.DashboardPage(onNavigate: (i) => setState(() => index = i)),
      const modern.ModernEmployeesPage(),
      const modern.ModernContractsPage(),
      const modern.ModernCredentialsPage(),
      const modern.ModernEvaluationsPage(),
      const modern.ModernRankingPage(),
      const app2.ReferencesDropdownPage(),
      const base.ReportsPage(),
    ];

    return Scaffold(
      body: Row(
        children: [
          _Sidebar(
            selectedIndex: index,
            role: widget.role,
            onLogout: widget.onLogout,
            onChanged: (i) => setState(() => index = i),
          ),
          const VerticalDivider(width: 1, color: _line),
          Expanded(child: pages[index]),
        ],
      ),
    );
  }
}

class _Sidebar extends StatelessWidget {
  final int selectedIndex;
  final String role;
  final ValueChanged<int> onChanged;
  final VoidCallback onLogout;

  const _Sidebar({required this.selectedIndex, required this.role, required this.onChanged, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    const labels = ['Dashboard', 'Employees', 'Contracts', 'Credentials', 'Evaluations', 'Ranking', 'References', 'Reports'];
    const icons = [Icons.dashboard_rounded, Icons.groups_rounded, Icons.assignment_rounded, Icons.badge_rounded, Icons.rate_review_rounded, Icons.leaderboard_rounded, Icons.tune_rounded, Icons.print_rounded];
    return Container(
      width: 248,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(18, 20, 18, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(width: 44, height: 44, decoration: BoxDecoration(gradient: const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]), borderRadius: BorderRadius.circular(16)), child: const Icon(Icons.school_rounded, color: Colors.white)),
            const SizedBox(width: 12),
            const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
          ]),
          const SizedBox(height: 7),
          const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 24),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: labels.length,
              itemBuilder: (_, i) => _SidebarItem(
                label: labels[i],
                icon: icons[i],
                selected: selectedIndex == i,
                onTap: () => onChanged(i),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(16), border: Border.all(color: _line)),
            child: Row(children: [
              CircleAvatar(radius: 18, backgroundColor: const Color(0xFFEFF6FF), child: Icon(role == 'Admin' ? Icons.admin_panel_settings_rounded : Icons.badge_rounded, color: _primary, size: 20)),
              const SizedBox(width: 10),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(role, style: const TextStyle(color: _ink, fontWeight: FontWeight.w900)),
                Text(role == 'Admin' ? 'admin@hr-monitoring.local' : 'hr@hr-monitoring.local', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: _muted, fontSize: 11.5, fontWeight: FontWeight.w600)),
              ])),
            ]),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: onLogout,
              icon: const Icon(Icons.logout_rounded),
              label: const Text('Logout'),
              style: OutlinedButton.styleFrom(foregroundColor: _danger),
            ),
          ),
        ],
      ),
    );
  }
}

class _SidebarItem extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const _SidebarItem({required this.label, required this.icon, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
          decoration: BoxDecoration(
            color: selected ? const Color(0xFFEFF6FF) : Colors.transparent,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: selected ? const Color(0xFFDBEAFE) : Colors.transparent),
          ),
          child: Row(children: [
            Icon(icon, color: selected ? _primary : const Color(0xFF64748B), size: 21),
            const SizedBox(width: 12),
            Expanded(child: Text(label, overflow: TextOverflow.ellipsis, style: TextStyle(fontWeight: selected ? FontWeight.w900 : FontWeight.w700, color: selected ? _primary : _ink))),
          ]),
        ),
      ),
    );
  }
}
