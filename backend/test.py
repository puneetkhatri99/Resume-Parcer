from parser.extractor import (extract_skills_section)
from parser.file_reader import read_file

text = read_file("uploads/file.txt")
skills_text = extract_skills_section(text)
    
if not skills_text.strip():
    skills_text = text
else:
    print(skills_text)