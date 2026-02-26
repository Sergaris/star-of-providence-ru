@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ====================================================
echo   Star of Providence — Восстановление оригинала
echo  ====================================================
echo.

set "GF=steamapps\common\Star of Providence"
set "GAME_PATH="

REM --- Auto-detect: Steam path from Windows registry ---
set "STEAM_DIR="
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v "SteamPath" 2^>nul') do set "STEAM_DIR=%%B"

if defined STEAM_DIR (
    set "STEAM_DIR=!STEAM_DIR:/=\!"
    if exist "!STEAM_DIR!\!GF!\_backup_ru\localization\" set "GAME_PATH=!STEAM_DIR!\!GF!"
)

REM --- Auto-detect: parse Steam library folders from libraryfolders.vdf ---
if not defined GAME_PATH if defined STEAM_DIR (
    set "VDF=!STEAM_DIR!\steamapps\libraryfolders.vdf"
    if exist "!VDF!" (
        for /f "usebackq tokens=1,*" %%A in (`findstr /c:"path" "!VDF!" 2^>nul`) do (
            if "%%~A"=="path" if not defined GAME_PATH (
                set "LIB=%%B"
                set "LIB=!LIB:"=!"
                set "LIB=!LIB:\\=\!"
                for /f "tokens=*" %%T in ("!LIB!") do set "LIB=%%T"
                if exist "!LIB!\!GF!\_backup_ru\localization\" set "GAME_PATH=!LIB!\!GF!"
            )
        )
    )
)

REM --- Auto-detect: scan all drives for SteamLibrary ---
if not defined GAME_PATH (
    for %%D in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        if not defined GAME_PATH (
            if exist "%%D:\SteamLibrary\!GF!\_backup_ru\localization\" set "GAME_PATH=%%D:\SteamLibrary\!GF!"
        )
    )
)

if defined GAME_PATH (
    echo  Игра с бэкапом найдена автоматически:
    echo  !GAME_PATH!
    echo.
    set /p "USE_AUTO=  Использовать этот путь? (y/n): "
    if /i "!USE_AUTO!"=="n" set "GAME_PATH="
)

if not defined GAME_PATH (
    echo  Укажите путь к папке игры Star of Providence.
    echo.
    set /p "GAME_PATH=  Путь: "
)

if "!GAME_PATH!"=="" (
    echo.
    echo  [ОШИБКА] Путь не указан.
    echo.
    pause
    exit /b 1
)

set "GAME_PATH=!GAME_PATH:"=!"
if "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH:~0,-1!"

REM --- Check backup ---
set "BACKUP_DIR=!GAME_PATH!\_backup_ru"

if not exist "!BACKUP_DIR!\localization\" (
    echo.
    echo  [ОШИБКА] Резервная копия не найдена в:
    echo  !BACKUP_DIR!
    echo.
    echo  Бэкап создается автоматически при установке через install_patch.bat
    echo.
    pause
    exit /b 1
)

REM --- Restore files ---
echo  Восстановление файлов...

set "COUNT=0"
for %%F in ("!BACKUP_DIR!\localization\*.csv") do (
    copy /Y "%%F" "!GAME_PATH!\localization\" >nul
    set /a COUNT+=1
)
echo  Восстановлено CSV-файлов: !COUNT!

if exist "!BACKUP_DIR!\fonts\Chusung-220206.ttf" (
    copy /Y "!BACKUP_DIR!\fonts\Chusung-220206.ttf" "!GAME_PATH!\fonts\" >nul
    echo  Шрифт восстановлен.
)

REM --- Optionally remove backup ---
echo.
set /p "DEL_BACKUP=  Удалить папку бэкапа? (y/n): "
if /i "!DEL_BACKUP!"=="y" (
    rmdir /s /q "!BACKUP_DIR!" 2>nul
    echo  Бэкап удалён.
)

echo.
echo  ====================================================
echo   Оригинальные файлы восстановлены!
echo  ====================================================
echo.

pause
