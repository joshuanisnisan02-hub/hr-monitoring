import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'hr_rebuilt_app.dart' as base;

const _primary = Color(0xFF2563EB);
const _accent = Color(0xFF4B5FA7);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF8FAFC);
const _line = Color(0xFFE2E8F0);

SupabaseClient get db => Supabase.instance.client;

class HrModernApp extends StatelessWidget {
  const HrModernApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HR Monitoring',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: _bg,
        colorScheme: ColorScheme.fromSeed(seedColor: _primary),
        fontFamily: 'Arial',
        dialogTheme: DialogThemeData(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          elevation: 18,
          alignment: Alignment.center,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
        ),
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
            backgroundColor: _accent,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: _accent,
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
      home: const ModernShellPage(),
    );
  }
}

class ModernShellPage extends StatefulWidget {
  const ModernShellPage({super.key});

  @override
  State<ModernShellPage> createState() => _ModernShellPageState();
}

class _ModernShellPageState extends State<ModernShellPage> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      base.DashboardPage(onNavigate: (i) => setState(() => index = i)),
      const ModernEmployeesPage(),
      const ModernContractsPage(),
      const ModernCredentialsPage(),
      const ModernEvaluationsPage(),
      const ModernRankingPage(),
      const ModernReferencesPage(),
      const base.ReportsPage(),
    ];

    return Scaffold(
      body: Row(
        children: [
          ModernSidebar(selectedIndex: index, onChanged: (i) => setState(() => index = i)),
          const VerticalDivider(width: 1, color: _line),
          Expanded(child: pages[index]),
        ],
      ),
    );
  }
}

class _NavItem {
  final String label;
  final IconData icon;
  const _NavItem(this.label, this.icon);
}

class ModernSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  const ModernSidebar({super.key, required this.selectedIndex, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    const items = [
      _NavItem('Dashboard', Icons.dashboard_rounded),
      _NavItem('Employees', Icons.groups_rounded),
      _NavItem('Contracts', Icons.assignment_rounded),
      _NavItem('Credentials', Icons.badge_rounded),
      _NavItem('Evaluations', Icons.rate_review_rounded),
      _NavItem('Ranking', Icons.leaderboard_rounded),
      _NavItem('References', Icons.tune_rounded),
      _NavItem('Reports', Icons.print_rounded),
    ];

    return Container(
      width: 240,
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(18, 20, 18, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [BoxShadow(color: Color(0x332563EB), blurRadius: 18, offset: Offset(0, 8))],
                ),
                child: const Icon(Icons.school_rounded, color: Colors.white),
              ),
              const SizedBox(width: 12),
              const Expanded(child: Text('HR Monitoring', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: _ink))),
            ],
          ),
          const SizedBox(height: 7),
          const Text('Faculty and staff records', style: TextStyle(fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 24),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: items.length,
              itemBuilder: (_, i) => _SidebarItem(
                label: items[i].label,
                icon: items[i].icon,
                selected: selectedIndex == i,
                onTap: () => onChanged(i),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFDBEAFE))),
            child: const Text(
              'References manage missing dropdown choices.',
              style: TextStyle(color: Color(0xFF1E3A8A), fontSize: 11.5, height: 1.25, fontWeight: FontWeight.w700),
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
          child: Row(
            children: [
              Icon(icon, color: selected ? _primary : const Color(0xFF64748B), size: 21),
              const SizedBox(width: 12),
              Expanded(child: Text(label, overflow: TextOverflow.ellipsis, style: TextStyle(fontWeight: selected ? FontWeight.w900 : FontWeight.w700, color: selected ? _primary : _ink))),
            ],
          ),
        ),
      ),
    );
  }
}

class ModernEmployeesPage extends StatelessWidget {
  const ModernEmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => base.PageFrame(
        title: 'Employees',
        subtitle: 'Create, edit, delete, and search employee or faculty master records.',
        child: base.CrudTable(
          load: () => base.loadEmployees(),
          searchHint: 'Search employees, appointment, status, or license',
          addLabel: 'Add Employee',
          columns: const [
            base.GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            base.GridCol('appointment', 'Appointment', flex: 2),
            base.GridCol('designation', 'Designation', flex: 2),
            base.GridCol('employee_type', 'Type'),
            base.GridCol('employment_status', 'Status', isStatus: true),
            base.GridCol('current_salary', 'Salary', isMoney: true),
          ],
          onAdd: (ctx, refresh) => editEmployee(ctx, null, refresh),
          onEdit: editEmployee,
          onDelete: (row) => db.from('employees').delete().eq('id', row['id']),
        ),
      );
}

class ModernContractsPage extends StatelessWidget {
  const ModernContractsPage({super.key});

