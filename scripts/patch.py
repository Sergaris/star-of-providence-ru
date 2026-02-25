#!/usr/bin/env python3
"""Star of Providence — утилита управления русской локализацией.

Инициализирует каталог ``localization/`` из файлов игры, показывает прогресс
перевода и проверяет переводы на типичные ошибки.

Usage::

    python scripts/patch.py init --game-path "E:\\SteamLibrary\\...\\Star of Providence"
    python scripts/patch.py stats
    python scripts/patch.py validate
"""

import argparse
import csv
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCALIZATION_DIR = ROOT_DIR / "localization"
ENCODING = "utf-8-sig"
BACKUP_SUFFIX = ".backup_ru"

SKIP_FILES: frozenset[str] = frozenset({
    "keyboard_keys.csv",
    "keyboard_keys_switch.csv",
})

TAG_RE = re.compile(r"/[cfp]\d")
VAR_RE = re.compile(r"%\w+%")

MIN_LENGTH_FOR_CHECK: int = 10
MAX_LENGTH_RATIO: float = 1.5


# ── Existing translations for migration during init ─────────────────────
# After `init` completes, all translations live in localization/*.csv
# and these dicts are no longer used at runtime.

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ui_strings.csv": {
        "best:": "рекорд:",
        "inactive machine": "неактивная машина",
        "reward": "награда",
        "reward lv.": "уровень награды",
        "game in progress#continue?": "игра в процессе#продолжить?",
        "yeah": "да",
        "nah": "нет",
        "save discrepancy detected##which save would#you like to use?": (
            "обнаружено расхождение сохранений##какое сохранение#использовать?"
        ),
        "greetings, visitor %nr%": "привет, посетитель %nr%",
        "external influence on database coherency has been detected_": (
            "обнаружено внешнее воздействие на целостность базы данных_"
        ),
        "corruption levels: 94%,#null driver event imminent_": (
            "уровень повреждения: 94%,#событие нулевого драйвера неизбежно_"
        ),
        "the user has been deemed a void-class threat_": (
            "пользователь признан угрозой класса «пустота»_"
        ),
        "purification in progress..._": "очистка в процессе…_",
        "thank you for using#the facility database_": (
            "спасибо за использование#базы данных объекта_"
        ),
        "see you next time_": "до следующей встречи_",
        "greetings, visitor_": "привет, посетитель_",
        "-loop %loop%-": "-цикл %loop%-",
        "local save": "локальное сохранение",
        "cloud save": "облачное сохранение",
        "hold confirm": "удерживайте",
        "- save report": "- сохранить отчёт",
        "good luck": "удачи",
        "your time is nigh": "твой час близок",
        "it begins": "начало",
        "out of depth": "за гранью",
        "everything hurts": "всё болит",
        "eternal nightmare": "вечный кошмар",
        "confirm choice": "подтвердить выбор",
    },
    "weapon_name.csv": {
        "basic": "базовое",
        "vulcan": "вулкан",
        "fireball": "огненный шар",
        "laser": "лазер",
        "sword": "меч",
        "charge": "заряд",
        "revolver": "револьвер",
        "razor": "бритва",
        "pulsar": "пульсар",
        "thunderhead": "громовая туча",
        "railgun": "рельсотрон",
        "drill": "бур",
        "spear": "копьё",
        "runic": "руническое",
        "bow": "лук",
        "grenade": "граната",
        "skully": "скалли",
    },
    "option_caption.csv": {
        "start": "старт",
        "options": "опции",
        "exit": "выход",
        "back": "назад",
        "video": "видео",
        "audio": "звук",
        "controls": "управление",
        "mode": "режим",
        "resolution": "разрешение",
        "cursor": "курсор",
        "shake cam": "тряска камеры",
        "fullscreen": "полный экран",
        "window": "окно",
        "default": "по умолчанию",
        "crosshair": "прицел",
        "mild": "лёгкая",
        "normal": "обычная",
        "strong": "сильная",
        "nuclear": "ядерная",
        "music volume": "громкость музыки",
        "sfx volume": "громкость эффектов",
        "control mode": "режим управления",
        "keyboard": "клавиатура",
        "controller": "геймпад",
        "resume": "продолжить",
        "exit to menu": "в меню",
        "exit game": "выход из игры",
        "enter the new key": "нажмите новую клавишу",
        "escape to cancel": "ESC — отмена",
        "key already in use": "клавиша уже занята",
        "language": "язык",
        "choose one": "выберите один",
        "so be it": "да будет так",
        "thats all folks": "вот и всё",
        "photosensitivity": "светочувствительность",
        "on": "вкл",
        "off": "выкл",
        "3d sound": "3D-звук",
        "global": "глобальный",
        "local": "локальный",
        "scanlines": "развёртка",
        "interpolation": "интерполяция",
        "reset controls": "сбросить управление",
        "aim opacity": "прозрачность прицела",
        "v-sync": "верт. синхр.",
        "the nimbus#has been broken": "нимб#разрушен",
        "crosshair 2": "прицел 2",
        "reset progress": "сбросить прогресс",
        "crt": "ЭЛТ",
        "ui flicker": "мерцание интерфейса",
        "enter the new button": "нажмите новую кнопку",
        "start to cancel": "START — отмена",
        "button already in use": "кнопка уже занята",
        "hitbox": "хитбокс",
        "outlines": "контуры",
        "restart": "перезапуск",
        "shiny lasers": "яркие лазеры",
        "guns on hold": "стрельба по удержанию",
        "the breach#has been opened": "брешь#открыта",
        "laser aim": "лазерный прицел",
        "empty": "пусто",
        "cannot#dig here": "здесь#копать нельзя",
        "back to hub": "в хаб",
        "-tier %tier%-": "-уровень %tier%-",
        "bravo!": "браво!",
        "excellent!": "отлично!",
        "perfect!": "идеально!",
        "touchscreen": "сенсорный экран",
        "strafing": "стрейф",
        "vibration": "вибрация",
        "button style": "стиль кнопок",
        "auto": "авто",
        "playstation": "PLAYSTATION",
        "xbox": "XBOX",
        "switch pro": "SWITCH PRO",
        "generic": "общий",
        "+ to cancel": "+ — отмена",
        "aim assist": "помощь прицеливания",
        "assist range": "радиус помощи",
        "wallpaper": "обои",
        "low": "низкая",
        "medium": "средняя",
        "high": "высокая",
        "extreme": "экстрим",
    },
    "option_tooltip.csv": {
        "set graphical options": "настройки графики",
        "set audio options": "настройки звука",
        "rebind controls#or set control mode": (
            "назначение клавиш#и режим управления"
        ),
        "changes game language": "смена языка игры",
        "change window mode": "режим окна",
        "set window resolution": "разрешение окна",
        "set cursor type": "тип курсора",
        "intensity of screen shaking": "интенсивность тряски камеры",
        "tones down#most flashing effects": (
            "смягчает#большинство мигающих эффектов"
        ),
        "volume of sound effects": "громкость эффектов",
        "volume of music": "громкость музыки",
        "rebind the controls": "назначить клавиши управления",
        "removes the cursor#and allows dual-stick aiming": (
            "убирает курсор#и включает прицеливание двумя стиками"
        ),
        "toggles type of#directional sound": (
            "переключает тип#пространственного звука"
        ),
        "sets scanline strength": "сила линий развёртки",
        "smoothes the pixel graphics": "сглаживание пиксельной графики",
        "resets controls#to default": "сброс управления#по умолчанию",
        "sets the visibility#of the aim reticle": "видимость прицела",
        "prevents tearing#may cause slowdown": (
            "устраняет разрывы#может снизить FPS"
        ),
        "hold confirm#to erase everything": (
            "удерживайте для полного сброса"
        ),
        "sets crt filter": "фильтр ЭЛТ",
        "toggles the ui flickering": "мерцание интерфейса",
        "show player hitbox": "показывать хитбокс игрока",
        "outlines all walls": "контуры стен",
        "hold confirm to#restart the run": (
            "удерживайте для перезапуска забега"
        ),
        "bomb to scrap": "бомба в лом",
        "enables additive blend mode#for enemy lasers": (
            "аддитивный режим#для вражеских лазеров"
        ),
        "controller option#disables stick fire": (
            "отключить стрельбу стиком"
        ),
        "assist aim with a#laser pointer": "подсветка прицела лазером",
        "enables touchscreen for#menus and aiming": (
            "сенсорный экран для меню и прицела"
        ),
        "controller option#disables move stick aim": (
            "отключить прицел стиком движения"
        ),
        "disables move stick aim": "прицел стиком движения выкл",
        "disables stick fire": "стрельба стиком выкл",
        "controller option#toggles vibration": "вибрация геймпада",
        "toggles vibration": "вибрация вкл/выкл",
        "controller option#changes controller graphics": (
            "иконки кнопок геймпада"
        ),
        "adjusts aim assist": "помощь прицеливания",
        "controller option#adjusts aim assist": (
            "помощь прицеливания (геймпад)"
        ),
        "alters aim assist range": "радиус помощи прицеливания",
        "controller option#alters aim assist range": (
            "радиус помощи (геймпад)"
        ),
        "displays art#in the sidebars": "картинки на боковых панелях",
    },
    "rarity_name.csv": {
        "common": "обычный",
        "rare": "редкий",
        "legendary": "легендарный",
        "eternal": "вечный",
    },
    "stat_name.csv": {
        "rarity": "редкость",
        "damage": "урон",
        "firerate": "скорострельность",
        "max ammo": "макс. боезапас",
        "crit chance": "шанс крита",
        "crit damage": "урон крита",
        "refill ammo": "пополнение боезапаса",
        "max hp": "макс. ОЗ",
        "gain bombs": "получить бомбы",
        "gain a shield": "получить щит",
    },
    "mode_name.csv": {
        "player": "игрок",
        "lethality": "летальность",
        "exit": "выход",
        "null#normal mode": "null#обычный режим",
        "d-13#hard mode": "d-13#сложный режим",
        "overlord#sword mode": "overlord#режим меча",
        "???#chaos mode": "???#режим хаоса",
        "null": "null",
        "d-13": "d-13",
        "overlord": "overlord",
        "???": "???",
        "a. blaster": "a. бластер",
        "arena blaster#no bombs, active items": (
            "арена бластер#без бомб, с активными предметами"
        ),
        "skully#modular weapons": "скалли#модульное оружие",
        "skully": "скалли",
        "armsmaster#two weapon slots, no bombs": (
            "мастер оружия#два слота оружия, без бомб"
        ),
        "armsmaster": "мастер оружия",
        "mild#100% damage, 10 health": "лёгкий#100% урона, 10 ОЗ",
        "intense#125% damage, 50% health": "интенсив#125% урона, 50% ОЗ",
        "sudden death#200% damage, 1 hp": (
            "внезапная смерть#200% урона, 1 ОЗ"
        ),
        "mild": "лёгкий",
        "intense": "интенсив",
        "sudden death": "внезапная смерть",
        "seed": "сид",
        "random": "случайно",
        "random seed": "случайный сид",
        "custom seed#press to set": "свой сид#нажмите для ввода",
        "normal mode#default difficulty": (
            "обычный режим#стандартная сложность"
        ),
        "hard mode#expert difficulty": "сложный режим#для экспертов",
        "normal": "обычный",
        "hard": "сложный",
        "difficulty": "сложность",
        "loops": "циклы",
        "enabled": "вкл",
        "disabled": "выкл",
        "null#twelfth visitor": "null#двенадцатый посетитель",
        "d-13#thirteenth visitor": "d-13#тринадцатый посетитель",
    },
    "boss_name.csv": {
        "forgotten": "забытый",
        "ringleader": "главарь",
        "thirteenth": "тринадцатый",
        "special": "особый",
        "offer": "предложение",
        "core": "ядро",
        "nightmare": "кошмар",
        "dont steal": "не воруй",
        "the warden": "надзиратель",
        "the arbitor": "арбитр",
        "chaosgod": "бог хаоса",
        "ace of storms": "туз бурь",
        "special offer": "спецпредложение",
        "the machine": "машина",
        "lucid dream": "осознанный сон",
    },
    "blessing_name.csv": {
        "flame": "пламя",
        "frost": "мороз",
        "earth": "земля",
        "storm": "буря",
        "sight": "зоркость",
        "abyss": "бездна",
        "enigma": "загадка",
    },
    "upgrade_name.csv": {
        "salvage": "утилизация",
        "weatherproof": "всепогодность",
        "focus": "фокус",
        "scanner": "сканер",
        "stealth": "скрытность",
        "discount": "скидка",
        "autobomb": "автобомба",
        "plating": "броня",
        "artifact": "артефакт",
        "blink": "рывок",
        "second wind": "второе дыхание",
        "extra pow": "доп. мощь",
        "fortune": "удача",
        "reserves": "резерв",
        "power eternal": "вечная сила",
        "quickening": "ускорение",
        "scrap runner": "гонка лома",
        "capacity": "вместимость",
        "expansion port": "порт расширения",
        "packrat": "коллекционер",
    },
    "area_name.csv": {
        "excavation": "раскопки",
        "archives": "архивы",
        "maintenance system": "система обслуживания",
        "bellows": "кузница",
        "sanctum": "святилище",
        "the temple": "храм",
        "nowhere": "нигде",
    },
    "control_display.csv": {
        "up": "вверх",
        "left": "влево",
        "down": "вниз",
        "right": "вправо",
        "select": "выбор",
        "cancel": "отмена",
        "fire": "огонь",
        "dash": "рывок",
        "bomb": "бомба",
        "map": "карта",
    },
    "credits.csv": {
        "programming:": "программирование:",
        "art and direction:": "арт и руководство:",
        "music and sfx:": "музыка и звуки:",
        "--special thanks--": "--особая благодарность--",
        "and all the users#of the uff forums": (
            "и все пользователи#форумов uff"
        ),
        "and all the#aspiring yesdevs#of /agdg/": (
            "и все начинающие#разработчики#из /agdg/"
        ),
        "all the people#who played the demo#and spread the word": (
            "все, кто играл в демо#и рассказывал друзьям"
        ),
        "many more": "и многие другие",
        "and you": "и тебе",
        "-thank you for playing-": "-спасибо за игру-",
        "the end?": "конец?",
        "-you've done your best-": "-ты сделал всё, что мог-",
        "splash art:": "сплэш-арт:",
    },
}

