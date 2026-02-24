#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Star of Providence — Russian localization installer.

Automatically finds the game directory, backs up original files,
patches CSV localization (replaces ZHS column with Russian),
and installs a Cyrillic-capable font.

Usage:
    python install.py              # auto-detect game directory
    python install.py "D:\\Games"  # specify custom path
    python install.py --restore    # restore original files from backups
"""
import csv
import logging
import platform
import shutil
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
FONT_SRC = SCRIPT_DIR / "fonts" / "NotoSans-ExtraBold.ttf"
ENCODING = "utf-8-sig"
BACKUP_SUFFIX = ".backup_ru"
GAME_DIR_NAME = "Star of Providence"
STEAM_APP_ID = "603960"

# ── Translation dictionaries ────────────────────────────────────────────

UI_STRINGS_RU: dict[str, str] = {
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
}

WEAPON_NAME_RU: dict[str, str] = {
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
}

OPTION_CAPTION_RU: dict[str, str] = {
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
}

OPTION_TOOLTIP_RU: dict[str, str] = {
    "set graphical options": "настройки графики",
    "set audio options": "настройки звука",
    "rebind controls#or set control mode": "назначение клавиш#и режим управления",
    "changes game language": "смена языка игры",
    "change window mode": "режим окна",
    "set window resolution": "разрешение окна",
    "set cursor type": "тип курсора",
    "intensity of screen shaking": "интенсивность тряски камеры",
    "tones down#most flashing effects": "смягчает#большинство мигающих эффектов",
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
    "hold confirm#to erase everything": "удерживайте для полного сброса",
    "sets crt filter": "фильтр ЭЛТ",
    "toggles the ui flickering": "мерцание интерфейса",
    "show player hitbox": "показывать хитбокс игрока",
    "outlines all walls": "контуры стен",
    "hold confirm to#restart the run": "удерживайте для перезапуска забега",
    "bomb to scrap": "бомба в лом",
    "enables additive blend mode#for enemy lasers": (
        "аддитивный режим#для вражеских лазеров"
    ),
    "controller option#disables stick fire": "отключить стрельбу стиком",
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
    "controller option#changes controller graphics": "иконки кнопок геймпада",
    "adjusts aim assist": "помощь прицеливания",
    "controller option#adjusts aim assist": "помощь прицеливания (геймпад)",
    "alters aim assist range": "радиус помощи прицеливания",
    "controller option#alters aim assist range": "радиус помощи (геймпад)",
    "displays art#in the sidebars": "картинки на боковых панелях",
}

RARITY_NAME_RU: dict[str, str] = {
    "common": "обычный",
    "rare": "редкий",
    "legendary": "легендарный",
    "eternal": "вечный",
}

STAT_NAME_RU: dict[str, str] = {
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
}

MODE_NAME_RU: dict[str, str] = {
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
    "sudden death#200% damage, 1 hp": "внезапная смерть#200% урона, 1 ОЗ",
    "mild": "лёгкий",
    "intense": "интенсив",
    "sudden death": "внезапная смерть",
    "seed": "сид",
    "random": "случайно",
    "random seed": "случайный сид",
    "custom seed#press to set": "свой сид#нажмите для ввода",
    "normal mode#default difficulty": "обычный режим#стандартная сложность",
    "hard mode#expert difficulty": "сложный режим#для экспертов",
    "normal": "обычный",
    "hard": "сложный",
    "difficulty": "сложность",
    "loops": "циклы",
    "enabled": "вкл",
    "disabled": "выкл",
    "null#twelfth visitor": "null#двенадцатый посетитель",
    "d-13#thirteenth visitor": "d-13#тринадцатый посетитель",
}

BOSS_NAME_RU: dict[str, str] = {
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
}

BLESSING_NAME_RU: dict[str, str] = {
    "flame": "пламя",
    "frost": "мороз",
    "earth": "земля",
    "storm": "буря",
    "sight": "зоркость",
    "abyss": "бездна",
    "enigma": "загадка",
}

UPGRADE_NAME_RU: dict[str, str] = {
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
}

AREA_NAME_RU: dict[str, str] = {
    "excavation": "раскопки",
    "archives": "архивы",
    "maintenance system": "система обслуживания",
    "bellows": "кузница",
    "sanctum": "святилище",
    "the temple": "храм",
    "nowhere": "нигде",
}

CONTROL_DISPLAY_RU: dict[str, str] = {
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
}

CREDITS_RU: dict[str, str] = {
    "programming:": "программирование:",
    "art and direction:": "арт и руководство:",
    "music and sfx:": "музыка и звуки:",
    "--special thanks--": "--особая благодарность--",
    "and all the users#of the uff forums": "и все пользователи#форумов uff",
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
}

FILE_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ui_strings.csv": UI_STRINGS_RU,
    "weapon_name.csv": WEAPON_NAME_RU,
    "option_caption.csv": OPTION_CAPTION_RU,
    "option_tooltip.csv": OPTION_TOOLTIP_RU,
    "rarity_name.csv": RARITY_NAME_RU,
    "stat_name.csv": STAT_NAME_RU,
    "mode_name.csv": MODE_NAME_RU,
    "boss_name.csv": BOSS_NAME_RU,
    "blessing_name.csv": BLESSING_NAME_RU,
    "upgrade_name.csv": UPGRADE_NAME_RU,
    "area_name.csv": AREA_NAME_RU,
    "control_display.csv": CONTROL_DISPLAY_RU,
    "credits.csv": CREDITS_RU,
}

SKIP_FILES: set[str] = {
    "keyboard_keys.csv",
    "keyboard_keys_switch.csv",
}


# ── Game directory detection ─────────────────────────────────────────────

STEAM_COMMON_PATHS: list[str] = [
    r"C:\Program Files (x86)\Steam\steamapps\common",
    r"C:\Program Files\Steam\steamapps\common",
    r"D:\Steam\steamapps\common",
    r"D:\SteamLibrary\steamapps\common",
    r"E:\Steam\steamapps\common",
    r"E:\SteamLibrary\steamapps\common",
    r"F:\Steam\steamapps\common",
    r"F:\SteamLibrary\steamapps\common",
    r"G:\SteamLibrary\steamapps\common",
    "~/.steam/steam/steamapps/common",
    "~/.local/share/Steam/steamapps/common",
]


def find_game_directory(custom_path: str | None = None) -> Path | None:
    """Auto-detect or validate the game installation directory.

    Args:
        custom_path: Optional user-provided path to game or Steam library.

    Returns:
        Path to the game root directory, or None if not found.
    """
    if custom_path:
        p = Path(custom_path).expanduser()
        if (p / "localization").is_dir():
            return p
        candidate = p / GAME_DIR_NAME
        if (candidate / "localization").is_dir():
            return candidate
        for child in p.iterdir() if p.is_dir() else []:
            if (child / "localization").is_dir():
                return child
        return None

    for steam_path in STEAM_COMMON_PATHS:
        candidate = Path(steam_path).expanduser() / GAME_DIR_NAME
        if (candidate / "localization").is_dir():
            return candidate

    return None


# ── Backup / restore ─────────────────────────────────────────────────────

def backup_file(path: Path) -> None:
    """Create a backup of a file if it doesn't already exist."""
    backup = path.with_suffix(path.suffix + BACKUP_SUFFIX)
    if not backup.exists():
        shutil.copy2(path, backup)


