# ═══════════════════════════════════════════════════════════════════
# Ollama Configuration for clstr.in Outreach Agents
# ═══════════════════════════════════════════════════════════════════
# Run this BEFORE starting any outreach/inbox agent sessions.
#
# Usage:
#   .\scripts\ollama_config.ps1
#
# What it does:
#   1. Sets optimal Ollama environment variables for 16GB RAM systems
#   2. Kills any zombie Ollama processes
#   3. Validates that qwen2.5:7b is available
#   4. Restarts Ollama with optimized settings
# ═══════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Ollama Config — RAM Optimization for Agents" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Set Ollama environment variables ─────────────────────
Write-Host "[1/4] Setting Ollama environment variables..." -ForegroundColor Yellow

# Only load 1 model at a time (saves ~2-4GB RAM)
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "1", "User")
$env:OLLAMA_NUM_PARALLEL = "1"

# Only keep 1 model loaded (prevents stacking models in VRAM/RAM)
[System.Environment]::SetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "1", "User")
$env:OLLAMA_MAX_LOADED_MODELS = "1"

# Enable flash attention (reduces memory usage significantly)
[System.Environment]::SetEnvironmentVariable("OLLAMA_FLASH_ATTENTION", "1", "User")
$env:OLLAMA_FLASH_ATTENTION = "1"

Write-Host "  OLLAMA_NUM_PARALLEL=1" -ForegroundColor Green
Write-Host "  OLLAMA_MAX_LOADED_MODELS=1" -ForegroundColor Green
Write-Host "  OLLAMA_FLASH_ATTENTION=1" -ForegroundColor Green
Write-Host ""

# ── Step 2: Kill zombie Ollama processes ────────────────────────
Write-Host "[2/4] Checking for zombie Ollama processes..." -ForegroundColor Yellow

$ollamaProcesses = Get-Process -Name "ollama*" -ErrorAction SilentlyContinue
if ($ollamaProcesses) {
    Write-Host "  Found $($ollamaProcesses.Count) Ollama process(es). Stopping..." -ForegroundColor Yellow
    $ollamaProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  Stopped." -ForegroundColor Green
} else {
    Write-Host "  No zombie processes found." -ForegroundColor Green
}
Write-Host ""

# ── Step 3: Start Ollama fresh ──────────────────────────────────
Write-Host "[3/4] Starting Ollama with optimized settings..." -ForegroundColor Yellow

# Start Ollama server in background
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Check if it's running
$running = Get-Process -Name "ollama*" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "  Ollama server running (PID: $($running[0].Id))" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Could not start Ollama. Start manually with 'ollama serve'" -ForegroundColor Red
}
Write-Host ""

# ── Step 4: Validate model availability ─────────────────────────
Write-Host "[4/4] Validating model availability..." -ForegroundColor Yellow

try {
    $models = & ollama list 2>&1
    if ($models -match "qwen2.5:7b") {
        Write-Host "  ✓ qwen2.5:7b is available" -ForegroundColor Green
    } else {
        Write-Host "  ✗ qwen2.5:7b NOT found. Pull it with:" -ForegroundColor Red
        Write-Host "    ollama pull qwen2.5:7b" -ForegroundColor Yellow
    }

    # Warn about large models that might compete for resources
    $largeModels = @("14b", "32b", "70b", "r1")
    foreach ($lg in $largeModels) {
        if ($models -match $lg) {
            Write-Host "  ⚠ WARNING: Large model detected ($lg). Consider removing to free disk/RAM." -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  Could not check models. Make sure 'ollama' is in PATH." -ForegroundColor Red
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Configuration complete." -ForegroundColor Green
Write-Host "  RAM target: stay under 80% usage" -ForegroundColor Green
Write-Host "  Model: qwen2.5:7b (4096 ctx, 256 predict)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
