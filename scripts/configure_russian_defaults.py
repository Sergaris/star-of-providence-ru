#!/usr/bin/env python3
"""Apply Russian-specific defaults after localization install.

Sets font resolution to 8px in game settings when a save/settings file exists.
Always ensures kleines shop price prefix is correct in the game folder.
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ENCODING = "utf-8-sig"
LANG_RUSSIAN_INDEX = 5
FONT_8PX_INDEX = 0
KLEINES_PRICE_ZHS = "#/p2/c1цена"
SAVEDATA_NAMES = (
    "savedata.d13",
    "savedata_sop.d13",
    "savedata_dlc1.d13",
    "temp_savedata.d13",
    "temp_savedata_sop.d13",
    "temp_savedata_dlc1.d13",
)


def _read_csv_rows(path: Path) -> list[list[str]]:
    with path.open(encoding=ENCODING, newline="") as handle:
        return list(csv.reader(handle))


def _write_csv_rows(path: Path, rows: list[list[str]]) -> None:
    line_ending = "\r\n" if path.read_text(encoding=ENCODING).find("\r\n") >= 0 else "\n"
    with path.open("w", encoding=ENCODING, newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows)
    if line_ending == "\r\n":
        text = path.read_text(encoding=ENCODING)
        path.write_text(text.replace("\n", "\r\n"), encoding=ENCODING, newline="")


def ensure_kleines_price(game_path: Path) -> bool:
    """Force Russian price prefix in installed kleines_caption.csv."""
    path = game_path / "localization" / "kleines_caption.csv"
    if not path.exists():
        logger.warning("kleines_caption.csv не найден: %s", path)
        return False

    rows = _read_csv_rows(path)
    if not rows or "ZHS" not in rows[0]:
        return False

    zhs_idx = rows[0].index("ZHS")
    changed = False
    for row in rows[1:]:
        if row and row[0].strip() == "9" and len(row) > zhs_idx:
            if row[zhs_idx] != KLEINES_PRICE_ZHS:
                row[zhs_idx] = KLEINES_PRICE_ZHS
                changed = True

    if changed:
        _write_csv_rows(path, rows)
    return changed


def _savedata_search_dirs(game_path: Path) -> list[Path]:
    dirs = [game_path]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        base = Path(local)
        for child in base.iterdir() if base.is_dir() else []:
            low = child.name.lower()
            if "providence" in low or "star" in low and "prov" in low:
                dirs.append(child)
    return dirs


def _find_savedata_files(game_path: Path) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for folder in _savedata_search_dirs(game_path):
        for name in SAVEDATA_NAMES:
            candidate = folder / name
            if candidate.is_file() and candidate not in seen:
                found.append(candidate)
                seen.add(candidate)
    return found


def _try_patch_savedata_font(data: bytearray) -> bool:
    """Heuristic: flip font_resolution to 8px when language is Russian.

    GameMaker buffers often store small integers sequentially. We look for
    (language=5, font=1) and change font to 0. This is best-effort.
    """
    needle = bytes([LANG_RUSSIAN_INDEX, 1])
    replacement = bytes([LANG_RUSSIAN_INDEX, FONT_8PX_INDEX])
    patched = False
    start = 0
    while True:
        pos = data.find(needle, start)
        if pos < 0:
            break
        data[pos + 1] = FONT_8PX_INDEX
        patched = True
        start = pos + 2
    return patched


def ensure_8px_in_savedata(game_path: Path) -> int:
    """Patch savedata files to use 8px when language index is Russian."""
    count = 0
    for path in _find_savedata_files(game_path):
        raw = bytearray(path.read_bytes())
        if _try_patch_savedata_font(raw):
            path.write_bytes(raw)
            count += 1
    return count


def ensure_8px_in_datawin(game_path: Path) -> bool:
    """Best-effort: set default font_resolution to 8px in data.win globals."""
    data_win = game_path / "data.win"
    if not data_win.is_file():
        return False

    data = bytearray(data_win.read_bytes())
    # Common pattern: push 1 (16px) as 32-bit little-endian after set_font_resolution refs
    # Only patch isolated Push 1 before Ret in set_font_resolution script region — skipped
    # without full decompiler. Return False to avoid risky edits.
    return False


def configure(game_path: Path) -> None:
    """Apply all Russian default tweaks under game_path."""
    game_path = game_path.resolve()
    if not (game_path / "localization").is_dir():
        logger.error("Не найдена папка localization в %s", game_path)
        sys.exit(1)

    ensure_kleines_price(game_path)
    ensure_8px_in_savedata(game_path)
    ensure_8px_in_datawin(game_path)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Настройки по умолчанию для русской локализации",
    )
    parser.add_argument(
        "game_path",
        type=Path,
        help="Корневая папка Star of Providence",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Без сообщений (для install_patch.bat)",
    )
    args = parser.parse_args()
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    configure(args.game_path)


if __name__ == "__main__":
    main()