_LANGUAGE_NAMES_RU: dict[str, str] = {
    "english": "английский",
    "german": "немецкий",
    "french": "французский",
    "spanish": "испанский",
    "portugese": "португальский",
    "chinese": "русский",
    "japanese": "японский",
}


# ── CSV I/O ─────────────────────────────────────────────────────────────


def read_csv(path: Path) -> list[list[str]]:
    """Read a CSV file with UTF-8 BOM encoding.

    Args:
        path: Path to the CSV file.

    Returns:
        List of rows, each row is a list of column values.
    """
    with path.open(encoding=ENCODING, newline="") as f:
        return list(csv.reader(f))


def write_csv(path: Path, rows: list[list[str]]) -> None:
    """Write rows to a CSV file with UTF-8 BOM encoding.

    Args:
        path: Destination path.
        rows: List of rows to write.
    """
    with path.open("w", encoding=ENCODING, newline="") as f:
        csv.writer(f).writerows(rows)


def _is_data_row(row: list[str]) -> bool:
    """Row has a numeric ID → contains translatable content."""
    return bool(row and row[0].strip().isdigit())


def _col_indices(header: list[str]) -> tuple[int, int] | None:
    """Return ``(en_idx, zhs_idx)`` or ``None`` if columns are missing."""
    if "EN" not in header or "ZHS" not in header:
        return None
    return header.index("EN"), header.index("ZHS")


