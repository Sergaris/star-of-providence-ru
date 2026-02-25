@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ====================================================
echo   Star of Providence - Восстановление оригинала
echo  ====================================================
echo.

:: ── Ввод пути к игре ──
echo  Укажите путь к папке игры Star of Providence.
echo.
set /p "GAME_PATH=  Путь: "

if "%GAME_PATH%"=="" (
    echo.
    echo  [ОШИБКА] Путь не указан.
    echo.
    pause
    exit /b 1
)

set "GAME_PATH=%GAME_PATH:"=%"
if "%GAME_PATH:~-1%"=="\" set "GAME_PATH=%GAME_PATH:~0,-1%"

:: ── Проверка бэкапа ──
set "BACKUP_DIR=%GAME_PATH%\_backup_ru"

if not exist "%BACKUP_DIR%\localization\" (
    echo.
    echo  [ОШИБКА] Резервная копия не найдена в:
    echo  %BACKUP_DIR%
    echo.
    echo  Бэкап создается автоматически при установке через install_patch.bat
    echo.
    pause
    exit /b 1
)

:: ── Восстановление ──
echo  Восстановление файлов...

set "COUNT=0"
for %%F in ("%BACKUP_DIR%\localization\*.csv") do (
    copy /Y "%%F" "%GAME_PATH%\localization\" >nul
    set /a COUNT+=1
)
echo  Восстановлено CSV-файлов: !COUNT!

if exist "%BACKUP_DIR%\fonts\Chusung-220206.ttf" (
    copy /Y "%BACKUP_DIR%\fonts\Chusung-220206.ttf" "%GAME_PATH%\fonts\" >nul
    echo  Шрифт восстановлен.
)

:: ── Удаление бэкапа (опционально) ──
echo.
set /p "DEL_BACKUP=  Удалить папку бэкапа? (y/n): "
if /i "!DEL_BACKUP!"=="y" (
    rmdir /s /q "%BACKUP_DIR%" 2>nul
    echo  Бэкап удалён.
)

echo.
echo  ====================================================
echo   Оригинальные файлы восстановлены!
echo  ====================================================
echo.

pause
