param([Parameter(Mandatory=$true)][string]$Python)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
$pipTemp = Join-Path $projectRoot '.venv/pip-tmp'
$previousTemp, $previousTmp = $env:TEMP, $env:TMP
New-Item -ItemType Directory -Path $pipTemp -Force | Out-Null
try {
$env:TEMP, $env:TMP = $pipTemp, $pipTemp
$version = & $Python -c 'import sys; print("%s.%s" % sys.version_info[:2])'
if ($LASTEXITCODE -ne 0 -or $version -ne '3.12') { throw 'Use an existing Python 3.12 interpreter.' }
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $Python -m venv (Join-Path $projectRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'venv creation failed; global Python was not modified.' }
}
$check = & $venvPython -c 'import sys; print(sys.prefix != sys.base_prefix and sys.version_info[:2] == (3,12))'
if ($LASTEXITCODE -ne 0 -or $check -ne 'True') { throw 'Expected an isolated Python 3.12 venv.' }
& $venvPython -m pip --disable-pip-version-check install --only-binary=:all: -r (Join-Path $PSScriptRoot 'requirements-geometry.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $venvPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency validation failed.' }
Write-Output "Geometry interpreter: $venvPython"
} finally {
    $env:TEMP, $env:TMP = $previousTemp, $previousTmp
}