# ── init ────────────────────────────────────────────────────────────────


def cmd_init(game_path: Path, *, force: bool = False) -> None:
    """Copy game CSVs to ``localization/``, applying existing translations.

    Prefers backup files (``*.csv.backup_ru``) over potentially
    already-patched game files as the source of original data.

    Args:
        game_path: Root directory of the game (contains ``localization/``).
        force: Overwrite existing files in ``localization/``.
    """
    loc_src = game_path / "localization"
    if not loc_src.is_dir():
        logger.error("Папка localization не найдена: %s", loc_src)
        sys.exit(1)

    LOCALIZATION_DIR.mkdir(exist_ok=True)

    csv_files = sorted(loc_src.glob("*.csv"))
    created = 0
    skipped = 0

    logger.info("Источник: %s", loc_src)
    logger.info("Назначение: %s", LOCALIZATION_DIR)
    logger.info("")

    for src in csv_files:
        if src.name in SKIP_FILES:
            logger.info("  [skip] %s (клавиши — без перевода)", src.name)
            continue

        dest = LOCALIZATION_DIR / src.name
        if dest.exists() and not force:
            logger.info("  [exists] %s", src.name)
            skipped += 1
            continue

        original = src.with_suffix(src.suffix + BACKUP_SUFFIX)
        source = original if original.exists() else src

        rows = read_csv(source)
        if not rows:
            continue

        indices = _col_indices(rows[0])
        if indices is None:
            continue

        en_idx, zhs_idx = indices

        if src.name == "language_name.csv":
            _init_language_name(rows, en_idx, zhs_idx)
        else:
            trans = _TRANSLATIONS.get(src.name, {})
            _init_data_rows(rows, en_idx, zhs_idx, trans)

        write_csv(dest, rows)
        created += 1

        label = "RU" if src.name in _TRANSLATIONS else "EN fallback"
        logger.info("  [%s] %s", label, src.name)

    logger.info("")
    logger.info(
        "Готово: создано %d, пропущено %d. Каталог: %s",
        created,
        skipped,
        LOCALIZATION_DIR,
    )
    if skipped:
        logger.info("Используйте --force для перезаписи существующих файлов.")