  @override
  Widget build(BuildContext context) => base.PageFrame(
        title: 'Contracts',
        subtitle: 'Manage contract records with dynamic total days left.',
        child: base.CrudTable(
          load: () => base.loadContracts(),
          searchHint: 'Search employee, contract type, date, or status',
          addLabel: 'Add Contract',
          columns: const [
            base.GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            base.GridCol('contract_type', 'Contract Type', flex: 2),
            base.GridCol('status', 'Status', isStatus: true),
            base.GridCol('contract_start_date', 'Start'),
            base.GridCol('duration_months', 'Months', isNumber: true),
            base.GridCol('contract_end_date', 'End'),
            base.GridCol('days_left', 'Days Left', isNumber: true),
          ],
          onAdd: (ctx, refresh) => editContract(ctx, null, refresh),
          onEdit: editContract,
          onDelete: (row) => db.from('employee_contracts').delete().eq('id', row['id']),
        ),
      );
}

class ModernCredentialsPage extends StatelessWidget {
  const ModernCredentialsPage({super.key});

  @override
  Widget build(BuildContext context) => base.PageFrame(
        title: 'Credentials',
        subtitle: 'Manage licenses and national certificates linked to employees.',
        child: DefaultTabController(
          length: 2,
          child: Column(children: const [
            Align(alignment: Alignment.centerLeft, child: SizedBox(width: 430, child: TabBar(tabs: [Tab(text: 'Licenses'), Tab(text: 'National Certificates')]))),
            SizedBox(height: 16),
            Expanded(child: TabBarView(children: [ModernLicensesTab(), ModernCertificatesTab()])),
          ]),
        ),
      );
}

class ModernLicensesTab extends StatelessWidget {
  const ModernLicensesTab({super.key});

  @override
  Widget build(BuildContext context) => base.CrudTable(
        load: () => base.loadLicenses(),
        searchHint: 'Search employee, license name, number, or status',
        addLabel: 'Add License',
        columns: const [
          base.GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          base.GridCol('license_name', 'License', flex: 2),
          base.GridCol('license_number', 'License No.', flex: 2),
          base.GridCol('issued_date', 'Issued'),
          base.GridCol('expiry_date', 'Expiry'),
          base.GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onEdit: editLicense,
        onDelete: (row) => db.from('employee_licenses').delete().eq('id', row['id']),
      );
}

class ModernCertificatesTab extends StatelessWidget {
  const ModernCertificatesTab({super.key});

  @override
  Widget build(BuildContext context) => base.CrudTable(
        load: () => base.loadCertificates(),
        searchHint: 'Search employee, certificate, number, or status',
        addLabel: 'Add Certificate',
        columns: const [
          base.GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          base.GridCol('certificate_name', 'Certificate', flex: 3),
          base.GridCol('certificate_type', 'Type', flex: 2),
          base.GridCol('certificate_number', 'Certificate No.', flex: 2),
          base.GridCol('expiry_date', 'Expiry'),
          base.GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editCertificate(ctx, null, refresh),
        onEdit: editCertificate,
        onDelete: (row) => db.from('employee_certificates').delete().eq('id', row['id']),
      );
}

class ModernEvaluationsPage extends StatelessWidget {
  const ModernEvaluationsPage({super.key});

  @override
  Widget build(BuildContext context) => base.PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage evaluation ratings by academic year and semester.',
        child: base.CrudTable(
          load: () => base.loadEvaluations(),
          searchHint: 'Search employee, academic year, semester, or description',
          addLabel: 'Add Evaluation',
          columns: const [
            base.GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            base.GridCol('academic_year', 'A.Y.'),
            base.GridCol('semester', 'Semester'),
            base.GridCol('superior_rating', 'Superior', isNumber: true),
            base.GridCol('peer_rating', 'Peer', isNumber: true),
            base.GridCol('student_rating', 'Student', isNumber: true),
            base.GridCol('total_rating', 'Total', isNumber: true),
            base.GridCol('total_description', 'Description', flex: 2),
          ],
          onAdd: (ctx, refresh) => editEvaluation(ctx, null, refresh),
          onEdit: editEvaluation,
          onDelete: (row) => db.from('evaluation_records').delete().eq('id', row['id']),
        ),
      );
}

class ModernRankingPage extends StatelessWidget {
  const ModernRankingPage({super.key});

  @override
  Widget build(BuildContext context) => base.PageFrame(
        title: 'Ranking',
        subtitle: 'Previous rank and salary are locked. Applied and approved fields remain editable.',
        child: base.CrudTable(
          load: () => base.loadRankings(),
          searchHint: 'Search employee, cycle, rank, or appointment',
          addLabel: 'Add Ranking',
          columns: const [
            base.GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            base.GridCol('cycle_name', 'Cycle', flex: 2),
            base.GridCol('previous_rank_text', 'Previous', flex: 2),
            base.GridCol('applied_rank_text', 'Applied', flex: 2),
            base.GridCol('points_earned', 'Points', isNumber: true),
            base.GridCol('approved_rank_text', 'Approved', flex: 2),
            base.GridCol('approved_salary', 'Salary', isMoney: true),
          ],
          onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
          onEdit: editRanking,
          onDelete: (row) => db.from('ranking_applications').delete().eq('id', row['id']),
        ),
      );
}

class ModernReferencesPage extends StatelessWidget {
  const ModernReferencesPage({super.key});

