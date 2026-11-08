$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot ".venv312\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $PythonPath)) {
    Write-Host "Creating Python 3.12 virtual environment..."
    & py -3.12 -m venv (Join-Path $ProjectRoot ".venv312")
    if ($LASTEXITCODE -ne 0) { throw "Could not create .venv312. Confirm Python 3.12 is installed." }
}

& $PythonPath -c "import fastapi, uvicorn, tensorflow, torch, ultralytics, numpy, PIL" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing project dependencies. The initial install may take several minutes..."
    & $PythonPath -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Could not upgrade pip." }
    & $PythonPath -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
}

Write-Host "Starting FabricAI at http://127.0.0.1:8000 (press Ctrl+C to stop)."
& $PythonPath -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