def _init_data_rows(
    rows: list[list[str]],
    en_idx: int,
    zhs_idx: int,
    translations: dict[str, str],
) -> None:
    """Set ZHS = Russian translation or EN fallback for each data row."""
    for row in rows[1:]:
        if not _is_data_row(row) or len(row) <= max(en_idx, zhs_idx):
            continue
        en_val = row[en_idx].strip()
        if not en_val:
            continue
        row[zhs_idx] = translations.get(en_val, en_val)


def _init_language_name(
    rows: list[list[str]],
    en_idx: int,
    zhs_idx: int,
) -> None:
    """Replace the Chinese language slot with Russian."""
    for row in rows[1:]:
        if len(row) <= max(en_idx, zhs_idx):
            continue
        en_val = row[en_idx].strip()
        if en_val == "chinese":
            row[en_idx] = "russian"
            row[zhs_idx] = "русский"
            for i in range(3, len(row)):
                if i != zhs_idx:
                    row[i] = "russian"
        elif en_val in _LANGUAGE_NAMES_RU:
            row[zhs_idx] = _LANGUAGE_NAMES_RU[en_val]
        elif en_val:
            row[zhs_idx] = en_val


# ── stats ───────────────────────────────────────────────────────────────


def cmd_stats() -> None:
    """Print a translation coverage table for all files in ``localization/``."""
    if not LOCALIZATION_DIR.is_dir():
        logger.error(
            "Каталог localization/ не найден. Сначала: patch.py init"
        )
        sys.exit(1)

    csv_files = sorted(LOCALIZATION_DIR.glob("*.csv"))
    total_all = 0
    total_done = 0

    print(f"\n{'Файл':<35} {'Строк':>6} {'Перевод':>8} {'Прогресс':>9}")
    print("─" * 62)

    for path in csv_files:
        rows = read_csv(path)
        if not rows:
            continue

        indices = _col_indices(rows[0])
        if indices is None:
            continue

        en_idx, zhs_idx = indices
        file_total = 0
        file_done = 0

        for row in rows[1:]:
            if not _is_data_row(row) or len(row) <= max(en_idx, zhs_idx):
                continue
            en_val = row[en_idx].strip()
            zhs_val = row[zhs_idx].strip()
            if not en_val:
                continue
            file_total += 1
            if zhs_val and zhs_val != en_val:
                file_done += 1

        total_all += file_total
        total_done += file_done
        pct = (file_done / file_total * 100) if file_total else 0.0
        mark = "✓" if file_total and pct == 100.0 else " "
        print(
            f"{mark} {path.name:<33} {file_total:>6} {file_done:>8}"
            f" {pct:>8.1f}%"
        )

    print("─" * 62)
    total_pct = (total_done / total_all * 100) if total_all else 0.0
    print(
        f"  {'ИТОГО':<33} {total_all:>6} {total_done:>8}"
        f" {total_pct:>8.1f}%"
    )
    print()


