$ErrorActionPreference = 'Stop'

$mainDart = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$text = [System.IO.File]::ReadAllText($mainDart)
if ($text.Contains('String buildPrintableReportHtml(')) {
  Write-Host 'buildPrintableReportHtml already exists. No changes needed.'
  exit 0
}

$function = @'
String buildPrintableReportHtml(
    String title, List<GridCol> columns, List<Map<String, dynamic>> rows) {
  final cols = columns.map((c) => '<th>${escapeHtml(c.label)}</th>').join();
  final body = rows.map((r) {
    final cells = columns.map((c) {
      final raw = valueFor(r, c.key);
      final value = c.isMoney ? formatMoney(raw) : formatValue(raw);
      return '<td>${escapeHtml(value)}</td>';
    }).join();
    return '<tr>$cells</tr>';
  }).join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 landscape;margin:12mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #cbd5e1;padding:6px;text-align:left;vertical-align:top}th{background:#eff6ff}</style></head><body><h1>${escapeHtml(title)}</h1><table><thead><tr>$cols</tr></thead><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}

'@

$marker = 'String buildPrintableSummaryReportHtml('
$index = $text.IndexOf($marker)
if ($index -lt 0) {
  throw 'Could not find buildPrintableSummaryReportHtml insertion point.'
}

$text = $text.Insert($index, $function)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mainDart, $text, $utf8NoBom)
Write-Host 'Restored buildPrintableReportHtml for existing table Print buttons.'
