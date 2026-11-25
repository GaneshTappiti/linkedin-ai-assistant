$ErrorActionPreference = 'Stop'

$repoRoot = (Get-Location).Path
$statePath = Join-Path $repoRoot '.qodo/state/memory_guard_state.json'

if (-not (Test-Path $statePath)) {
    @{
        hookSpecificOutput = @{
            hookEventName = 'PreToolUse'
            permissionDecision = 'deny'
            permissionDecisionReason = 'Blocked by memory guard: bootstrap state not initialized.'
        }
    } | ConvertTo-Json -Compress
    exit 2
}

$state = Get-Content -Path $statePath -Raw | ConvertFrom-Json

if ($null -eq $state.loaded -or -not $state.loaded) {
    $reason = 'Blocked by memory guard: required memory bundle not loaded. Missing files: '
    if ($null -ne $state.missingFiles -and $state.missingFiles.Count -gt 0) {
        $reason += ($state.missingFiles -join ', ')
    } else {
        $reason += 'unknown.'
    }

    @{
        hookSpecificOutput = @{
            hookEventName = 'PreToolUse'
            permissionDecision = 'deny'
            permissionDecisionReason = $reason
        }
    } | ConvertTo-Json -Compress
    exit 2
}

@{
    hookSpecificOutput = @{
        hookEventName = 'PreToolUse'
        permissionDecision = 'allow'
        permissionDecisionReason = 'Memory guard satisfied.'
    }
} | ConvertTo-Json -Compress
exit 0
