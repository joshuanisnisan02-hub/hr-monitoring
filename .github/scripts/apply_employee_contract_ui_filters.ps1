$ErrorActionPreference = 'Stop'

$mainPath = Join-Path (Get-Location) 'lib/main.dart'
if (-not (Test-Path $mainPath)) {
  throw 'Run this script from the hr-monitoring project root.'
}

$text = Get-Content $mainPath -Raw

function Find-BlockEnd {
  param([string]$Source, [int]$Start)
  $brace = $Source.IndexOf('{', $Start)
  if ($brace -lt 0) { return -1 }
  $depth = 0
  $quote = [char]0
  $escape = $false
  for ($i = $brace; $i -lt $Source.Length; $i++) {
    $ch = $Source[$i]
    if ($quote -ne [char]0) {
      if ($escape) { $escape = $false }
      elseif ($ch -eq '\') { $escape = $true }
      elseif ($ch -eq $quote) { $quote = [char]0 }
    } else {
      if ($ch -eq '"' -or $ch -eq "'") { $quote = $ch }
      elseif ($ch -eq '{') { $depth++ }
      elseif ($ch -eq '}') {
        $depth--
        if ($depth -eq 0) { return $i + 1 }
      }
    }
  }
  return -1
}

function Replace-Function {
  param([string]$Source, [string]$Signature, [string]$Replacement)
  $start = $Source.IndexOf($Signature)
  if ($start -lt 0) { return $Source }
  $end = Find-BlockEnd -Source $Source -Start $start
  if ($end -lt 0) { throw "Could not find end of function $Signature" }
  return $Source.Substring(0, $start) + $Replacement.Trim() + $Source.Substring($end)
}

# Fix old named-parameter damage if present.
foreach ($name in @('textAlign','alignment','mainAxisAlignment','crossAxisAlignment','verticalDirection','textDirection','clipBehavior')) {
  $text = $text.Replace("$name(", "$name`:")
}
$text = $text.Replace("Align:`n", "Align(`n")

# Remove duplicate loadResignedEmployees definitions: keep first only.
$signature = 'Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {'
$positions = @()
$searchStart = 0
while ($true) {
  $pos = $text.IndexOf($signature, $searchStart)
  if ($pos -lt 0) { break }
  $positions += $pos
  $searchStart = $pos + $signature.Length
}
if ($positions.Count -gt 1) {
  for ($idx = $positions.Count - 1; $idx -ge 1; $idx--) {
    $pos = $positions[$idx]
    $end = Find-BlockEnd -Source $text -Start $pos
    if ($end -lt 0) { throw 'Could not remove duplicate loadResignedEmployees.' }
    while ($end -lt $text.Length -and " `t`r`n".Contains($text[$end])) { $end++ }
    $text = $text.Substring(0, $pos) + $text.Substring($end)
  }
}

# Insert active/resigned helpers if missing.
$helperMarker = 'Future<List<dynamic>> loadAppointments({int limit = 5000})'
$helperCode = @'
bool isResignedText(Object? value) {
  final text = '${value ?? ''}'.toLowerCase();
  return text.contains('resign');
}

bool rowHasResignedStatus(Map<String, dynamic> row) {
  return isResignedText(row['employment_status']) ||
      isResignedText(row['employee_status']) ||
      isResignedText(row['status']) ||
      isResignedText(row['latest_status']) ||
      isResignedText(row['contract_status']);
}

Future<Set<String>> loadResignedEmployeeIdSet() async {
  final ids = <String>{};
  try {
    final employees = await db
        .from('employees')
        .select('id, employment_status, employee_status, status, latest_status')
        .limit(5000);
    for (final item in employees) {
      final row = Map<String, dynamic>.from(item as Map);
      if (rowHasResignedStatus(row)) ids.add('${row['id']}');
    }
  } catch (_) {}
  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, status')
        .limit(5000);
    for (final item in contracts) {
      final row = Map<String, dynamic>.from(item as Map);
      if (isResignedText(row['status'])) ids.add('${row['employee_id']}');
    }
  } catch (_) {}
  ids.removeWhere((value) => value.trim().isEmpty || value == 'null');
  return ids;
}

String rowEmployeeId(Map<String, dynamic> row) {
  final raw = row['employee_id'] ?? row['id'];
  return '${raw ?? ''}'.trim();
}

Future<List<dynamic>> activeOnlyRows(Future<List<dynamic>> source) async {
  final rows = await source;
  final resignedIds = await loadResignedEmployeeIdSet();
  return rows.where((item) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final id = rowEmployeeId(row);
    if (id.isNotEmpty && resignedIds.contains(id)) return false;
    if (rowHasResignedStatus(row)) return false;
    return true;
  }).toList();
}

