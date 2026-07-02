$ErrorActionPreference = 'Stop'

function Run-Patch($Path) {
  if (Test-Path $Path) {
    Write-Host "Running $Path ..." -ForegroundColor Cyan
    powershell -ExecutionPolicy Bypass -File $Path
  } else {
    Write-Host "Missing $Path" -ForegroundColor Yellow
  }
}

$root = Get-Location
$mainDart = Join-Path $root 'lib/main.dart'
if (-not (Test-Path $mainDart)) {
  throw 'Run this from the Flutter project root. lib/main.dart was not found.'
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = Join-Path $root "lib/main.dart.backup-$stamp"
Copy-Item $mainDart $backup
Write-Host "Backup created: $backup" -ForegroundColor Green

Run-Patch '.github/scripts/apply_contract_modal_update_local.ps1'
Run-Patch '.github/scripts/apply_evaluation_tabs_local.ps1'

Write-Host ''
Write-Host 'Checking applied markers...' -ForegroundColor Cyan
$updated = Get-Content $mainDart -Raw
$markers = @(
  'showContractDialog',
  'pickAndUploadContractPdf',
  'contractStatusFromEndDate',
  'EvaluationTypeTable',
  'DefaultTabController',
  'Superior Evaluation',
  'Peer-to-peer Evaluation',
  'Self Evaluation',
  'Student Evaluation'
)
foreach ($marker in $markers) {
  if ($updated.Contains($marker)) {
    Write-Host "OK: $marker" -ForegroundColor Green
  } else {
    Write-Host "MISSING: $marker" -ForegroundColor Red
  }
}

Write-Host ''
Write-Host 'Device sync patches completed. Next run:' -ForegroundColor Green
Write-Host 'dart format lib/main.dart'
Write-Host 'flutter clean'
Write-Host 'flutter pub get'
Write-Host 'flutter run -d edge'
