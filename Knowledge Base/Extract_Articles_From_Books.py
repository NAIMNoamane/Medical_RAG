import re 
from PyPDF2 import PdfReader
import json


file_names = ["Gale Encyclopedia of Medicine Vol. 1 (A-B).pdf",
              "Gale Encyclopedia of Medicine Vol. 2 (C-F).pdf",
              "Gale Encyclopedia of Medicine Vol. 3 (G-M).pdf",
              "Gale Encyclopedia of Medicine Vol. 4 (N-S).pdf",
              "Gale Encyclopedia of Medicine Vol. 5 (T-Z).pdf"]

for index, file_name in enumerate(file_names) : 
  reader = PdfReader(file_name)
  txt_file=f"Gale_Vol_{index+1}.txt"
  json_file_name=f"Gale_Vol{index}.json" # we will use this after extracting articles


#================== Reading the files ======================

  with open(txt_file,"w",encoding="utf-8") as gale : 
    for i in range(len(reader.pages)):
      gale.write(reader.pages[i].extract_text())
    print(f"Reading {file_name} finished.")

#================== Extracting Articles ====================== 

  with open(txt_file, "r", encoding="utf-8") as galile:
    full_text = galile.read()
    full_text = re.sub(r'\n+', '\n', full_text)

    # Pattern: capture article title (non-empty line) that is followed by 'Definition'
    pattern = r"\n([A-Z][a-zA-Z \-,'()]+)\nDefinition\n"
    matches = list(re.finditer(pattern, full_text))

    articles = []

    for i in range(len(matches)):
        title = matches[i].group(1).strip()
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        content = full_text[start:end].strip()
        articles.append((title, content))
    print(f"Extracting {file_name} Finished")
#================== Loading Articles in JSON Files ======================

  with open(json_file_name, "w", encoding="utf-8") as f:
      json.dump([{"title": t, "content": c} for t, c in articles], f, ensure_ascii=False, indent=2)
      print(f"JSON file is ready")


