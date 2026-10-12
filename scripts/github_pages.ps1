param([string]$Repository = 'Moveath/myologiya-3d')
$ErrorActionPreference = 'Stop'
$atlasRoot = Split-Path $PSScriptRoot -Parent
$atlasPages = Join-Path $atlasRoot '.pages'
$atlasPython = Join-Path $atlasRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $atlasPython)) { $atlasPython = 'python' }
if (!(Test-Path -LiteralPath (Join-Path $atlasPages '.git'))) {
    New-Item -ItemType Directory -Path $atlasPages -Force | Out-Null
    git -C $atlasPages init -b gh-pages
    if ($LASTEXITCODE) { throw 'git init failed' }
    git -C $atlasPages remote add origin "https://github.com/$Repository.git"
}
& $atlasPython (Join-Path $PSScriptRoot 'package_site.py') $atlasPages
if ($LASTEXITCODE) { throw 'Static build failed' }
git -C $atlasPages config user.name Moveath
git -C $atlasPages config user.email '249351385+Moveath@users.noreply.github.com'
git -C $atlasPages add --all
git -C $atlasPages diff --cached --quiet
if ($LASTEXITCODE -eq 1) { git -C $atlasPages commit -m 'Publish anatomy atlas' }
git -C $atlasPages push -u origin gh-pages
if ($LASTEXITCODE) { throw 'Pages push failed' }
