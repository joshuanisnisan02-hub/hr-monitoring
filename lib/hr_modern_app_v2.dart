import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'hr_modern_app.dart' as modern;
import 'hr_rebuilt_app.dart' as base;

const _primary = Color(0xFF2563EB);
const _accent = Color(0xFF4B5FA7);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF8FAFC);
const _line = Color(0xFFE2E8F0);

SupabaseClient get db => Supabase.instance.client;

class HrModernAppV2 extends StatelessWidget {
  const HrModernAppV2({super.key});

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
      home: const ModernShellPageV2(),
    );
  }
}

class ModernShellPageV2 extends StatefulWidget {
  const ModernShellPageV2({super.key});

  @override
  State<ModernShellPageV2> createState() => _ModernShellPageV2State();
}

class _ModernShellPageV2State extends State<ModernShellPageV2> {
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
      const ReferencesDropdownPage(),
      const base.ReportsPage(),
    ];

    return Scaffold(
      body: Row(
        children: [
          modern.ModernSidebar(selectedIndex: index, onChanged: (i) => setState(() => index = i)),
          const VerticalDivider(width: 1, color: _line),
          Expanded(child: pages[index]),
        ],
      ),
    );
  }
}

class ReferencesDropdownPage extends StatelessWidget {
  const ReferencesDropdownPage({super.key});

  @override
  Widget build(BuildContext context) {
    return base.PageFrame(
      title: 'References',
      subtitle: 'Choose what you are adding from a dropdown, then enter only the needed details.',
      child: base.CrudTable(
        load: () => base.loadReferences(),
        searchHint: 'Search module, option name, or salary',
        addLabel: 'Add Reference',
        columns: const [
          base.GridCol('category', 'Reference Type', flex: 2, primary: true),
          base.GridCol('label', 'Option Name', flex: 3),
          base.GridCol('value', 'Saved As', flex: 3),
          base.GridCol('salary', 'Salary', isMoney: true),
          base.GridCol('is_active', 'Active', isBool: true),
          base.GridCol('sort_order', 'Sort', isNumber: true),
        ],
        onAdd: (ctx, refresh) => editReferenceDropdown(ctx, null, refresh),
        onEdit: editReferenceDropdown,
        onDelete: (row) => db.from('hr_reference_options').delete().eq('id', row['id']),
      ),
    );
  }
}

class ReferenceType {
  final String category;
  final String title;
  final String labelName;
  final String hint;
  final bool showSalary;

  const ReferenceType({required this.category, required this.title, required this.labelName, required this.hint, this.showSalary = false});
}

const referenceTypes = <ReferenceType>[
  ReferenceType(category: 'contract_type', title: 'Contracts - Contract Type', labelName: 'Contract Type Name', hint: 'Example: Full-Time-Probationary, Compliance, Renewal'),
  ReferenceType(category: 'contract_status', title: 'Contracts - Status', labelName: 'Contract Status Name', hint: 'Example: On-going, For Renewal, Expired'),
  ReferenceType(category: 'license_name', title: 'Credentials - License Name', labelName: 'License Name', hint: 'Example: LPT, RCRIM, MSCRIM'),
  ReferenceType(category: 'certificate_type', title: 'Credentials - Certificate Type', labelName: 'Certificate Type Name', hint: 'Example: National Certificate, Training Certificate'),
  ReferenceType(category: 'credential_status', title: 'Credentials - Status', labelName: 'Credential Status Name', hint: 'Example: Active, For Renewal, Expired'),
  ReferenceType(category: 'evaluation_semester', title: 'Evaluations - Semester', labelName: 'Semester Name', hint: 'Example: 1st Semester, 2nd Semester, Summer'),
  ReferenceType(category: 'evaluation_description', title: 'Evaluations - Description', labelName: 'Evaluation Description', hint: 'Example: Excellent, Very Satisfactory, Satisfactory'),
  ReferenceType(category: 'rank', title: 'Ranking - Rank and Salary', labelName: 'Rank Name', hint: 'Example: Instructor I, Teacher III, Assistant Professor IV', showSalary: true),
];

ReferenceType referenceTypeFor(String? category) {
  return referenceTypes.firstWhere(
    (item) => item.category == category,
    orElse: () => referenceTypes.first,
  );
}

Future<void> editReferenceDropdown(BuildContext context, Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showReferenceDropdownDialog(context, row);
  if (data == null) return;
  await saveReferenceRow(context, row?['id'], data, refresh);
}

