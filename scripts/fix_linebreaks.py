"""Fix line breaks in Russian (ZHS) translations for Star of Providence.

The game renders text character-by-character and wraps at pixel boundaries,
not word boundaries. Russian text uses NotoSans-ExtraBold (wider than the
original pixel font), so lines overflow sooner. This script adds '#' at
word boundaries to prevent mid-word wrapping.
"""

import csv
import re
from io import StringIO
from pathlib import Path

LOCALIZATION_DIR = Path(__file__).parent.parent / "localization"

TAG_PATTERN = re.compile(r"/[cfpsnrmq]\d")
CYRILLIC_PATTERN = re.compile(r"[а-яА-ЯёЁ]")

DIALOGUE_FILES = {
    "gossip_tank.csv",
    "gossip_death.csv",
    "gossip_alt.csv",
    "greeting_strings.csv",
}

NARRATIVE_FILES = {
    "hack_text.csv",
    "kleines_caption.csv",
    "mirror_strings.csv",
    "crate_strings.csv",
    "postgame_strings.csv",
    "credits_strings.csv",
    "branch_strings.csv",
    "focus_message.csv",
}

DESCRIPTION_FILES = {
    "bestiary_entry.csv",
}

TOOLTIP_FILES = {
    "item_tooltip.csv",
    "upgrade_tooltip.csv",
    "upgrade_description.csv",
    "bomb_description.csv",
    "blessing_tooltip.csv",
    "cart_desc.csv",
    "map_tooltip.csv",
    "report_tooltip.csv",
    "tooltip_buc.csv",
    "tooltip_crate.csv",
    "active_description.csv",
    "area_report.csv",
    "weapon_keyword.csv",
    "weapon_keyword_ex.csv",
}

UI_FILES = {
    "ui_strings.csv",
    "option_caption.csv",
    "option_tooltip.csv",
    "bestiary_special.csv",
    "bestiary_type.csv",
}

SKIP_FILES = {
    "language_name.csv",
    "mode_name.csv",
    "weapon_name.csv",
    "boss_name.csv",
    "area_name.csv",
    "active_name.csv",
    "bomb_name.csv",
    "blessing_name.csv",
    "cart_name.csv",
    "database_name.csv",
    "rarity_name.csv",
    "roomtype_name.csv",
    "skull_name.csv",
    "special_name.csv",
    "stat_name.csv",
    "unlock_name.csv",
    "upgrade_name.csv",
    "control_display.csv",
    "death_action.csv",
    "death_source_string.csv",
    "debris_string.csv",
    "notification_name.csv",
    "score_caption.csv",
    "credits.csv",
}

DIALOGUE_MAX_VIS = 22
NARRATIVE_MAX_VIS = 42
DESCRIPTION_MAX_VIS = 50
TOOLTIP_MAX_VIS = 25
UI_MAX_VIS = 45
DEFAULT_MAX_VIS = 50


def strip_tags(text: str) -> str:
    """Remove formatting tags, returning only visible text."""
    return TAG_PATTERN.sub("", text)


def vis_len(text: str) -> int:
    """Calculate visible character count (excluding formatting tags)."""
    return len(strip_tags(text))


def break_segment(segment: str, max_vis: int) -> str:
    """Break a segment into lines of max_vis visible chars at word boundaries.

    Preserves formatting tags attached to their words.
    Returns the segment with '#' inserted at break points.
    """
    if vis_len(segment) <= max_vis:
        return segment

    words = segment.split(" ")
    lines: list[str] = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        if vis_len(test) > max_vis and current:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    return "#".join(lines)


def fix_zhs_text(text: str, max_vis: int) -> str:
    """Fix line breaks in ZHS text, respecting existing '#' and '##'."""
    if not text or not text.strip():
        return text

    double_parts = text.split("##")
    fixed_double: list[str] = []

    for dp in double_parts:
        single_parts = dp.split("#")
        fixed_single = [break_segment(seg, max_vis) for seg in single_parts]
        fixed_double.append("#".join(fixed_single))

    return "##".join(fixed_double)


def get_max_vis(filename: str) -> int | None:
    """Return the max visible chars threshold for a file, or None to skip."""
    if filename in SKIP_FILES:
        return None
    if filename in DIALOGUE_FILES:
        return DIALOGUE_MAX_VIS
    if filename in NARRATIVE_FILES:
        return NARRATIVE_MAX_VIS
    if filename in DESCRIPTION_FILES:
        return DESCRIPTION_MAX_VIS
    if filename in TOOLTIP_FILES:
        return TOOLTIP_MAX_VIS
    if filename in UI_FILES:
        return UI_MAX_VIS
    return DEFAULT_MAX_VIS


def detect_line_ending(content: str) -> str:
    """Detect whether file uses CRLF or LF."""
    if "\r\n" in content:
        return "\r\n"
    return "\n"


def process_file(csv_path: Path, max_vis: int) -> list[tuple[int, str, str]]:
    """Process a CSV file and fix ZHS text. Returns list of (row, old, new)."""
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        raw_content = f.read()

    line_ending = detect_line_ending(raw_content)

    rows = list(csv.reader(raw_content.splitlines()))
    if not rows:
        return []

    header = rows[0]
    if "ZHS" not in header:
        return []

    zi = header.index("ZHS")
    changes: list[tuple[int, str, str]] = []

    for row_num, row in enumerate(rows[1:], start=2):
        if len(row) <= zi:
            continue

        original = row[zi]
        if not original.strip():
            continue

        if not CYRILLIC_PATTERN.search(original):
            continue

        fixed = fix_zhs_text(original, max_vis)

        if fixed != original:
            changes.append((row_num, original, fixed))
            row[zi] = fixed

    if changes:
        buf = StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        for row in rows:
            writer.writerow(row)

        output = buf.getvalue()
        if line_ending == "\r\n":
            output = output.replace("\n", "\r\n")

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            f.write(output)

    return changes


def main() -> None:
    """Run line break fixes on all localization files."""
    total_changes = 0
    file_summaries: list[tuple[str, int]] = []

    for csv_path in sorted(LOCALIZATION_DIR.glob("*.csv")):
        max_vis = get_max_vis(csv_path.name)
        if max_vis is None:
            continue

        changes = process_file(csv_path, max_vis)
        if changes:
            file_summaries.append((csv_path.name, len(changes)))
            total_changes += len(changes)

            for row_num, old, new in changes[:5]:
                old_short = old[:70] + ("..." if len(old) > 70 else "")
                new_short = new[:70] + ("..." if len(new) > 70 else "")
                print(f"  [{row_num}] {old_short}")
                print(f"     -> {new_short}")
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more")
            print()

    print("=" * 60)
    print(f"Total: {total_changes} changes in {len(file_summaries)} files")
    print()
    for fname, count in file_summaries:
        print(f"  {fname}: {count} changes")


if __name__ == "__main__":
    main()
