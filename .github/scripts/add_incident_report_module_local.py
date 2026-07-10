from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Add loader near other loaders.
if 'Future<List<dynamic>> loadIncidentReports' not in text:
    marker = 'Future<List<dynamic>> loadRankings({int limit = 1500})'
    loader = """Future<List<dynamic>> loadIncidentReports({int limit = 1500}) => db
    .from('incident_reports')
    .select(
        'id, employee_id, ir, date_submitted, nte_date_received, explanation_date_submitted, nod, date_received, employees(full_name)')
    .order('date_submitted', ascending: false)
    .limit(limit);

"""
    if marker not in text:
        raise SystemExit('Could not find loader insertion point.')
    text = text.replace(marker, loader + marker, 1)

# Add page to ShellPage before Reports.
text = text.replace(
    """      const RankingPage(),
      const ReportsPage(),""",
    """      const RankingPage(),
      const IncidentReportPage(),
      const ReportsPage(),""",
    1,
)

# Add sidebar item before Reports.
text = text.replace(
    """      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Reports', Icons.summarize_rounded),""",
    """      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Incident Report', Icons.report_problem_rounded),
      NavItem('Reports', Icons.summarize_rounded),""",
    1,
)

# Insert page and dialogs before ReportsPage class.
if 'class IncidentReportPage' not in text:
    marker = 'class ReportsPage extends StatelessWidget'
    module = r'''
class IncidentReportPage extends StatelessWidget {
  const IncidentReportPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Incident Report',
        subtitle:
            'Track employee IR, NTE, explanation deadline, NOD, and received dates.',
        child: CrudTable(
          load: () => activeOnlyRows(loadIncidentReports()),
          searchHint: 'Search employee, IR, NTE, explanation, or NOD',
          addLabel: 'Add Incident Report',
          reportTitle: 'Incident Report',
          archiveTableName: 'incident_reports',
          archiveModuleName: 'Incident Report',
          columns: const [
            GridCol('employee_name', 'Employee', flex: 3, primary: true),
            GridCol('ir', 'IR', flex: 2),
            GridCol('date_submitted', 'Date Submitted', flex: 2),
            GridCol('nte_date_received', 'NTE Date Received', flex: 2),
            GridCol('explanation_date_submitted',
                'Explanation Date Submitted',
                flex: 2),
            GridCol('nod', 'NOD', flex: 2),
            GridCol('date_received', 'Date Received', flex: 2),
          ],
          onAdd: (ctx, refresh) => editIncidentReport(ctx, null, refresh),
          onView: viewIncidentReport,
          onEdit: editIncidentReport,
          onDelete: (row) =>
              db.from('incident_reports').delete().eq('id', row['id']),
        ),
      );
}

String? incidentReportComputedExplanationDate(String nteText) {
  final parsed = parseFlexibleDate(nteText);
  if (parsed == null) return null;
  return DateFormat('yyyy-MM-dd').format(parsed.add(const Duration(days: 3)));
}

String incidentReportDisplayDate(String? isoText) {
  if (isoText == null || isoText.trim().isEmpty) return '';
  final parsed = parseFlexibleDate(isoText.trim());
  if (parsed == null) return isoText;
  return DateFormat('MMMM dd, yyyy').format(parsed);
}

Future<Map<String, dynamic>?> showIncidentReportDialog(
    BuildContext context, Map<String, dynamic>? row) async {
  final isAdd = row == null;
  final source = normalizeRow(row ?? {});
  final employees = await employeeOptions();
  String? employeeId = isAdd ? null : source['employee_id']?.toString();
  final ir = TextEditingController(text: formatEditValue(source['ir']));
  final dateSubmitted =
      TextEditingController(text: formatEditValue(source['date_submitted']));
  final nteDateReceived = TextEditingController(
      text: formatEditValue(source['nte_date_received']));
  final explanationDate = TextEditingController(
      text: incidentReportDisplayDate(
          formatEditValue(source['explanation_date_submitted'])));
  final nod = TextEditingController(text: formatEditValue(source['nod']));
  final dateReceived =
      TextEditingController(text: formatEditValue(source['date_received']));
  final formKey = GlobalKey<FormState>();

  void recomputeExplanationDate() {
    final computed = incidentReportComputedExplanationDate(nteDateReceived.text);
    explanationDate.text = incidentReportDisplayDate(computed);
  }

  if (explanationDate.text.trim().isEmpty &&
      nteDateReceived.text.trim().isNotEmpty) {
    recomputeExplanationDate();
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Incident Report' : 'Edit Incident Report'),
        content: SizedBox(
          width: 820,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const DialogSectionTitle('Employee Information'),
                  if (isAdd)
                    employeeAutocompleteField(
                      employees: employees,
                      employeeId: employeeId,
                      width: 728,
                      onEmployeeChanged: (value) =>
                          setDialogState(() => employeeId = value),
                    )
                  else
                    ReadOnlyEmployeeBox(linkedEmployeeName(source)),
                  const SizedBox(height: 16),
                  const DialogSectionTitle('Incident Report Information'),
                  Wrap(spacing: 14, runSpacing: 14, children: [
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: ir,
                        decoration: const InputDecoration(labelText: 'IR'),
                        validator: (value) =>
                            value == null || value.trim().isEmpty
                                ? 'Required'
                                : null,
                      ),
                    ),
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: dateSubmitted,
                        decoration: const InputDecoration(
                            labelText: 'Date Submitted',
                            hintText: 'January 02, 2026',
                            suffixIcon: Icon(Icons.calendar_month_rounded)),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Required';
                          }
                          if (parseFlexibleDate(value.trim()) == null) {
                            return 'Use January 02, 2026 or MM/DD/YYYY';
                          }
                          return null;
                        },
                      ),
                    ),
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: nteDateReceived,
                        decoration: const InputDecoration(
                            labelText: 'NTE Date Received',
                            hintText: 'January 02, 2026',
                            suffixIcon: Icon(Icons.calendar_month_rounded)),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Required';
                          }
                          if (parseFlexibleDate(value.trim()) == null) {
                            return 'Use January 02, 2026 or MM/DD/YYYY';
                          }
                          return null;
                        },
                        onChanged: (_) => setDialogState(recomputeExplanationDate),
                      ),
                    ),
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: explanationDate,
                        readOnly: true,
                        decoration: const InputDecoration(
                          labelText: 'Explanation Date Submitted',
                          helperText: 'Auto-computed: 3 days after NTE date',
                          suffixIcon: Icon(Icons.auto_fix_high_rounded),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: nod,
                        decoration: const InputDecoration(labelText: 'NOD'),
                      ),
                    ),
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: dateReceived,
                        decoration: const InputDecoration(
                            labelText: 'Date Received',
                            hintText: 'January 02, 2026',
                            suffixIcon: Icon(Icons.calendar_month_rounded)),
                        validator: (value) {
                          final clean = '${value ?? ''}'.trim();
                          if (clean.isEmpty) return null;
                          if (parseFlexibleDate(clean) == null) {
                            return 'Use January 02, 2026 or MM/DD/YYYY';
                          }
                          return null;
                        },
                      ),
                    ),
                  ]),
                ],
              ),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              recomputeExplanationDate();
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, <String, dynamic>{
                if (isAdd) 'employee_id': employeeId,
                'ir': ir.text.trim(),
                'date_submitted': toIsoDateInput(dateSubmitted.text),
                'nte_date_received': toIsoDateInput(nteDateReceived.text),
                'explanation_date_submitted':
                    incidentReportComputedExplanationDate(nteDateReceived.text),
                'nod': nod.text.trim(),
                'date_received': toIsoDateInput(dateReceived.text),
              }..removeWhere((_, value) =>
                  value == null || value.toString().trim().isEmpty));
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final controller in [
    ir,
    dateSubmitted,
    nteDateReceived,
    explanationDate,
    nod,
    dateReceived,
  ]) {
    controller.dispose();
  }
  return result;
}

Future<void> editIncidentReport(BuildContext context,
    Map<String, dynamic>? row, VoidCallback refresh) async {
  final data = await showIncidentReportDialog(context, row);
  if (data == null) return;
  await saveRow(context, 'incident_reports', row == null ? null : row['id'],
      data, refresh);
}

Future<void> viewIncidentReport(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title:
          Text('Incident Report - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Incident Report Information', normalized, const {
              'Employee': 'employee_name',
              'IR': 'ir',
              'Date Submitted': 'date_submitted',
              'NTE Date Received': 'nte_date_received',
              'Explanation Date Submitted': 'explanation_date_submitted',
              'NOD': 'nod',
              'Date Received': 'date_received',
            }),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close')),
      ],
    ),
  );
}

'''
    if marker not in text:
        raise SystemExit('Could not find ReportsPage insertion point.')
    text = text.replace(marker, module + marker, 1)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Incident Report module may already be present.')
else:
    print('Added Incident Report module and auto-computed explanation date.')