Future<Map<String, dynamic>?> showReferenceDropdownDialog(BuildContext context, Map<String, dynamic>? initial) async {
  final formKey = GlobalKey<FormState>();
  String category = referenceTypeFor(initial?['category']?.toString()).category;
  String isActive = (initial?['is_active'] ?? true) == true ? 'true' : 'false';
  final labelController = TextEditingController(text: base.formatEditValue(initial?['label']));
  final salaryController = TextEditingController(text: base.formatEditValue(initial?['salary']));
  final sortController = TextEditingController(text: base.formatEditValue(initial?['sort_order']));

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    barrierDismissible: false,
    builder: (dialogContext) => StatefulBuilder(
      builder: (dialogContext, setDialogState) {
        final type = referenceTypeFor(category);
        return Dialog(
          insetPadding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: 720, maxHeight: MediaQuery.sizeOf(dialogContext).height * 0.86),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(24, 22, 18, 14),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          initial == null ? 'Add Reference Option' : 'Edit Reference Option',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: _ink, letterSpacing: -0.3),
                        ),
                      ),
                      IconButton(onPressed: () => Navigator.pop(dialogContext), icon: const Icon(Icons.close_rounded)),
                    ],
                  ),
                ),
                const Divider(height: 1, color: _line),
                Flexible(
                  child: Form(
                    key: formKey,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(22),
                      child: LayoutBuilder(
                        builder: (context, constraints) {
                          final twoColumns = constraints.maxWidth >= 620;
                          final itemWidth = twoColumns ? (constraints.maxWidth - 14) / 2 : constraints.maxWidth;
                          return Wrap(
                            spacing: 14,
                            runSpacing: 14,
                            children: [
                              SizedBox(
                                width: constraints.maxWidth,
                                child: DropdownButtonFormField<String>(
                                  value: category,
                                  isExpanded: true,
                                  decoration: const InputDecoration(
                                    labelText: 'What Are You Adding?',
                                    prefixIcon: Icon(Icons.category_rounded),
                                  ),
                                  items: referenceTypes
                                      .map((item) => DropdownMenuItem<String>(
                                            value: item.category,
                                            child: Text(item.title, overflow: TextOverflow.ellipsis),
                                          ))
                                      .toList(),
                                  onChanged: (value) => setDialogState(() => category = value ?? category),
                                ),
                              ),
                              SizedBox(
                                width: constraints.maxWidth,
                                child: Container(
                                  padding: const EdgeInsets.all(13),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFEFF6FF),
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(color: const Color(0xFFDBEAFE)),
                                  ),
                                  child: Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Icon(Icons.info_outline_rounded, color: _primary, size: 19),
                                      const SizedBox(width: 10),
                                      Expanded(
                                        child: Text(
                                          type.hint,
                                          style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w700, height: 1.3),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              SizedBox(
                                width: type.showSalary && twoColumns ? itemWidth : constraints.maxWidth,
                                child: TextFormField(
                                  controller: labelController,
                                  decoration: InputDecoration(labelText: type.labelName, prefixIcon: const Icon(Icons.edit_note_rounded)),
                                  validator: (value) => value == null || value.trim().isEmpty ? 'Required' : null,
                                ),
                              ),
                              if (type.showSalary)
                                SizedBox(
                                  width: twoColumns ? itemWidth : constraints.maxWidth,
                                  child: TextFormField(
                                    controller: salaryController,
                                    keyboardType: TextInputType.number,
                                    decoration: const InputDecoration(labelText: 'Auto-Fill Salary', prefixIcon: Icon(Icons.payments_rounded), hintText: 'Example: 15000'),
                                  ),
                                ),
                              SizedBox(
                                width: twoColumns ? itemWidth : constraints.maxWidth,
                                child: TextFormField(
                                  controller: sortController,
                                  keyboardType: TextInputType.number,
                                  decoration: const InputDecoration(labelText: 'Sort Order', prefixIcon: Icon(Icons.sort_rounded), hintText: 'Optional'),
                                ),
                              ),
                              SizedBox(
                                width: twoColumns ? itemWidth : constraints.maxWidth,
                                child: DropdownButtonFormField<String>(
                                  value: isActive,
                                  isExpanded: true,
                                  decoration: const InputDecoration(labelText: 'Status', prefixIcon: Icon(Icons.toggle_on_rounded)),
                                  items: const [
                                    DropdownMenuItem(value: 'true', child: Text('Active')),
                                    DropdownMenuItem(value: 'false', child: Text('Inactive')),
                                  ],
                                  onChanged: (value) => setDialogState(() => isActive = value ?? 'true'),
                                ),
                              ),
                              SizedBox(
                                width: constraints.maxWidth,
                                child: Container(
                                  padding: const EdgeInsets.all(13),
                                  decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14), border: Border.all(color: _line)),
                                  child: Text(
                                    'This will be saved as: ${labelController.text.trim().isEmpty ? 'same as option name' : labelController.text.trim()}',
                                    style: const TextStyle(color: _muted, fontWeight: FontWeight.w700),
                                  ),
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ),
                  ),
                ),
                const Divider(height: 1, color: _line),
                Padding(
                  padding: const EdgeInsets.fromLTRB(22, 14, 22, 18),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
                      const SizedBox(width: 10),
                      FilledButton.icon(
                        icon: const Icon(Icons.save_rounded, size: 18),
                        onPressed: () {
                          if (!formKey.currentState!.validate()) return;
                          final label = labelController.text.trim();
                          final salary = num.tryParse(salaryController.text.trim());
                          Navigator.pop(dialogContext, {
                            'category': category,
                            'label': label,
                            'value': label,
                            'salary': referenceTypeFor(category).showSalary ? salary : null,
                            'sort_order': int.tryParse(sortController.text.trim()) ?? 0,
                            'is_active': isActive == 'true',
                          });
                        },
                        label: const Text('Save Reference'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    ),
  );

  labelController.dispose();
  salaryController.dispose();
  sortController.dispose();
  return result;
}

Future<void> saveReferenceRow(BuildContext context, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
  try {
    data['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from('hr_reference_options').insert(data);
      showSnack(context, 'Reference option added.');
    } else {
      await db.from('hr_reference_options').update(data).eq('id', id);
      showSnack(context, 'Reference option updated.');
    }
    refresh();
  } catch (e) {
    showSnack(context, 'Save failed: $e');
  }
}

void showSnack(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}
