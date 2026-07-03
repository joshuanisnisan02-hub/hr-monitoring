$ErrorActionPreference = 'Stop'

$mainDart = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$text = [System.IO.File]::ReadAllText($mainDart)
$original = $text

$pattern = 'class ReportConfig \{[\s\S]*?\r?\nString buildPrintableReportHtml\([\s\S]*?\r?\n\}\s*\r?\n\r?\nList<EditField> employeeEditFields\(\) => const \['
$replacement = @'
class SummaryReportCategory {
  final String title;
  final String keyLabel;
  final Future<List<SummaryReportRow>> Function() load;
  const SummaryReportCategory(this.title, this.keyLabel, this.load);
}

class SummaryReportRow {
  final String label;
  final int total;
  final int male;
  final int female;
  const SummaryReportRow({required this.label, required this.total, this.male = 0, this.female = 0});
}

class _SummaryBucket {
  int total = 0;
  int male = 0;
  int female = 0;

  void add(String gender) {
    total++;
    final key = gender.trim().toLowerCase();
    if (key == 'male' || key == 'm') male++;
    if (key == 'female' || key == 'f') female++;
  }
}

class ResignedEmployeesPage extends StatelessWidget {
  const ResignedEmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Resigned Employees',
        subtitle:
            'Employees marked as resigned are separated from the active Employees table.',
        child: CrudTable(
          load: () => loadResignedEmployees(),
          searchHint:
              'Search resigned employee, bio number, type, date, or status',
          addLabel: 'Add Employee',
          allowAdd: false,
          reportTitle: 'Resigned Employees Report',
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('employee_type', 'Type'),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onView: viewEmployee,
          onEdit: editEmployee,
          showDelete: false,
          onDelete: (row) async {},
        ),
      );
}

class ReportsPage extends StatefulWidget {
  const ReportsPage({super.key});

  @override
  State<ReportsPage> createState() => _ReportsPageState();
}

class _ReportsPageState extends State<ReportsPage> {
  int selected = 0;

  List<SummaryReportCategory> get reports => [
        SummaryReportCategory('Contract Type Gender Summary Report', 'Type', loadContractTypeGenderSummary),
        SummaryReportCategory('Gender Summary Report', 'Gender', loadGenderSummary),
        SummaryReportCategory('Ranks Summary Report', 'Rank', loadRanksSummary),
        SummaryReportCategory('Type of License Summary Report', 'Type', loadLicenseTypeSummary),
        SummaryReportCategory('NC/TM Summary Report', 'Type', loadCertificateTypeSummary),
      ];

  Future<void> printCurrentReport(SummaryReportCategory config) async {
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final rows = await config.load();
      final markup = buildPrintableSummaryReportHtml(config.title, config.keyLabel, rows);
      final blob = html.Blob([markup], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      if (printWindow != null) {
        printWindow.location.href = url;
      } else {
        html.window.open(url, '_blank');
      }
    } catch (e) {
      if (mounted) showSnack(context, 'Print Failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final config = reports[selected];
    return PageFrame(
      title: 'Reports',
      subtitle: 'Print each summary category separately in two-column table format.',
      child: Column(children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(children: [
              SizedBox(
                width: 330,
                child: DropdownButtonFormField<int>(
                  value: selected,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Summary Category'),
                  items: [
                    for (var i = 0; i < reports.length; i++)
                      DropdownMenuItem(value: i, child: Text(reports[i].title, overflow: TextOverflow.ellipsis))
                  ],
                  onChanged: (v) => setState(() => selected = v ?? 0),
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                  onPressed: () => printCurrentReport(config),
                  icon: const Icon(Icons.print_rounded),
                  label: const Text('Print Report')),
              const SizedBox(width: 12),
              const Expanded(
                  child: Text('Select one category, then print that category as a simple two-column table.',
                      style: TextStyle(color: _muted, fontWeight: FontWeight.w600))),
            ]),
          ),
        ),
        const SizedBox(height: 14),
        Expanded(
          child: FutureBuilder<List<SummaryReportRow>>(
            key: ValueKey(selected),
            future: config.load(),
            builder: (context, snap) {
              if (snap.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snap.hasError) return ErrorBox('${snap.error}');
              final rows = snap.data ?? const <SummaryReportRow>[];
              return SummaryReportPreview(title: config.title, keyLabel: config.keyLabel, rows: rows);
            },
          ),
        ),
      ]),
    );
  }
}

Future<Map<String, String>> employeeGenderById() async {
  final employees = await loadEmployees(limit: 5000);
  final out = <String, String>{};
  for (final item in employees) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final id = '${row['id'] ?? ''}'.trim();
    if (id.isNotEmpty) out[id] = formatValue(row['gender']);
  }
  return out;
}

String reportCleanLabel(Object? value, String fallback) {
  final text = formatValue(value).trim();
  if (text.isEmpty || text == '-') return fallback;
  return text;
}

