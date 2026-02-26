@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ====================================================
echo   Star of Providence — Установка русского перевода
echo  ====================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "GF=steamapps\common\Star of Providence"
set "GAME_PATH="

REM --- Auto-detect: Steam path from Windows registry ---
set "STEAM_DIR="
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v "SteamPath" 2^>nul') do set "STEAM_DIR=%%B"

if defined STEAM_DIR (
    set "STEAM_DIR=!STEAM_DIR:/=\!"
    if exist "!STEAM_DIR!\!GF!\localization" set "GAME_PATH=!STEAM_DIR!\!GF!"
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
                if exist "!LIB!\!GF!\localization" set "GAME_PATH=!LIB!\!GF!"
            )
        )
    )
)

REM --- Auto-detect: scan all drives for SteamLibrary ---
if not defined GAME_PATH (
    for %%D in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        if not defined GAME_PATH (
            if exist "%%D:\SteamLibrary\!GF!\localization" set "GAME_PATH=%%D:\SteamLibrary\!GF!"
        )
    )
)

if defined GAME_PATH (
    echo  Игра найдена автоматически:
    echo  !GAME_PATH!
    echo.
    set /p "USE_AUTO=  Использовать этот путь? (y/n): "
    if /i "!USE_AUTO!"=="n" set "GAME_PATH="
)

if not defined GAME_PATH (
    echo  Укажите путь к папке игры Star of Providence.
    echo  Подсказка: ПКМ по игре в Steam ^> Управление ^> Обзор локальных файлов
    echo.
    set /p "GAME_PATH=  Путь: "
)

REM --- Validate input ---
if "!GAME_PATH!"=="" (
    echo.
    echo  [ОШИБКА] Путь не указан.
    echo.
    pause
    exit /b 1
)

set "GAME_PATH=!GAME_PATH:"=!"
if "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH:~0,-1!"

if not exist "!GAME_PATH!\localization" (
    echo.
    echo  [ОШИБКА] Папка localization не найдена в:
    echo  !GAME_PATH!
    echo.
    echo  Убедитесь, что путь ведет к корневой папке игры.
    echo.
    pause
    exit /b 1
)

REM --- Check patch files ---
if not exist "%SCRIPT_DIR%localization\*.csv" (
    echo.
    echo  [ОШИБКА] Файлы локализации не найдены в:
    echo  %SCRIPT_DIR%localization\
    echo.
    pause
    exit /b 1
)

REM --- Create backup ---
set "BACKUP_DIR=!GAME_PATH!\_backup_ru"

if not exist "!BACKUP_DIR!\localization\" (
    echo.
    echo  Создание резервной копии...
    mkdir "!BACKUP_DIR!\localization" 2>nul

    for %%F in ("!GAME_PATH!\localization\*.csv") do (
        copy /Y "%%F" "!BACKUP_DIR!\localization\" >nul
    )

    if exist "!GAME_PATH!\fonts\Chusung-220206.ttf" (
        mkdir "!BACKUP_DIR!\fonts" 2>nul
        copy /Y "!GAME_PATH!\fonts\Chusung-220206.ttf" "!BACKUP_DIR!\fonts\" >nul
    )

    echo  Бэкап создан: !BACKUP_DIR!
) else (
    echo.
    echo  Бэкап уже существует, пропускаем.
)

REM --- Install localization ---
echo.
echo  Установка файлов локализации...

set "COUNT=0"
for %%F in ("%SCRIPT_DIR%localization\*.csv") do (
    copy /Y "%%F" "!GAME_PATH!\localization\" >nul
    set /a COUNT+=1
)

echo  Скопировано CSV-файлов: !COUNT!

REM --- Install font ---
if exist "%SCRIPT_DIR%fonts\NotoSans-ExtraBold.ttf" (
    if exist "!GAME_PATH!\fonts\Chusung-220206.ttf" (
        copy /Y "%SCRIPT_DIR%fonts\NotoSans-ExtraBold.ttf" "!GAME_PATH!\fonts\Chusung-220206.ttf" >nul
        echo  Шрифт установлен.
    ) else (
        echo  [!] Файл Chusung-220206.ttf не найден в папке fonts игры.
    )
) else (
    echo  [!] Шрифт NotoSans-ExtraBold.ttf не найден в fonts/
    echo      Кириллический шрифт не установлен.
)

REM --- Done ---
echo.
echo  ====================================================
echo   Установка завершена!
echo.
echo   Запустите игру и выберите язык "русский"
echo   (заменяет слот китайского языка)
echo.
echo   Для восстановления оригинала: restore_backup.bat
echo  ====================================================
echo.

pause