  @override
  Widget build(BuildContext context) => base.PageFrame(
        title: 'References',
        subtitle: 'Create additional options for contracts, credentials, evaluations, and ranking ranks/salaries.',
        child: base.CrudTable(
          load: () => base.loadReferences(),
          searchHint: 'Search category, label, value, or salary',
          addLabel: 'Add Reference',
          columns: const [
            base.GridCol('category', 'Category', flex: 2, primary: true),
            base.GridCol('label', 'Display Label', flex: 3),
            base.GridCol('value', 'Saved Value', flex: 3),
            base.GridCol('salary', 'Salary', isMoney: true),
            base.GridCol('is_active', 'Active', isBool: true),
            base.GridCol('sort_order', 'Sort', isNumber: true),
          ],
          onAdd: (ctx, refresh) => editReference(ctx, null, refresh),
          onEdit: editReference,
          onDelete: (row) => db.from('hr_reference_options').delete().eq('id', row['id']),
        ),
      );
}

enum FieldKind { text, number, integer, date, dropdown, multiline, bool }

class EditOption {
  final String value;
  final String label;
  final num? salary;
  const EditOption(this.value, this.label, {this.salary});
}

class EditField {
  final String key;
  final String label;
  final FieldKind kind;
  final bool required;
  final List<EditOption> options;
  final int lines;
  const EditField(this.key, this.label, {this.kind = FieldKind.text, this.required = false, this.options = const [], this.lines = 1});
}

class _ReadOnlyBox extends StatelessWidget {
  final String label;
  final String value;
  final bool wide;
  const _ReadOnlyBox({required this.label, required this.value, this.wide = false});

  @override
  Widget build(BuildContext context) => _FieldShell(
        wide: wide,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(label, style: const TextStyle(color: Color(0xFF1E40AF), fontWeight: FontWeight.w800, fontSize: 12)),
            const SizedBox(height: 5),
            Text(value, style: const TextStyle(color: _ink, fontSize: 14.5, fontWeight: FontWeight.w800)),
          ]),
        ),
      );
}

class _FieldShell extends StatelessWidget {
  final Widget child;
  final bool wide;
  const _FieldShell({required this.child, this.wide = false});

  @override
  Widget build(BuildContext context) {
    final width = ModalFieldWidth.of(context);
    return SizedBox(width: wide ? width.full : width.item, child: child);
  }
}

class ModalFieldWidth extends InheritedWidget {
  final double full;
  final double item;
  const ModalFieldWidth({super.key, required this.full, required this.item, required super.child});

  static ModalFieldWidth of(BuildContext context) {
    final value = context.dependOnInheritedWidgetOfExactType<ModalFieldWidth>();
    assert(value != null, 'ModalFieldWidth missing');
    return value!;
  }

  @override
  bool updateShouldNotify(ModalFieldWidth oldWidget) => full != oldWidget.full || item != oldWidget.item;
}


String _employeeDialogSectionFor(String key) {
  const sections = <String, String>{
    'full_name': 'Personal Information',
    'appointment': 'Personal Information',
    'bio_number': 'Personal Information',
    'gender': 'Personal Information',
    'civil_status': 'Personal Information',
    'birth_date': 'Personal Information',
    'address': 'Personal Information',
    'contact_number': 'Personal Information',
    'email': 'Personal Information',
    'education_level': 'Educational Information',
    'school_graduated': 'Educational Information',
    'degree_course': 'Educational Information',
    'guardian_name': 'Guardian Information',
    'guardian_relationship': 'Guardian Information',
    'guardian_contact': 'Guardian Information',
    'guardian_address': 'Guardian Information',
    'designation': 'Employment Information',
    'employee_type': 'Employment Information',
    'teaching_status': 'Employment Information',
    'employment_status': 'Employment Information',
    'date_hired': 'Employment Information',
    'starting_date': 'Employment Information',
    'current_salary': 'Employment Information',
    'license_summary': 'Employment Information',
    'notes': 'Employment Information',
    'contract_type': 'Contract Information',
    'contract_start_date': 'Contract Information',
    'duration_months': 'Contract Information',
    'contract_end_date': 'Contract Information',
    'contract_attachment_url': 'Contract Information',
    'contract_status': 'Contract Information',
    'credential_kind': 'Credential Information',
    'license_name': 'License Information',
    'license_number': 'License Information',
    'license_issued_date': 'License Information',
    'license_expiry_date': 'License Information',
    'license_attachment_url': 'License Information',
    'license_status': 'License Information',
    'certificate_type': 'Certificate Information',
    'certificate_name': 'Certificate Information',
    'certificate_number': 'Certificate Information',
    'certificate_issued_date': 'Certificate Information',
    'certificate_expiry_date': 'Certificate Information',
    'certificate_attachment_url': 'Certificate Information',
    'certificate_status': 'Certificate Information',
  };
  return sections[key] ?? 'Other Information';
}

