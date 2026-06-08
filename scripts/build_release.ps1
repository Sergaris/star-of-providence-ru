# Собирает zip для GitHub Release: fonts/, localization/, install_patch.bat
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$version = (Get-Content (Join-Path $root "install_patch.bat") -Encoding UTF8 |
    Where-Object { $_ -match 'set "RUSSIFIER_VERSION=(.+)"' } |
    ForEach-Object { if ($_ -match 'set "RUSSIFIER_VERSION=(.+)"') { $Matches[1] } } |
    Select-Object -First 1)
if (-not $version) {
    throw "Не найдена RUSSIFIER_VERSION в install_patch.bat"
}

$outDir = Join-Path $env:TEMP "star-of-providence-ru-v$version"
$zipPath = Join-Path $root "star-of-providence-ru-v$version.zip"

if (Test-Path $outDir) { Remove-Item $outDir -Recurse -Force }
New-Item -ItemType Directory -Path $outDir | Out-Null

Copy-Item (Join-Path $root "install_patch.bat") $outDir
Copy-Item (Join-Path $root "fonts") (Join-Path $outDir "fonts") -Recurse
Copy-Item (Join-Path $root "localization") (Join-Path $outDir "localization") -Recurse

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $outDir "*") -DestinationPath $zipPath -Force
Remove-Item $outDir -Recurse -Force

Write-Host "Готово: $zipPath"