def restore_file(path: Path) -> bool:
    """Restore a file from its backup. Returns True if restored."""
    backup = path.with_suffix(path.suffix + BACKUP_SUFFIX)
    if backup.exists():
        shutil.copy2(backup, path)
        return True
    return False


# ── CSV patching ─────────────────────────────────────────────────────────

def strip_ru_column(rows: list[list[str]]) -> list[list[str]]:
    """Remove trailing RU column if present (from earlier patching attempts)."""
    if not rows or "RU" not in rows[0]:
        return rows
    ru_idx = rows[0].index("RU")
    return [
        [c for j, c in enumerate(row) if j != ru_idx]
        for row in rows
    ]


def patch_csv(csv_path: Path, en_to_ru: dict[str, str] | None) -> int:
    """Patch a CSV file: replace ZHS column with Russian text.

    Args:
        csv_path: Path to CSV file.
        en_to_ru: Translation dict (EN -> RU). None = use EN as fallback.

    Returns:
        Number of translated rows.
    """
    rows: list[list[str]] = []
    with csv_path.open(encoding=ENCODING, newline="", errors="replace") as f:
        rows = list(csv.reader(f))

    if not rows:
        return 0

    rows = strip_ru_column(rows)
    header = rows[0]

    if "ZHS" not in header or "EN" not in header:
        return 0

    zhs_idx = header.index("ZHS")
    en_idx = header.index("EN")
    translated = 0

    for row in rows[1:]:
        if len(row) <= max(zhs_idx, en_idx):
            continue

        en_val = row[en_idx].strip()
        if not en_val:
            continue

        if en_to_ru and en_val in en_to_ru:
            row[zhs_idx] = en_to_ru[en_val]
            translated += 1
        else:
            row[zhs_idx] = en_val

    with csv_path.open("w", encoding=ENCODING, newline="") as f:
        csv.writer(f).writerows(rows)

    return translated