class _EmployeeDialogSectionLabel extends StatelessWidget {
  final String title;
  const _EmployeeDialogSectionLabel(this.title);

  @override
  Widget build(BuildContext context) => SizedBox(
        width: double.infinity,
        child: Container(
          margin: const EdgeInsets.only(top: 14, bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFFEFF6FF),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFBFDBFE)),
          ),
          child: Row(children: [
            const Expanded(child: Divider(color: Color(0xFF93C5FD), thickness: 1)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: Text(
                title.toUpperCase(),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF1E3A8A),
                  letterSpacing: 0.6,
                ),
              ),
            ),
            const Expanded(child: Divider(color: Color(0xFF93C5FD), thickness: 1)),
          ]),
        ),
      );
}

List<Widget> _buildModernDialogFields(
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState,
) {
  final widgets = <Widget>[];
  String? currentSection;

  for (final f in fields) {
    final section = _employeeDialogSectionFor(f.key);
    if (section != currentSection) {
      if (widgets.isNotEmpty) widgets.add(const _FieldShell(wide: true, child: SizedBox(height: 4)));
      widgets.add(_EmployeeDialogSectionLabel(section));
      currentSection = section;
    }

    final wide = f.kind == FieldKind.multiline;
    if (f.kind == FieldKind.dropdown || f.kind == FieldKind.bool) {
      final opts = f.kind == FieldKind.bool ? const [EditOption('true', 'Active'), EditOption('false', 'Inactive')] : uniqueOptions(f.options);
      widgets.add(_FieldShell(
        wide: wide,
        child: DropdownButtonFormField<String>(
          value: optionValueOrFirst(selected[f.key], opts, f.required),
          isExpanded: true,
          decoration: InputDecoration(labelText: f.label),
          items: opts.map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
          validator: (v) => f.required && (v == null || v.isEmpty) ? 'Required' : null,
          onChanged: (v) => setDialogState(() => selected[f.key] = v),
        ),
      ));
    } else {
      widgets.add(_FieldShell(
        wide: wide,
        child: TextFormField(
          controller: controllers[f.key],
          maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
          keyboardType: f.kind == FieldKind.number || f.kind == FieldKind.integer ? TextInputType.number : TextInputType.text,
          decoration: InputDecoration(labelText: f.label, hintText: f.kind == FieldKind.date ? 'YYYY-MM-DD' : null),
          validator: (v) => f.required && (v == null || v.trim().isEmpty) ? 'Required' : null,
        ),
      ));
    }
  }
  return widgets;
}

