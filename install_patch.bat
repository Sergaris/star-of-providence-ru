@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "RUSSIFIER_VERSION=1.5"
set "GF=steamapps\common\Star of Providence"
set "GAME_PATH="

REM --- Auto-detect game path (silent) ---
set "STEAM_DIR="
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v "SteamPath" 2^>nul') do set "STEAM_DIR=%%B"

if defined STEAM_DIR (
    set "STEAM_DIR=!STEAM_DIR:/=\!"
    if exist "!STEAM_DIR!\!GF!\localization" set "GAME_PATH=!STEAM_DIR!\!GF!"
)

if not defined GAME_PATH if defined STEAM_DIR (
    set "VDF=!STEAM_DIR!\steamapps\libraryfolders.vdf"
    if exist "!VDF!" (
        for /f "usebackq tokens=1,*" %%A in (`findstr /c:"path" "!VDF!" 2^>nul`) do (
            if "%%~A"=="path" if not defined GAME_PATH (
                set "LIB=%%B"
                set "LIB=!LIB:"=!"
                set "LIB=!LIB:\\=\!"
                for /f "tokens=*" %%T in ("!LIB!") do set "LIB=%%T"
                if exist "!LIB!\!GF!\localization" set "GAME_PATH=!LIB!\!GF!"
            )
        )
    )
)

if not defined GAME_PATH (
    for %%D in (C D E F G H) do (
        if not defined GAME_PATH (
            if exist "%%D:\SteamLibrary\!GF!\localization" set "GAME_PATH=%%D:\SteamLibrary\!GF!"
        )
    )
)

if defined GAME_PATH (
    echo.
    echo  Найдена папка игры:
    echo  !GAME_PATH!
    echo.
    set /p "USE_AUTO=  Установить сюда? (Y/n): "
    if /i "!USE_AUTO!"=="n" set "GAME_PATH="
)

if not defined GAME_PATH (
    echo.
    echo  Укажите путь к папке Star of Providence.
    echo  ПКМ в Steam - Управление - Обзор локальных файлов
    echo.
    set /p "GAME_PATH=  Путь: "
)

if "!GAME_PATH!"=="" (
    echo.
    echo  [ОШИБКА] Путь не указан.
    pause
    exit /b 1
)

set "GAME_PATH=!GAME_PATH:"=!"
if "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH:~0,-1!"

if not exist "!GAME_PATH!\localization" (
    echo.
    echo  [ОШИБКА] В папке нет localization. Проверьте путь:
    echo  !GAME_PATH!
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%localization\*.csv" (
    echo.
    echo  [ОШИБКА] Нет файлов перевода в %SCRIPT_DIR%localization\
    pause
    exit /b 1
)

REM --- Check for newer russifier release via GitHub API (non-blocking) ---
set "RELEASE_CHECK="
for /f "delims=" %%R in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$local='!RUSSIFIER_VERSION!'; try { $r=Invoke-RestMethod -Uri 'https://api.github.com/repos/Sergaris/star-of-providence-ru/releases/latest' -Headers @{ 'User-Agent'='star-of-providence-ru-installer' } -TimeoutSec 10; $remote=($r.tag_name -replace '^[vV]','').Trim(); function ToVer([string]$s) { $s=$s.Trim().TrimStart('v','V'); $p=$s.Split('.'); $maj=[int]$p[0]; $min=0; $pat=0; if ($p.Length -gt 1) { [void][int]::TryParse($p[1],[ref]$min) }; if ($p.Length -gt 2) { [void][int]::TryParse($p[2],[ref]$pat) }; [version]::new($maj,$min,$pat) }; if ((ToVer $remote) -gt (ToVer $local)) { Write-Output ('UPDATE:'+$remote) } } catch { }" 2^>nul') do set "RELEASE_CHECK=%%R"
if defined RELEASE_CHECK (
    echo !RELEASE_CHECK! | findstr /b /c:"UPDATE:" >nul 2>&1
    if not errorlevel 1 (
        echo.
        echo  [!] Доступен более новый релиз русификатора: !RELEASE_CHECK:UPDATE:=!
        echo      У вас: v!RUSSIFIER_VERSION!
        echo      https://github.com/Sergaris/star-of-providence-ru/releases/latest
        echo      Установка продолжится с текущей версией.
        echo.
    )
)

REM --- Install (silent) ---
for %%F in ("%SCRIPT_DIR%localization\*.csv") do (
    copy /Y "%%F" "!GAME_PATH!\localization\" >nul 2>&1
)

if exist "%SCRIPT_DIR%fonts\NotoSans-ExtraBold.ttf" (
    if exist "!GAME_PATH!\fonts\Chusung-220206.ttf" (
        copy /Y "%SCRIPT_DIR%fonts\NotoSans-ExtraBold.ttf" "!GAME_PATH!\fonts\Chusung-220206.ttf" >nul 2>&1
    )
)

echo.
echo  Готово. Перевод v!RUSSIFIER_VERSION! установлен.
echo.
echo  Обязательно в игре:
echo    Опции - Язык - «русский»
echo    в том же меню - «8px» (не 16px)
echo.
echo  Без 8px возможны обрезка текста и ошибки в магазине.
echo.
pause