def patch_language_name(csv_path: Path) -> None:
    """Rename the ZHS language slot from Chinese to Russian."""
    rows: list[list[str]] = []
    with csv_path.open(encoding=ENCODING, newline="", errors="replace") as f:
        rows = list(csv.reader(f))

    rows = strip_ru_column(rows)
    header = rows[0]

    if "ZHS" not in header:
        return

    zhs_idx = header.index("ZHS")
    en_idx = header.index("EN") if "EN" in header else 2

    lang_names_ru: dict[str, str] = {
        "english": "английский",
        "german": "немецкий",
        "french": "французский",
        "spanish": "испанский",
        "portugese": "португальский",
        "chinese": "русский",
        "japanese": "японский",
    }

    new_rows: list[list[str]] = [header]
    for row in rows[1:]:
        if len(row) <= max(zhs_idx, en_idx):
            new_rows.append(row)
            continue

        en_val = row[en_idx].strip()

        if en_val == "chinese":
            row[en_idx] = "russian"
            row[zhs_idx] = "русский"
            for col_idx in range(3, len(row)):
                if col_idx != zhs_idx:
                    row[col_idx] = "russian"
        elif en_val in lang_names_ru:
            row[zhs_idx] = lang_names_ru[en_val]
        elif en_val:
            row[zhs_idx] = en_val

        new_rows.append(row)

    with csv_path.open("w", encoding=ENCODING, newline="") as f:
        csv.writer(f).writerows(new_rows)


# ── Main commands ────────────────────────────────────────────────────────

def install(game_dir: Path) -> None:
    """Run the full installation."""
    loc_dir = game_dir / "localization"
    fonts_dir = game_dir / "fonts"

    logger.info("Game directory: %s", game_dir)

    # ── Backup originals ──
    logger.info("Creating backups...")
    for csv_file in loc_dir.glob("*.csv"):
        backup_file(csv_file)
    chusung = fonts_dir / "Chusung-220206.ttf"
    if chusung.exists():
        backup_file(chusung)

    # ── Patch CSVs ──
    csv_files = sorted(loc_dir.glob("*.csv"))
    total_translated = 0
    total_rows = 0

    logger.info("Patching %d CSV files...", len(csv_files))
    for csv_path in csv_files:
        if csv_path.name in SKIP_FILES:
            logger.info("  [skip] %s", csv_path.name)
            continue

        if csv_path.name == "language_name.csv":
            patch_language_name(csv_path)
            logger.info("  [lang] %s — ZHS slot renamed to russian", csv_path.name)
            continue

        translations = FILE_TRANSLATIONS.get(csv_path.name)
        count = patch_csv(csv_path, translations)
        total_translated += count

        rows: list[list[str]] = []
        with csv_path.open(encoding=ENCODING, newline="", errors="replace") as f:
            rows = list(csv.reader(f))
        data_rows = sum(
            1 for r in rows[1:] if r and r[0].strip().isdigit()
        )
        total_rows += data_rows

        status = "RU" if translations else "EN fallback"
        logger.info(
            "  [%s] %s — %d/%d rows",
            status, csv_path.name, count, data_rows,
        )

    # ── Install font ──
    if FONT_SRC.exists() and chusung.exists():
        shutil.copy2(FONT_SRC, chusung)
        logger.info("Font installed: %s -> %s", FONT_SRC.name, chusung.name)
    elif not FONT_SRC.exists():
        logger.warning("Font file not found: %s", FONT_SRC)
    else:
        logger.warning("Target font not found: %s", chusung)

    # ── Summary ──
    logger.info("")
    logger.info("=" * 50)
    logger.info("Installation complete!")
    logger.info("  Translated: %d / %d rows", total_translated, total_rows)
    logger.info("  Untranslated rows use English as fallback.")
    logger.info("")
    logger.info("Launch the game and select 'русский' in language settings.")
    logger.info("(It replaces the Chinese language slot.)")
    logger.info("")
    logger.info("To restore originals: python install.py --restore")
    logger.info("=" * 50)


def restore(game_dir: Path) -> None:
    """Restore all original files from backups."""
    loc_dir = game_dir / "localization"
    fonts_dir = game_dir / "fonts"
    restored = 0

    for csv_file in loc_dir.glob("*.csv"):
        if restore_file(csv_file):
            restored += 1

    chusung = fonts_dir / "Chusung-220206.ttf"
    if restore_file(chusung):
        restored += 1

    logger.info("Restored %d files to original state.", restored)


def main() -> None:
    """Entry point: parse arguments and run."""
    args = sys.argv[1:]
    do_restore = "--restore" in args
    custom_path = next((a for a in args if not a.startswith("--")), None)

    game_dir = find_game_directory(custom_path)

    if not game_dir:
        logger.error(
            "Game directory not found! Searched common Steam paths."
        )
        logger.error(
            "Specify the path manually: python install.py \"D:\\Games\\%s\"",
            GAME_DIR_NAME,
        )
        if platform.system() == "Windows":
            logger.error(
                "Tip: right-click the game in Steam → Manage → Browse Local Files"
            )
        sys.exit(1)

    if do_restore:
        restore(game_dir)
    else:
        install(game_dir)


if __name__ == "__main__":
    main()