Future<Map<String, dynamic>?> showModernRecordDialog(BuildContext context, String title, List<EditField> fields, Map<String, dynamic>? initial, {String? readOnlyEmployeeName}) async {
  final formKey = GlobalKey<FormState>();
  final controllers = <String, TextEditingController>{};
  final selected = <String, String?>{};

  for (final f in fields) {
    final raw = initial?[f.key]?.toString();
    if (f.kind == FieldKind.dropdown || f.kind == FieldKind.bool) {
      selected[f.key] = f.kind == FieldKind.bool ? ((initial?[f.key] ?? true) == true ? 'true' : 'false') : optionValueOrFirst(raw, f.options, f.required);
    } else {
      controllers[f.key] = TextEditingController(text: base.formatEditValue(initial?[f.key]));
    }
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    barrierDismissible: false,
    builder: (dialogContext) => StatefulBuilder(
      builder: (dialogContext, setDialogState) => Dialog(
        insetPadding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final screen = MediaQuery.sizeOf(context);
            final maxWidth = screen.width < 920 ? screen.width - 40 : 820.0;
            final maxHeight = screen.height * 0.88;
            return ConstrainedBox(
              constraints: BoxConstraints(maxWidth: maxWidth, maxHeight: maxHeight),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(24, 22, 18, 14),
                    child: Row(children: [
                      Expanded(child: Text(title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.3))),
                      IconButton(onPressed: () => Navigator.pop(dialogContext), icon: const Icon(Icons.close_rounded)),
                    ]),
                  ),
                  const Divider(height: 1, color: _line),
                  Flexible(
                    child: Form(
                      key: formKey,
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(22),
                        child: LayoutBuilder(
                          builder: (context, inner) {
                            final twoColumns = inner.maxWidth >= 720;
                            final gap = twoColumns ? 14.0 : 0.0;
                            final itemWidth = twoColumns ? (inner.maxWidth - gap) / 2 : inner.maxWidth;
                            return ModalFieldWidth(
                              full: inner.maxWidth,
                              item: itemWidth,
                              child: Wrap(
                                spacing: gap,
                                runSpacing: 14,
                                children: [
                                  if (readOnlyEmployeeName != null) _ReadOnlyBox(label: 'Employee Name', value: readOnlyEmployeeName, wide: true),
                                  ..._buildModernDialogFields(fields, controllers, selected, setDialogState),
                                ],
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                  ),
                  const Divider(height: 1, color: _line),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(22, 14, 22, 18),
                    child: Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                      TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
                      const SizedBox(width: 10),
                      FilledButton.icon(
                        icon: const Icon(Icons.save_rounded, size: 18),
                        onPressed: () {
                          if (!formKey.currentState!.validate()) return;
                          final out = <String, dynamic>{};
                          for (final f in fields) {
                            if (f.kind == FieldKind.dropdown) {
                              out[f.key] = base.emptyToNull(selected[f.key]);
                            } else if (f.kind == FieldKind.bool) {
                              out[f.key] = selected[f.key] == 'true';
                            } else {
                              out[f.key] = parseFieldValue(controllers[f.key]!.text, f.kind);
                            }
                          }
                          Navigator.pop(dialogContext, out);
                        },
                        label: const Text('Save'),
                      ),
                    ]),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    ),
  );

  for (final c in controllers.values) {
    c.dispose();
  }
  return result;
}

Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), base.formatValue(r['full_name']))).toList();
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), base.formatValue(r['name']))).toList();
}

Future<List<EditOption>> referenceOptions(String category, List<EditOption> fallback) async {
  try {
    final rows = await db.from('hr_reference_options').select('label, value, salary').eq('category', category).eq('is_active', true).order('sort_order').order('label').limit(500);
    final refs = rows.map<EditOption>((r) => EditOption((r['value'] ?? r['label']).toString(), base.formatValue(r['label']), salary: num.tryParse('${r['salary'] ?? ''}'))).toList();
    return uniqueOptions([...fallback, ...refs]);
  } catch (_) {
    return fallback;
  }
}

Future<List<EditOption>> rankOptions() async {
  final out = <EditOption>[];
  try {
    final rows = await db.from('ranks').select('name, default_salary, salary_grade').order('sort_order').order('name').limit(500);
    for (final r in rows) {
      final name = base.formatValue(r['name']);
      final salary = num.tryParse('${r['default_salary'] ?? ''}');
      final sg = r['salary_grade'] == null ? '' : ' - SG ${r['salary_grade']}';
      final pay = salary == null ? '' : ' - ${base.formatMoney(salary)}';
      out.add(EditOption(name, '$name$sg$pay', salary: salary));
    }
  } catch (_) {}
  final refs = await referenceOptions('rank', const []);
  return uniqueOptions([...out, ...refs]);
}

String linkedEmployeeName(Map<String, dynamic>? row) => row?['employees'] is Map ? base.formatValue(row?['employees']['full_name']) : 'Linked Employee';

Future<bool> ensureNoEmployeeDuplicate(BuildContext context, String tableName, Object? employeeId, String moduleName) async {
  if (employeeId == null || employeeId.toString().trim().isEmpty) return true;
  try {
    final existing = await db.from(tableName).select('id').eq('employee_id', employeeId).limit(1);
    if (existing.isNotEmpty) {
      showSnack(context, 'Duplicate prevented: this employee already has a $moduleName record.');
      return false;
    }
    return true;
  } catch (e) {
    showSnack(context, 'Duplicate check failed: $e');
    return false;
  }
}

Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showModernRecordDialog(
    context,
    row == null ? 'Add Employee' : 'Edit Employee',
    const [
      EditField('full_name', 'Full Name', required: true),
      EditField('appointment', 'Appointment'),
      EditField('designation', 'Designation'),
      EditField('employee_type', 'Employee Type', kind: FieldKind.dropdown, options: [EditOption('full_time', 'Full Time'), EditOption('probationary', 'Probationary'), EditOption('part_time', 'Part Time'), EditOption('staff', 'Staff'), EditOption('faculty_staff', 'Faculty / Staff')]),
      EditField('employment_status', 'Employment Status', kind: FieldKind.dropdown, options: [EditOption('active', 'Active'), EditOption('inactive', 'Inactive'), EditOption('separated', 'Separated')]),
      EditField('current_salary', 'Current Salary', kind: FieldKind.number),
      EditField('license_summary', 'License Summary'),
    ],
    row,
  );
  if (data == null) return;
  data['name_key'] = base.normalizeName(data['full_name']?.toString() ?? '');
  await saveRow(context, 'employees', row?['id'], data, refresh);
}