List<SummaryReportRow> bucketRows(Map<String, _SummaryBucket> buckets, {List<String> preferredOrder = const []}) {
  final keys = <String>[];
  for (final item in preferredOrder) {
    if (buckets.containsKey(item)) keys.add(item);
  }
  final remaining = buckets.keys.where((key) => !keys.contains(key)).toList()..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
  keys.addAll(remaining);
  return [
    for (final key in keys)
      SummaryReportRow(label: key, total: buckets[key]!.total, male: buckets[key]!.male, female: buckets[key]!.female),
  ];
}

Future<List<SummaryReportRow>> loadContractTypeGenderSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadContracts(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final type = reportCleanLabel(row['contract_type'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(type, () => _SummaryBucket()).add(gender);
  }
  for (final type in const ['Full-time', 'Full-time-Probationary', 'Part-time', 'Probationary', 'Compliance']) {
    buckets.putIfAbsent(type, () => _SummaryBucket());
  }
  return bucketRows(buckets, preferredOrder: const ['Full-time', 'Full-time-Probationary', 'Part-time', 'Probationary', 'Compliance']);
}

Future<List<SummaryReportRow>> loadGenderSummary() async {
  final employees = await loadActiveEmployees(limit: 5000);
  final buckets = <String, _SummaryBucket>{};
  for (final item in employees) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final gender = reportCleanLabel(row['gender'], 'Unspecified');
    buckets.putIfAbsent(gender, () => _SummaryBucket()).add(gender);
  }
  for (final gender in const ['Male', 'Female', 'Unspecified']) {
    buckets.putIfAbsent(gender, () => _SummaryBucket());
  }
  return bucketRows(buckets, preferredOrder: const ['Male', 'Female', 'Unspecified']);
}

Future<List<SummaryReportRow>> loadRanksSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadRankings(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final rank = reportCleanLabel(row['approved_rank_text'] ?? row['applied_rank_text'] ?? row['previous_rank_text'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(rank, () => _SummaryBucket()).add(gender);
  }
  return bucketRows(buckets);
}

Future<List<SummaryReportRow>> loadLicenseTypeSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadLicenses(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final type = reportCleanLabel(row['license_name'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(type, () => _SummaryBucket()).add(gender);
  }
  return bucketRows(buckets);
}

Future<List<SummaryReportRow>> loadCertificateTypeSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadCertificates(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final name = reportCleanLabel(row['certificate_name'] ?? row['certificate_type'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(name, () => _SummaryBucket()).add(gender);
  }
  return bucketRows(buckets);
}

class SummaryReportPreview extends StatelessWidget {
  final String title;
  final String keyLabel;
  final List<SummaryReportRow> rows;
  const SummaryReportPreview({super.key, required this.title, required this.keyLabel, required this.rows});

  @override
  Widget build(BuildContext context) => Card(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: Column(children: [
            Container(
                width: double.infinity,
                color: const Color(0xFFF8FAFC),
                padding: const EdgeInsets.all(16),
                child: Text('$title Preview', style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
            const Divider(height: 1, color: _line),
            Expanded(
              child: rows.isEmpty
                  ? const EmptyBox()
                  : ListView.separated(
                      itemCount: rows.length,
                      separatorBuilder: (_, __) => const Divider(height: 1, color: _line),
                      itemBuilder: (_, i) {
                        final row = rows[i];
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
                          child: Row(children: [
                            Expanded(flex: 2, child: Text('$keyLabel: ${row.label}', style: const TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                            Expanded(child: Text('Total: ${row.total}', style: const TextStyle(color: _ink, fontWeight: FontWeight.w500))),
                            Expanded(child: Text('Male: ${row.male}', style: const TextStyle(color: _ink, fontWeight: FontWeight.w500))),
                            Expanded(child: Text('Female: ${row.female}', style: const TextStyle(color: _ink, fontWeight: FontWeight.w500))),
                          ]),
                        );
                      },
                    ),
            ),
          ]),
        ),
      );
}

String buildPrintableSummaryReportHtml(String title, String keyLabel, List<SummaryReportRow> rows) {
  final body = rows
      .map((r) => '<tr><td>${escapeHtml('$keyLabel: ${r.label}')}</td><td>${escapeHtml('Total: ${r.total}')}</td><td>${escapeHtml('Male: ${r.male}')}</td><td>${escapeHtml('Female: ${r.female}')}</td></tr>')
      .join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 portrait;margin:14mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px;margin:0 0 12px}table{width:100%;border-collapse:collapse;font-size:12px}td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}td:first-child{font-weight:700;background:#f8fafc}</style></head><body><h1>${escapeHtml(title)}</h1><table><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}

List<EditField> employeeEditFields() => const [
'@

$text = [System.Text.RegularExpressions.Regex]::Replace($text, $pattern, $replacement, 1)

if ($text -eq $original) {
  Write-Host 'No changes applied. Report block may already be updated or expected block was not found.'
  exit 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mainDart, $text, $utf8NoBom)
Write-Host 'Applied live-system style summary reports to lib/main.dart.'
