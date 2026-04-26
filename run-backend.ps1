param(
    [int]$Port = 8000,
    [switch]$Reload
)

$projectRoot = $PSScriptRoot
$backendDir = Join-Path $projectRoot 'backend'
$pythonPath = Join-Path $backendDir 'venv\Scripts\python.exe'

if (-not (Test-Path $pythonPath)) {
    throw "Backend Python executable not found at $pythonPath. Create the backend venv first."
}

Set-Location $backendDir

$uvicornArgs = @(
    '-m', 'uvicorn',
    'app.main:app',
    '--app-dir', $backendDir,
    '--host', '127.0.0.1',
    '--port', $Port
)

if ($Reload) {
    $uvicornArgs += '--reload'
}

& $pythonPath @uvicornArgs