Future<void> editContract(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final contractTypes = await referenceOptions('contract_type', const [EditOption('Full-Time-Probationary', 'Full-Time-Probationary'), EditOption('Probationary', 'Probationary'), EditOption('Compliance', 'Compliance')]);
  final statuses = await referenceOptions('contract_status', const [EditOption('On-going', 'On-going'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]);
  final data = await showModernRecordDialog(
    context,
    isAdd ? 'Add Contract' : 'Edit Contract',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      EditField('contract_type', 'Contract Type', kind: FieldKind.dropdown, options: contractTypes),
      const EditField('contract_start_date', 'Start Date', kind: FieldKind.date),
      const EditField('duration_months', 'Duration In Months', kind: FieldKind.integer),
      const EditField('contract_end_date', 'End Date', kind: FieldKind.date),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: statuses),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_contracts', data['employee_id'], 'contract')) return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}

Future<void> editLicense(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final licenses = await referenceOptions('license_name', const [EditOption('LPT', 'LPT'), EditOption('RCRIM', 'RCRIM'), EditOption('MSCRIM', 'MSCRIM')]);
  final statuses = await referenceOptions('credential_status', const [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]);
  final data = await showModernRecordDialog(
    context,
    isAdd ? 'Add License' : 'Edit License',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      EditField('license_name', 'License Name', kind: FieldKind.dropdown, required: true, options: licenses),
      const EditField('license_number', 'License Number'),
      const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: statuses),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_licenses', data['employee_id'], 'license')) return;
  await saveRow(context, 'employee_licenses', row?['id'], data, refresh);
}

Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final certTypes = await referenceOptions('certificate_type', const [EditOption('National Certificate', 'National Certificate'), EditOption('Training Certificate', 'Training Certificate'), EditOption('Eligibility', 'Eligibility')]);
  final statuses = await referenceOptions('credential_status', const [EditOption('Active', 'Active'), EditOption('For Renewal', 'For Renewal'), EditOption('Expired', 'Expired'), EditOption('Archived', 'Archived')]);
  final data = await showModernRecordDialog(
    context,
    isAdd ? 'Add Certificate' : 'Edit Certificate',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      EditField('certificate_type', 'Certificate Type', kind: FieldKind.dropdown, options: certTypes),
      const EditField('certificate_name', 'Certificate Name', required: true),
      const EditField('certificate_number', 'Certificate Number'),
      const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
      const EditField('expiry_date', 'Expiry Date', kind: FieldKind.date),
      EditField('status', 'Status', kind: FieldKind.dropdown, options: statuses),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'employee_certificates', data['employee_id'], 'certificate')) return;
  data['certificate_type'] ??= 'National Certificate';
  await saveRow(context, 'employee_certificates', row?['id'], data, refresh);
}

Future<void> editEvaluation(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final semesters = await referenceOptions('evaluation_semester', const [EditOption('1st Semester', '1st Semester'), EditOption('2nd Semester', '2nd Semester')]);
  final descriptions = await referenceOptions('evaluation_description', const [EditOption('Excellent', 'Excellent'), EditOption('Very Satisfactory', 'Very Satisfactory'), EditOption('Satisfactory', 'Satisfactory')]);
  final data = await showModernRecordDialog(
    context,
    isAdd ? 'Add Evaluation' : 'Edit Evaluation',
    [
      if (isAdd) EditField('employee_id', 'Employee Name', kind: FieldKind.dropdown, required: true, options: employees),
      const EditField('academic_year', 'Academic Year', required: true),
      EditField('semester', 'Semester', kind: FieldKind.dropdown, required: true, options: semesters),
      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),
      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),
      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),
      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),
      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),
      EditField('total_description', 'Total Description', kind: FieldKind.dropdown, options: descriptions),
    ],
    row,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(row),
  );
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'evaluation_records', data['employee_id'], 'evaluation')) return;
  await saveRow(context, 'evaluation_records', row?['id'], data, refresh);
}

Future<void> editRanking(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showModernRankingDialog(context, isAdd ? await employeeOptions() : const <EditOption>[], await cycleOptions(), await rankOptions(), row);
  if (data == null) return;
  if (isAdd && !await ensureNoEmployeeDuplicate(context, 'ranking_applications', data['employee_id'], 'ranking')) return;
  await saveRow(context, 'ranking_applications', row?['id'], data, refresh);
}

