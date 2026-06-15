param(
    [switch]$Clean,
    [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Resolve-Python {
    param([string]$Requested)
    if ($Requested -and (Test-Path $Requested)) {
        return (Resolve-Path $Requested).Path
    }
    $candidate = Join-Path $Root "venv310\Scripts\python.exe"
    if (Test-Path $candidate) {
        return (Resolve-Path $candidate).Path
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    throw "Python executable not found. Use -PythonExe to specify it."
}

function Remove-PathIfExists {
    param([string]$Path)
    if (Test-Path $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

$Python = Resolve-Python $PythonExe

if ($Clean) {
    Remove-PathIfExists (Join-Path $Root "build")
    Remove-PathIfExists (Join-Path $Root "dist")
}

& npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
& npm run build
if ($LASTEXITCODE -ne 0) { throw "frontend build failed" }

& $Python -m pip install --upgrade pip wheel "setuptools<81"
if ($LASTEXITCODE -ne 0) { throw "pip bootstrap failed" }
& $Python -m pip install -r requirements.txt -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "dependency install failed" }

& $Python -m PyInstaller Ideogram4Generator.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }

& $Python tools\write_runtime_report.py --package-dir dist\Ideogram4Generator --output dist\Ideogram4Generator\RUNTIME-CUDA-COMPATIBILITY.txt --require-cuda --require-bitsandbytes-cuda
if ($LASTEXITCODE -ne 0) { throw "runtime compatibility report failed" }

Write-Host "Portable build completed: dist\Ideogram4Generator"