# ── validate ────────────────────────────────────────────────────────────


def cmd_validate() -> None:
    """Check translated rows for missing tags, variables, and length issues."""
    if not LOCALIZATION_DIR.is_dir():
        logger.error(
            "Каталог localization/ не найден. Сначала: patch.py init"
        )
        sys.exit(1)

    csv_files = sorted(LOCALIZATION_DIR.glob("*.csv"))
    issues: list[str] = []

    for path in csv_files:
        rows = read_csv(path)
        if not rows:
            continue

        indices = _col_indices(rows[0])
        if indices is None:
            continue

        en_idx, zhs_idx = indices

        for line_num, row in enumerate(rows[1:], start=2):
            if not _is_data_row(row) or len(row) <= max(en_idx, zhs_idx):
                continue

            en_val = row[en_idx]
            zhs_val = row[zhs_idx]

            if not en_val.strip() or zhs_val.strip() == en_val.strip():
                continue

            en_tags = sorted(TAG_RE.findall(en_val))
            zhs_tags = sorted(TAG_RE.findall(zhs_val))
            if en_tags != zhs_tags:
                issues.append(
                    f"{path.name}:{line_num} теги: "
                    f"EN={en_tags} ≠ ZHS={zhs_tags}"
                )

            en_vars = sorted(VAR_RE.findall(en_val))
            zhs_vars = sorted(VAR_RE.findall(zhs_val))
            if en_vars != zhs_vars:
                issues.append(
                    f"{path.name}:{line_num} переменные: "
                    f"EN={en_vars} ≠ ZHS={zhs_vars}"
                )

            en_breaks = en_val.count("#")
            zhs_breaks = zhs_val.count("#")
            if en_breaks != zhs_breaks:
                issues.append(
                    f"{path.name}:{line_num} переносы #: "
                    f"EN={en_breaks} ≠ ZHS={zhs_breaks}"
                )

            if en_val.rstrip().endswith("_") and not zhs_val.rstrip().endswith(
                "_"
            ):
                issues.append(
                    f"{path.name}:{line_num} отсутствует завершающий '_'"
                )

            en_len = len(en_val.strip())
            zhs_len = len(zhs_val.strip())
            if (
                en_len > MIN_LENGTH_FOR_CHECK
                and zhs_len > en_len * MAX_LENGTH_RATIO
            ):
                issues.append(
                    f"{path.name}:{line_num} длина: "
                    f"{zhs_len} символов (EN: {en_len})"
                )

    if issues:
        print(f"\nНайдено проблем: {len(issues)}\n")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print("\n✓ Проблем не найдено.")
    print()


# ── main ────────────────────────────────────────────────────────────────


def main() -> None:
    """Parse CLI arguments and dispatch the requested command."""
    parser = argparse.ArgumentParser(
        description="Star of Providence — утилита русской локализации",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser(
        "init",
        help="Создать localization/ из файлов игры",
    )
    p_init.add_argument(
        "--game-path",
        required=True,
        type=Path,
        help="Путь к корневой папке игры Star of Providence",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Перезаписать существующие файлы в localization/",
    )

    sub.add_parser("stats", help="Показать прогресс перевода")
    sub.add_parser("validate", help="Проверить переводы на ошибки")

    args = parser.parse_args()

    match args.command:
        case "init":
            cmd_init(args.game_path, force=args.force)
        case "stats":
            cmd_stats()
        case "validate":
            cmd_validate()


if __name__ == "__main__":
    main()
