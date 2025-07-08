from parser.extractor import  extract_resume_info
from parser.file_reader import read_file

text = read_file("uploads/Puneet_CV.pdf")
print(extract_resume_info(text))