Future<void> editReference(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showModernRecordDialog(
    context,
    row == null ? 'Add Reference' : 'Edit Reference',
    const [
      EditField('category', 'Module / Category', kind: FieldKind.dropdown, required: true, options: [
        EditOption('contract_type', 'Contracts - Contract Type'),
        EditOption('contract_status', 'Contracts - Status'),
        EditOption('license_name', 'Credentials - License Name'),
        EditOption('certificate_type', 'Credentials - Certificate Type'),
        EditOption('credential_status', 'Credentials - Status'),
        EditOption('evaluation_semester', 'Evaluations - Semester'),
        EditOption('evaluation_description', 'Evaluations - Description'),
        EditOption('rank', 'Ranking - Rank / Salary'),
      ]),
      EditField('label', 'Display Label', required: true),
      EditField('value', 'Saved Value'),
      EditField('salary', 'Salary For Rank', kind: FieldKind.number),
      EditField('sort_order', 'Sort Order', kind: FieldKind.integer),
      EditField('is_active', 'Status', kind: FieldKind.bool),
    ],
    row,
  );
  if (data == null) return;
  data['value'] = base.emptyToNull('${data['value'] ?? ''}') ?? data['label'];
  await saveRow(context, 'hr_reference_options', row?['id'], data, refresh);
}

Future<Map<String, dynamic>?> showModernRankingDialog(BuildContext context, List<EditOption> employees, List<EditOption> cycles, List<EditOption> ranks, Map<String, dynamic>? initial) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? optionValueOrFirst(null, employees, true) : initial?['employee_id']?.toString();
  String? cycleId = optionValueOrFirst(initial?['cycle_id']?.toString(), cycles, true);
  final appointment = TextEditingController(text: base.formatEditValue(initial?['appointment']));
  final appliedRank = TextEditingController(text: base.formatEditValue(initial?['applied_rank_text']));
  final appliedSalary = TextEditingController(text: base.formatEditValue(initial?['applied_salary']));
  final points = TextEditingController(text: base.formatEditValue(initial?['points_earned']));
  final approvedRank = TextEditingController(text: base.formatEditValue(initial?['approved_rank_text']));
  final approvedSalary = TextEditingController(text: base.formatEditValue(initial?['approved_salary']));

  Future<void> pickRank(TextEditingController rank, TextEditingController salary) async {
    final selected = await showDialog<EditOption>(
      context: context,
      builder: (_) => Dialog(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520, maxHeight: 560),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(22, 20, 16, 12),
              child: Row(children: [
                const Expanded(child: Text('Choose Rank', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: _ink))),
                IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close_rounded)),
              ]),
            ),
            const Divider(height: 1, color: _line),
            Flexible(
              child: ranks.isEmpty
                  ? const Center(child: Padding(padding: EdgeInsets.all(24), child: Text('No rank reference found. Add ranks under References.')))
                  : ListView.separated(
                      padding: const EdgeInsets.all(8),
                      itemCount: ranks.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (_, i) => ListTile(title: Text(ranks[i].label), onTap: () => Navigator.pop(context, ranks[i])),
                    ),
            ),
          ]),
        ),
      ),
    );
    if (selected == null) return;
    rank.text = selected.value;
    if (selected.salary != null) salary.text = selected.salary!.toStringAsFixed(2);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    barrierDismissible: false,
    builder: (dialogContext) => StatefulBuilder(
      builder: (dialogContext, setDialogState) => Dialog(
        insetPadding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
        child: LayoutBuilder(builder: (context, constraints) {
          final screen = MediaQuery.sizeOf(context);
          final maxWidth = screen.width < 920 ? screen.width - 40 : 820.0;
          final maxHeight = screen.height * 0.88;
          return ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth, maxHeight: maxHeight),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 22, 18, 14),
                child: Row(children: [
                  Expanded(child: Text(isAdd ? 'Add Ranking Record' : 'Edit Ranking Record', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.3))),
                  IconButton(onPressed: () => Navigator.pop(dialogContext), icon: const Icon(Icons.close_rounded)),
                ]),
              ),
              const Divider(height: 1, color: _line),
              Flexible(
                child: Form(
                  key: formKey,
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(22),
                    child: LayoutBuilder(builder: (context, inner) {
                      final twoColumns = inner.maxWidth >= 720;
                      final gap = twoColumns ? 14.0 : 0.0;
                      final itemWidth = twoColumns ? (inner.maxWidth - gap) / 2 : inner.maxWidth;
                      return ModalFieldWidth(
                        full: inner.maxWidth,
                        item: itemWidth,
                        child: Wrap(spacing: gap, runSpacing: 14, children: [
                          if (isAdd)
                            _FieldShell(
                              child: DropdownButtonFormField<String>(
                                value: optionValueOrFirst(employeeId, employees, true),
                                isExpanded: true,
                                decoration: const InputDecoration(labelText: 'Employee Name'),
                                items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                                onChanged: (v) => setDialogState(() => employeeId = v),
                              ),
                            )
                          else
                            _ReadOnlyBox(label: 'Employee Name', value: linkedEmployeeName(initial), wide: true),
                          _FieldShell(
                            child: DropdownButtonFormField<String>(
                              value: optionValueOrFirst(cycleId, cycles, true),
                              isExpanded: true,
                              decoration: const InputDecoration(labelText: 'Ranking Cycle'),
                              items: uniqueOptions(cycles).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                              validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                              onChanged: (v) => setDialogState(() => cycleId = v),
                            ),
                          ),
                          textBox('Appointment', appointment),
                          textBox('Points Earned', points, kind: FieldKind.number),
                          _ReadOnlyBox(label: 'Previous Rank', value: base.formatValue(initial?['previous_rank_text'])),
                          _ReadOnlyBox(label: 'Previous Salary', value: base.formatMoney(initial?['previous_salary'])),
                          rankTextBox('Applied Rank', appliedRank, () => pickRank(appliedRank, appliedSalary)),
                          textBox('Applied Salary', appliedSalary, kind: FieldKind.number),
                          rankTextBox('Approved Rank', approvedRank, () => pickRank(approvedRank, approvedSalary)),
                          textBox('Approved Salary', approvedSalary, kind: FieldKind.number),
                          _FieldShell(
                            wide: true,
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(14)),
                              child: const Text('Previous rank and previous salary are locked. Add new rank choices under References.', style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w700)),
                            ),
                          ),
                        ]),
                      );
                    }),
                  ),
                ),
              ),
              const Divider(height: 1, color: _line),
              Padding(
                padding: const EdgeInsets.fromLTRB(22, 14, 22, 18),
                child: Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                  TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
                  const SizedBox(width: 10),
                  FilledButton.icon(
                    icon: const Icon(Icons.save_rounded, size: 18),
                    onPressed: () {
                      if (!formKey.currentState!.validate()) return;
                      Navigator.pop(dialogContext, {
                        'employee_id': isAdd ? base.emptyToNull(employeeId) : initial?['employee_id'],
                        'cycle_id': base.emptyToNull(cycleId),
                        'appointment': base.emptyToNull(appointment.text),
                        'previous_rank_text': initial?['previous_rank_text'],
                        'previous_salary': initial?['previous_salary'],
                        'applied_rank_text': base.emptyToNull(appliedRank.text),
                        'applied_salary': num.tryParse(appliedSalary.text.trim()),
                        'points_earned': num.tryParse(points.text.trim()),
                        'approved_rank_text': base.emptyToNull(approvedRank.text),
                        'approved_salary': num.tryParse(approvedSalary.text.trim()),
                      });
                    },
                    label: const Text('Save'),
                  ),
                ]),
              ),
            ]),
          );
        }),
      ),
    ),
  );

  for (final c in [appointment, appliedRank, appliedSalary, points, approvedRank, approvedSalary]) {
    c.dispose();
  }
  return result;
}

