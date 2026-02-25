@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ====================================================
echo   Star of Providence - Установка русского перевода
echo  ====================================================
echo.

set "SCRIPT_DIR=%~dp0"

:: ── Ввод пути к игре ──
echo  Укажите путь к папке игры Star of Providence.
echo  Подсказка: ПКМ по игре в Steam ^> Управление ^> Обзор локальных файлов
echo.
set /p "GAME_PATH=  Путь: "

:: Проверяем пустой ввод
if "%GAME_PATH%"=="" (
    echo.
    echo  [ОШИБКА] Путь не указан.
    echo.
    pause
    exit /b 1
)

:: Убираем кавычки если есть
set "GAME_PATH=%GAME_PATH:"=%"

:: Убираем завершающий слэш
if "%GAME_PATH:~-1%"=="\" set "GAME_PATH=%GAME_PATH:~0,-1%"

:: ── Валидация ──
if not exist "%GAME_PATH%\localization" (
    echo.
    echo  [ОШИБКА] Папка localization не найдена в:
    echo  %GAME_PATH%
    echo.
    echo  Убедитесь, что путь ведет к корневой папке игры.
    echo.
    pause
    exit /b 1
)

:: ── Проверяем наличие файлов патча ──
if not exist "%SCRIPT_DIR%localization\*.csv" (
    echo.
    echo  [ОШИБКА] Файлы локализации не найдены в:
    echo  %SCRIPT_DIR%localization\
    echo.
    echo  Сначала выполните: python scripts/patch.py init
    echo.
    pause
    exit /b 1
)

:: ── Создание бэкапа ──
set "BACKUP_DIR=%GAME_PATH%\_backup_ru"

if not exist "%BACKUP_DIR%\localization\" (
    echo.
    echo  Создание резервной копии...
    mkdir "%BACKUP_DIR%\localization" 2>nul

    for %%F in ("%GAME_PATH%\localization\*.csv") do (
        copy /Y "%%F" "%BACKUP_DIR%\localization\" >nul
    )

    if exist "%GAME_PATH%\fonts\Chusung-220206.ttf" (
        mkdir "%BACKUP_DIR%\fonts" 2>nul
        copy /Y "%GAME_PATH%\fonts\Chusung-220206.ttf" "%BACKUP_DIR%\fonts\" >nul
    )

    echo  Бэкап создан: %BACKUP_DIR%
) else (
    echo.
    echo  Бэкап уже существует, пропускаем.
)

:: ── Установка файлов локализации ──
echo.
echo  Установка файлов локализации...

set "COUNT=0"
for %%F in ("%SCRIPT_DIR%localization\*.csv") do (
    copy /Y "%%F" "%GAME_PATH%\localization\" >nul
    set /a COUNT+=1
)

echo  Скопировано CSV-файлов: !COUNT!

:: ── Установка шрифта ──
if exist "%SCRIPT_DIR%fonts\NotoSans-ExtraBold.ttf" (
    if exist "%GAME_PATH%\fonts\Chusung-220206.ttf" (
        copy /Y "%SCRIPT_DIR%fonts\NotoSans-ExtraBold.ttf" "%GAME_PATH%\fonts\Chusung-220206.ttf" >nul
        echo  Шрифт установлен.
    ) else (
        echo  [!] Целевой шрифт Chusung-220206.ttf не найден в игре.
    )
) else (
    echo  [!] Шрифт NotoSans-ExtraBold.ttf не найден в fonts/
    echo      Кириллический шрифт не установлен.
)

:: ── Итог ──
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
