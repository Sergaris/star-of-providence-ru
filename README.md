# Star of Providence - русская локализация

> Это AI-перевод с помощью модели Sonnet 4.6 (Anthropic) + ручная вычитка и адаптация игровых терминов.

Неофициальный русский перевод для [Star of Providence](https://store.steampowered.com/app/603960/Star_of_Providence/) · 98.5% переведено.


---

## Установка

1. Скачай [последний релиз](../../releases/latest) и распакуй
2. Запусти `install_patch.bat`
3. Укажи путь к папке игры (скрипт попробует найти автоматически)
4. В игре выбери язык **«русский»**

Чтобы восстановить файлы, в случае проблем - запусти `restore_backup.bat`.

---

<div align="center">

### Поддержать автора

Если перевод пригодился - можно закинуть на кофе :3

[![Задонатить](https://img.shields.io/badge/DonationAlerts-FF6A00?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://www.donationalerts.com/r/sergaris)

<sub>Кнопка не работает? → [прямая ссылка](https://www.donationalerts.com/c/sergaris)</sub>

</div>

---

## Об ошибках в переводе

Если что-то переведено неточно или звучит странно - открой [Issue](../../issues) и опиши:
- где в игре встретилась строка
- что не так
- свой вариант (если есть)

Или сразу Pull Request: найди нужный CSV в `localization/`, исправь 8-ю колонку (ZHS) и отправь.

---

<details>
<summary>Для продвинутых пользователей</summary>

### Ручная установка

1. Скопируй все файлы из `localization/` в `<папка игры>/localization/` с заменой
2. Скопируй `fonts/NotoSans-ExtraBold.ttf` в `<папка игры>/fonts/Chusung-220206.ttf` (переименуй!)
3. В игре выбери язык **«русский»**

### Шрифт

Для отображения кириллицы нужен `NotoSans-ExtraBold.ttf` в папке `fonts/`:

1. Скачай [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans) (вариант ExtraBold)
2. Переименуй в `NotoSans-ExtraBold.ttf`
3. Положи в `fonts/` в корне репозитория

### Утилита patch.py

```bash
# Инициализация localization/ из файлов игры (первый запуск)
python scripts/patch.py init --game-path "E:\\SteamLibrary\\steamapps\\common\\Star of Providence"

# Повторная инициализация (перезапись)
python scripts/patch.py init --game-path "..." --force

# Статистика перевода
python scripts/patch.py stats

# Проверка переводов на ошибки
python scripts/patch.py validate
```

### Прогресс по категориям

| Категория | Статус |
|-----------|--------|
| Меню и настройки | ✓ Готово |
| Оружие, боссы, зоны | ✓ Готово |
| Ключевые слова оружия | ✓ Готово |
| Описания предметов | ✓ Готово |
| UI и информация | ✓ Готово |
| Бестиарий и смерти | ✓ Готово |
| Диалоги NPC | ✓ Готово |

> Оставшиеся ~1.5% - плейсхолдеры разработчиков (`???`, `lorem ipsum`), латинские фразы и имена в титрах.

### Технические детали

- Переводы хранятся в колонке `ZHS` (заменяет китайский язык)
- Формат: CSV, UTF-8 BOM (`utf-8-sig`)
- Шрифт `Chusung-220206.ttf` (корейский) заменяется на `NotoSans-ExtraBold.ttf` (кириллица)
- Спецсимволы: `#` (перенос), `/c0-5` (цвета), `/f0-1` (формат), `/p1-2` (пауза), `%var%` (переменные)

### При обновлении игры

1. `python scripts/patch.py init --game-path "..." --force` - обновит localization/
2. `git diff` - новые строки будут иметь ZHS == EN
3. Переведи новые строки

</details>