Future<List<dynamic>> loadActiveEmployees({int limit = 5000}) =>
    activeOnlyRows(loadEmployees(limit: limit));

'@
if (-not $text.Contains('Future<Set<String>> loadResignedEmployeeIdSet()')) {
  $insert = $text.IndexOf($helperMarker)
  if ($insert -ge 0) { $text = $text.Substring(0, $insert) + $helperCode + $text.Substring($insert) }
}

# Remove Employee Matching card from Employees page.
$empStart = $text.IndexOf('class EmployeesPage')
$empEnd = $text.IndexOf('class ContractsPage', $empStart)
if ($empStart -ge 0 -and $empEnd -gt $empStart) {
  $emp = $text.Substring($empStart, $empEnd - $empStart)
  $marker = $emp.IndexOf('Excel Employee Matching')
  if ($marker -ge 0) {
    $cardStart = $emp.LastIndexOf('          Card(', $marker)
    if ($cardStart -ge 0) {
      $cardEnd = Find-BlockEnd -Source $emp -Start $cardStart
      if ($cardEnd -gt $cardStart) {
        $j = $cardEnd
        while ($j -lt $emp.Length -and " `t`r`n,".Contains($emp[$j])) { $j++ }
        $spacer = 'const SizedBox(height: 14),'
        if ($j + $spacer.Length -le $emp.Length -and $emp.Substring($j, $spacer.Length) -eq $spacer) {
          $j += $spacer.Length
          while ($j -lt $emp.Length -and " `t`r`n,".Contains($emp[$j])) { $j++ }
        }
        $emp = $emp.Substring(0, $cardStart) + $emp.Substring($j)
      }
    }
  }

  # Replace Employees loader with active-only loader.
  $methodSig = '  Future<List<dynamic>> _loadEmployees() async {'
  $mStart = $emp.IndexOf($methodSig)
  if ($mStart -ge 0) {
    $mEnd = Find-BlockEnd -Source $emp -Start $mStart
    if ($mEnd -gt $mStart) {
      $newMethod = @'
  Future<List<dynamic>> _loadEmployees() async {
    final rows = await loadActiveEmployees(limit: 5000);
    if (genderFilter == 'All') return rows;
    return rows
        .where((item) => _matchesGenderFilter(
            normalizeRow(Map<String, dynamic>.from(item as Map))))
        .toList();
  }
'@
      $emp = $emp.Substring(0, $mStart) + $newMethod.TrimEnd() + $emp.Substring($mEnd)
    }
  }
  $text = $text.Substring(0, $empStart) + $emp + $text.Substring($empEnd)
}

# Replace employeeOptions so all employee dropdowns hide resigned employees.
$employeeOptions = @'
Future<List<EditOption>> employeeOptions() async {
  final rows = await loadActiveEmployees(limit: 5000);
  final options = rows
      .map((item) {
        final row = normalizeRow(Map<String, dynamic>.from(item as Map));
        return EditOption('${row['id']}', formatValue(row['full_name']));
      })
      .where((option) => option.value.trim().isNotEmpty && option.label != '-')
      .toList();
  options.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return uniqueOptions(options);
}
'@
if ($text.Contains('Future<List<EditOption>> employeeOptions() async')) {
  $text = Replace-Function -Source $text -Signature 'Future<List<EditOption>> employeeOptions() async' -Replacement $employeeOptions
}

# Contracts table and report must hide resigned employees.
$text = $text.Replace('load: () => loadContracts(),', 'load: () => activeOnlyRows(loadContracts()),')
$text = $text.Replace("ReportConfig('Contract Monitoring Report',`r`n            () => loadContracts(limit: 5000),", "ReportConfig('Contract Monitoring Report',`r`n            () => activeOnlyRows(loadContracts(limit: 5000)),")
$text = $text.Replace("ReportConfig('Contract Monitoring Report',`n            () => loadContracts(limit: 5000),", "ReportConfig('Contract Monitoring Report',`n            () => activeOnlyRows(loadContracts(limit: 5000)),")

# Keep Resigned module unfiltered if old scripts touched it.
$text = $text.Replace('load: () => activeOnlyRows(loadResignedEmployees()),', 'load: () => loadResignedEmployees(),')

Set-Content $mainPath $text -Encoding UTF8
Write-Host 'Applied Employees and Contracts modifications:'
Write-Host '- Employee Matching card removed'
Write-Host '- Employees table hides resigned employees'
Write-Host '- Contract table hides resigned employees'
Write-Host '- Contract Add dropdown hides resigned employees'
