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

При релизе: обновить `VERSION` в корне и создать тег `vX.Y` на GitHub.

Не запускать удалённый `fix_ui_overflow.py`.

## Установка

`install_patch.bat` вызывает `configure_russian_defaults.py` (цена в магазине, 8px в save при наличии).
