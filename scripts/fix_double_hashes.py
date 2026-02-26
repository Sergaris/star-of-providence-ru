import csv
import os
import glob
import re

dir_path = "star-of-providence-ru/localization"
files = glob.glob(os.path.join(dir_path, "*.csv"))

issues_fixed = 0

for filepath in files:
    changed = False
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        try:
            en_idx = header.index("EN")
            zhs_idx = header.index("ZHS")
        except ValueError:
            continue
            
        rows = [header]
        for row in reader:
            if len(row) > max(en_idx, zhs_idx):
                en_text = row[en_idx]
                ru_text = row[zhs_idx]
                
                en_double_hashes = en_text.count("##")
                ru_double_hashes = ru_text.count("##")
                
                if en_double_hashes > 0 and ru_double_hashes == 0:
                    # Specific fixes based on patterns
                    
                    # Pattern 1: Missing ## before /c5 or /c4
                    if "##/c5" in en_text and "/c5" in ru_text and "##/c5" not in ru_text:
                        ru_text = ru_text.replace(" /c5", "##/c5").replace("#/c5", "##/c5")
                    elif "##/c4" in en_text and "/c4" in ru_text and "##/c4" not in ru_text:
                        ru_text = ru_text.replace(" /c4", "##/c4").replace("#/c4", "##/c4")
                    
                    # Pattern 2: Credits file
                    elif filepath.endswith("credits.csv"):
                        if "programming:" in en_text:
                            ru_text = ru_text.replace("программирование:#", "программирование:##")
                        elif "art and direction:" in en_text:
                            ru_text = ru_text.replace("руководство:#", "руководство:##")
                        elif "music and sfx:" in en_text:
                            ru_text = ru_text.replace("звуки:#", "звуки:##")
                        elif "splash art:" in en_text:
                            ru_text = ru_text.replace("арт:#", "арт:##")
                        elif "mmx#" in en_text:
                            ru_text = ru_text.replace("aquamancia#и", "aquamancia##и")
                        elif "jec#" in en_text:
                            ru_text = ru_text.replace("vine#и", "vine##и")
                            
                    # Pattern 3: Crate strings
                    elif filepath.endswith("crate_strings.csv") and "##/c5contains:" in en_text:
                        ru_text = ru_text.replace(" /c5содержит:", "##/c5содержит:")
                        
                    # Pattern 4: Upgrade description
                    elif filepath.endswith("upgrade_description.csv") and "increases maximum" in en_text:
                        ru_text = ru_text.replace("макс. ОЗ +1/3 блокирует", "макс. ОЗ +1/3##блокирует")
                        
                    # Pattern 5: UI strings
                    elif filepath.endswith("ui_strings.csv") and "save discrepancy detected" in en_text:
                        ru_text = ru_text.replace("сохранений какое", "сохранений##какое")

                    # Pattern 6: bestiary_entry.csv (Manual mappings for complex cases)
                    elif filepath.endswith("bestiary_entry.csv"):
                        ru_text = ru_text.replace("прежней. что-то", "прежней.##что-то")
                        ru_text = ru_text.replace("себя? вступай", "себя?##вступай")
                        ru_text = ru_text.replace("топливо. сущность", "топливо.##сущность")
                        ru_text = ru_text.replace("парни. сначала", "парни.##сначала")
                        ru_text = ru_text.replace("экстракторам. они", "экстракторам.##они")
                        ru_text = ru_text.replace("мышь. воистину", "мышь.##воистину")
                        ru_text = ru_text.replace("уровнях. пожалуйста", "уровнях.##пожалуйста")
                        ru_text = ru_text.replace("начала.#он", "начала.##он")
                        ru_text = ru_text.replace("ответственно. прямой", "ответственно.##прямой")
                        ru_text = ru_text.replace("огненная магия: 1 магия", "огненная магия: 1##магия")
                        ru_text = ru_text.replace("криомагии. слишком", "криомагии.##слишком")
                        ru_text = ru_text.replace("из смерти — сила. из силы", "из смерти — сила.##из силы")
                        ru_text = ru_text.replace("из жизни — смерть. из смерти", "из жизни — смерть.##из смерти")
                        ru_text = ru_text.replace("восстановленный. в", "восстановленный.##в")
                        ru_text = ru_text.replace("времени. восстановленный.", "времени.##восстановленный.")
                        ru_text = ru_text.replace("этажей: кому", "этажей:##кому")
                        ru_text = ru_text.replace("особенный. все", "особенный.##все")
                        ru_text = ru_text.replace("незначительными.#они", "незначительными.##они")
                        ru_text = ru_text.replace("гахахаха! новый", "гахахаха!##новый")
                        ru_text = ru_text.replace("секции. не", "секции.##не")
                        ru_text = ru_text.replace("самостоятельно. ни", "самостоятельно.##ни")
                        ru_text = ru_text.replace("войну. целые", "войну.##целые")
                        ru_text = ru_text.replace("ревизия №5. пришлось", "ревизия №5##пришлось")
                        ru_text = ru_text.replace("смертоядро.#простите", "смертоядро.##простите")
                        ru_text = ru_text.replace("привычки.#в рейтинге", "привычки.##в рейтинге")
                        ru_text = ru_text.replace("в руках. давно", "в руках.##давно")
                        ru_text = ru_text.replace("меня. мне", "меня.##мне")
                        ru_text = ru_text.replace("серьёзными. возможно", "серьёзными.##возможно")
                        ru_text = ru_text.replace("ритуал: попытался", "ритуал:##попытался")
                        ru_text = ru_text.replace("повторилась. яркая", "повторилась.##яркая")
                        ru_text = ru_text.replace("интересно. эта", "интересно.##эта")
                        ru_text = ru_text.replace("мире. и ты", "мире.##и ты")
                        ru_text = ru_text.replace("спасению. хотя", "спасению.##хотя")
                        ru_text = ru_text.replace("обнаружено.#обновление", "обнаружено.##обновление")

                    if ru_text != row[zhs_idx]:
                        row[zhs_idx] = ru_text
                        changed = True
                        issues_fixed += 1
                        
            rows.append(row)
            
    if changed:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
            
print(f"Fixed {issues_fixed} missing double hashes.")
