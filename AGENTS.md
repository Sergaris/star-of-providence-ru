# Инструкции для агентов (Star of Providence RU)

Перед правкой: **[docs/LOCALIZATION.md](docs/LOCALIZATION.md)**.

## Кратко

- Перевод только в колонку **ZHS**; теги и `%var%` как в EN.
- Режим **8px** в меню языка — **обязательное требование** при русском (не 16px).
- **Не сокращать** `*_name.csv` и осмысленные слова в меню («продолжить», не «продолж.»).
- **`kleines_caption.csv` id 9:** `#/p2/c1цена` (≤10 байт UTF-8 видимого текста).
- Откат: проверка целостности файлов в Steam (см. README).

## Проверки

```bash
python scripts/patch.py validate
python scripts/patch.py check-release
python scripts/fix_linebreaks.py
```

При релизе: обновить `RUSSIFIER_VERSION` в `install_patch.bat`, синхронизировать `VERSION`, тег `vX.Y`, собрать zip (`scripts/build_release.ps1`), опубликовать на GitHub Releases.

Не запускать удалённый `fix_ui_overflow.py`.

## Релизный архив

Только три элемента в корне: `install_patch.bat`, `localization/`, `fonts/`. Проверка версии — в bat (PowerShell + GitHub API), без Python и без `scripts/`.

## Установка

`install_patch.bat` копирует CSV и шрифт; 8px пользователь выбирает в игре вручную.
