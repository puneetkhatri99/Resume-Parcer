import spacy
import re
from parser.file_reader import read_file
import json 


nlp = spacy.load("en_core_web_sm")

def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:10]:
        if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){0,3}$", line):
            return line
    doc = nlp("\n".join(lines[:10]))
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+91[-\s]?)?\(?\d{3,5}\)?[-\s]?\d{3}[-\s]?\d{4}', text)
    return match.group(0) if match else None

def extract_social_links(text):
    return re.findall(r'https?://[^\s]+', text)

def extract_section(text, header_keywords):
    pattern = '|'.join([re.escape(h) for h in header_keywords])
    sections = re.split(rf'(?i)\b({pattern})\b', text)
    section_data = {}
    for i, sec in enumerate(sections):
        if sec.strip().lower() in [h.lower() for h in header_keywords] and i + 1 < len(sections):
            section_data[sec.strip()] = sections[i + 1]
    return section_data

def extract_education(section_text):
    edu = []
    blocks = re.split(r'\n{2,}', section_text)
    for block in blocks:
        lines = block.strip().splitlines()
        text = ' '.join(lines)
        degree_match = re.search(r"(Bachelor|Master|B\.Tech|BSc|BA|Diploma|Associate|Ph\.D|M\.Tech|MSc)", text, re.I)
        inst_match = re.search(r"(University|College|Institute|School)[^\n]*", text, re.I)
        year_match = re.search(r"(19|20)\d{2}", text)
        grade_match = re.search(r"GPA[:\s]?[0-9\.]+/?[0-9\.]*", text, re.I)

        if degree_match or inst_match:
            edu.append({
                "degree": degree_match.group(0) if degree_match else None,
                "institution": inst_match.group(0) if inst_match else None,
                "duration": year_match.group(0) if year_match else None,
                "grade": grade_match.group(0) if grade_match else None,
            })
    return edu if edu else None

def extract_experience(section_text):
    jobs = []
    entries = re.split(r'\n{2,}', section_text)
    for entry in entries:
        lines = entry.strip().splitlines()
        text = ' '.join(lines)
        org = re.search(r"(at\s+)?([A-Z][A-Za-z&\s]+(Inc|Ltd|Technologies|Solutions|LLC|Company|Corporation|Pvt\sLtd))", text)
        role = lines[0] if lines else None
        date = re.search(r"(20\d{2}|19\d{2}).*?(20\d{2}|Present)", text, re.I)
        if role and date:
            jobs.append({
                "position": role.strip(),
                "duration": date.group(0),
                "organization": org.group(2) if org else None,
                "description": ' '.join(lines[1:]).strip()
            })
    return jobs if jobs else None

def extract_summary(section_text):
    lines = section_text.strip().splitlines()
    return ' '.join([l.strip() for l in lines if l]) if lines else None


def extract_resume_info(text):
    sections = extract_section(text, [
        "Summary", "Objective", "Education", "Experience",
        "Projects", "Skills", "Certifications"
    ])

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "social_links": extract_social_links(text),
        "summary": extract_summary(sections.get("Summary", sections.get("Objective", ""))),
        "education": extract_education(sections.get("Education", "")),
        "experience": extract_experience(sections.get("Experience", "")),
    }


text = read_file("uploads/file.txt")
text = extract_resume_info(text)
print(json.dumps(text, indent=2))