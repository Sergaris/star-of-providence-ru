import csv
import os
import glob

dir_path = "star-of-providence-ru/localization"
files = glob.glob(os.path.join(dir_path, "*.csv"))

issues = []

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        try:
            en_idx = header.index("EN")
            zhs_idx = header.index("ZHS")
        except ValueError:
            continue
            
        for row_num, row in enumerate(reader, start=2):
            if len(row) > max(en_idx, zhs_idx):
                en_text = row[en_idx]
                ru_text = row[zhs_idx]
                
                # Check for ## mismatch
                en_double_hashes = en_text.count("##")
                ru_double_hashes = ru_text.count("##")
                
                if en_double_hashes > 0 and ru_double_hashes == 0:
                    issues.append({
                        "file": os.path.basename(filepath),
                        "row": row_num,
                        "en": en_text,
                        "ru": ru_text
                    })

for issue in issues:
    print(f"[{issue['file']}:{issue['row']}]")
    print(f"EN: {issue['en']}")
    print(f"RU: {issue['ru']}")
    print("-" * 60)

print(f"Found {len(issues)} issues.")