Widget textBox(String label, TextEditingController controller, {FieldKind kind = FieldKind.text}) => _FieldShell(
      child: TextFormField(
        controller: controller,
        keyboardType: kind == FieldKind.number || kind == FieldKind.integer ? TextInputType.number : TextInputType.text,
        maxLines: kind == FieldKind.multiline ? 3 : 1,
        decoration: InputDecoration(labelText: label),
      ),
    );

Widget rankTextBox(String label, TextEditingController controller, VoidCallback onPick) => _FieldShell(
      child: Row(children: [
        Expanded(child: TextFormField(controller: controller, decoration: InputDecoration(labelText: label))),
        const SizedBox(width: 8),
        OutlinedButton(onPressed: onPick, child: const Text('Pick')),
      ]),
    );

Future<void> saveRow(BuildContext context, String table, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from(table).insert(data);
      showSnack(context, 'Record Added.');
    } else {
      await db.from(table).update(data).eq('id', id);
      showSnack(context, 'Record Updated.');
    }
    refresh();
  } catch (e) {
    showSnack(context, 'Save Failed: $e');
  }
}

List<EditOption> uniqueOptions(List<EditOption> options) {
  final seen = <String>{};
  final out = <EditOption>[];
  for (final option in options) {
    if (seen.add(option.value)) out.add(option);
  }
  return out;
}

String? optionValueOrFirst(String? value, List<EditOption> options, bool requiredField) {
  final unique = uniqueOptions(options);
  if (value != null && unique.any((o) => o.value == value)) return value;
  if (requiredField && unique.isNotEmpty) return unique.first.value;
  if (unique.any((o) => o.value == '')) return '';
  return null;
}

Object? parseFieldValue(String text, FieldKind kind) {
  final t = text.trim();
  if (t.isEmpty) return null;
  if (kind == FieldKind.number) return num.tryParse(t);
  if (kind == FieldKind.integer) return int.tryParse(t);
  return t;
}

void showSnack(BuildContext context, String message) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
