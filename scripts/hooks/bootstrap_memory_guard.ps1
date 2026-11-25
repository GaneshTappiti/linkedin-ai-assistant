$ErrorActionPreference = 'Stop'

$repoRoot = (Get-Location).Path
$stateDir = Join-Path $repoRoot '.qodo/state'
$statePath = Join-Path $stateDir 'memory_guard_state.json'

if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}

$required = @(
    'memory/normalized_2026-04-26/linkedin_master_export_deduped.json',
    'memory/normalized_2026-04-26/goals_vision_building_focus.json',
    'memory/normalized_2026-04-26/profile_comprehensive_analysis.json',
    'memory/normalized_2026-04-26/normalization_summary_report.json',
    'memory/normalized_2026-04-26/PERSONAL_SYNTHESIS_GANESH.md'
)

$missing = @()
$loadedFiles = @()

foreach ($rel in $required) {
    $abs = Join-Path $repoRoot $rel
    if (Test-Path $abs) {
        # Force file read during bootstrap.
        Get-Content -Path $abs -Raw | Out-Null
        $loadedFiles += $rel
    } else {
        $missing += $rel
    }
}

$loaded = ($missing.Count -eq 0)
$state = [ordered]@{
    loaded = $loaded
    loadedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    requiredCount = $required.Count
    loadedCount = $loadedFiles.Count
    loadedFiles = $loadedFiles
    missingFiles = $missing
}

$state | ConvertTo-Json -Depth 5 | Set-Content -Path $statePath -Encoding UTF8

if ($loaded) {
    @{ continue = $true; systemMessage = 'Memory guard: normalized bundle loaded and guard is active.' } | ConvertTo-Json -Compress
    exit 0
}

@{ continue = $true; systemMessage = ('Memory guard: BLOCK mode active. Missing files: ' + ($missing -join ', ')) } | ConvertTo-Json -Compress
exit 0
