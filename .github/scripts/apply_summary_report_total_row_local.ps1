$ErrorActionPreference = 'Stop'

$mainDart = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$text = [System.IO.File]::ReadAllText($mainDart)
$original = $text

# Add an overall total helper for summary report rows.
if (-not $text.Contains('SummaryReportRow summaryGrandTotal')) {
  $marker = 'List<SummaryReportRow> bucketRows('
  $helper = @'
SummaryReportRow summaryGrandTotal(List<SummaryReportRow> rows) {
  return SummaryReportRow(
    label: 'TOTAL',
    total: rows.fold<int>(0, (sum, row) => sum + row.total),
    male: rows.fold<int>(0, (sum, row) => sum + row.male),
    female: rows.fold<int>(0, (sum, row) => sum + row.female),
  );
}

'@
  $index = $text.IndexOf($marker)
  if ($index -lt 0) { throw 'Could not find bucketRows insertion point.' }
  $text = $text.Insert($index, $helper)
}

# Make the preview show the grand total row first and style it clearly.
$text = $text.Replace(@'
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
'@, @'
  @override
  Widget build(BuildContext context) {
    final displayRows = rows.isEmpty
        ? const <SummaryReportRow>[]
        : <SummaryReportRow>[summaryGrandTotal(rows), ...rows];
    return Card(
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
            child: displayRows.isEmpty
                ? const EmptyBox()
                : ListView.separated(
                    itemCount: displayRows.length,
                    separatorBuilder: (_, __) => const Divider(height: 1, color: _line),
                    itemBuilder: (_, i) {
                      final row = displayRows[i];
                      final isTotal = i == 0;
                      final label = isTotal ? 'Grand Total' : '$keyLabel: ${row.label}';
                      return Container(
                        color: isTotal ? const Color(0xFFF8FAFC) : Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
                        child: Row(children: [
                          Expanded(flex: 2, child: Text(label, style: TextStyle(fontWeight: isTotal ? FontWeight.w900 : FontWeight.w800, color: _ink))),
                          Expanded(child: Text('Total: ${row.total}', style: TextStyle(color: _ink, fontWeight: isTotal ? FontWeight.w900 : FontWeight.w500))),
                          Expanded(child: Text('Male: ${row.male}', style: TextStyle(color: _ink, fontWeight: isTotal ? FontWeight.w900 : FontWeight.w500))),
                          Expanded(child: Text('Female: ${row.female}', style: TextStyle(color: _ink, fontWeight: isTotal ? FontWeight.w900 : FontWeight.w500))),
                        ]),
                      );
                    },
                  ),
          ),
        ]),
      ),
    );
  }
}
'@)

# Make printed summary reports also include the grand total row first.
$text = $text.Replace(@'
String buildPrintableSummaryReportHtml(String title, String keyLabel, List<SummaryReportRow> rows) {
  final body = rows
      .map((r) => '<tr><td>${escapeHtml('$keyLabel: ${r.label}')}</td><td>${escapeHtml('Total: ${r.total}')}</td><td>${escapeHtml('Male: ${r.male}')}</td><td>${escapeHtml('Female: ${r.female}')}</td></tr>')
      .join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 portrait;margin:14mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px;margin:0 0 12px}table{width:100%;border-collapse:collapse;font-size:12px}td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}td:first-child{font-weight:700;background:#f8fafc}</style></head><body><h1>${escapeHtml(title)}</h1><table><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}
'@, @'
String buildPrintableSummaryReportHtml(String title, String keyLabel, List<SummaryReportRow> rows) {
  final displayRows = rows.isEmpty
      ? const <SummaryReportRow>[]
      : <SummaryReportRow>[summaryGrandTotal(rows), ...rows];
  final body = displayRows.asMap().entries
      .map((entry) {
        final i = entry.key;
        final r = entry.value;
        final label = i == 0 ? 'Grand Total' : '$keyLabel: ${r.label}';
        final style = i == 0 ? ' class="grand-total"' : '';
        return '<tr$style><td>${escapeHtml(label)}</td><td>${escapeHtml('Total: ${r.total}')}</td><td>${escapeHtml('Male: ${r.male}')}</td><td>${escapeHtml('Female: ${r.female}')}</td></tr>';
      })
      .join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 portrait;margin:14mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px;margin:0 0 12px}table{width:100%;border-collapse:collapse;font-size:12px}td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}td:first-child{font-weight:700;background:#f8fafc}.grand-total td{font-weight:800;background:#eff6ff}</style></head><body><h1>${escapeHtml(title)}</h1><table><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}
'@)

if ($text -eq $original) {
  Write-Host 'No changes applied. Make sure the live summary reports patch has been applied first.'
  exit 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mainDart, $text, $utf8NoBom)
Write-Host 'Added Grand Total row to summary reports and printed reports.'
