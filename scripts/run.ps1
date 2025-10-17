Param(
    [switch]$Api,
    [switch]$DryRun,
    [string]$Preset = "fluxconvert/presets/web-1080p.yaml",
    [int]$Port = 7845
)

$ErrorActionPreference = "Stop"

function Ensure-Venv {
    if (-not (Test-Path ".venv")) {
        Write-Host "[setup] Creating virtual environment..."
        python -m venv .venv
    }
}

function Ensure-Dependencies {
    Write-Host "[setup] Installing dependencies (editable)..."
    .\.venv\Scripts\pip install -e ".[dev]" | Out-Null
}

function Activate-Venv {
    $venvActivate = ".\.venv\Scripts\Activate.ps1"
    if (-not (Test-Path $venvActivate)) {
        throw "Virtual environment activation script not found."
    }
    & $venvActivate
}

# Bootstrap
Ensure-Venv
Activate-Venv
Ensure-Dependencies

if ($Api -or (-not $DryRun)) {
    Write-Host "[run] Starting API on port $Port..."
    fluxconvert api --port $Port
    exit $LASTEXITCODE
}

if ($DryRun) {
    Write-Host "[run] Dry-running preset: $Preset"
    fluxconvert dry-run $Preset
    exit $LASTEXITCODE
}

