# Собирает zip для GitHub Release: fonts/, localization/, install_patch.bat, VERSION
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$versionFile = Join-Path $root "VERSION"
if (-not (Test-Path $versionFile)) {
    throw "Не найден файл VERSION"
}
$version = (Get-Content $versionFile -Encoding UTF8 -TotalCount 1).Trim().TrimStart('v', 'V')
if (-not $version) {
    throw "Файл VERSION пуст"
}

$outDir = Join-Path $env:TEMP "star-of-providence-ru-v$version"
$zipPath = Join-Path $root "star-of-providence-ru-v$version.zip"

if (Test-Path $outDir) { Remove-Item $outDir -Recurse -Force }
New-Item -ItemType Directory -Path $outDir | Out-Null

Copy-Item (Join-Path $root "install_patch.bat") $outDir
Copy-Item $versionFile $outDir
Copy-Item (Join-Path $root "fonts") (Join-Path $outDir "fonts") -Recurse
Copy-Item (Join-Path $root "localization") (Join-Path $outDir "localization") -Recurse

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $outDir "*") -DestinationPath $zipPath -Force
Remove-Item $outDir -Recurse -Force

Write-Host "Готово: $zipPath"
