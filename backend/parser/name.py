import spacy
import re

nlp = spacy.load("en_core_web_sm")

# def extract_name(text):
#     # Only analyze top part of resume (first 100 characters is usually enough)
#     doc = nlp(text)
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             return ent.text
#     return None

# def extract_name(text):
#     # Step 1: Look at only the top 10 non-empty lines
#     lines = [line.strip() for line in text.splitlines() if line.strip()]
#     top_lines = lines[:10]

#     # Step 2: Try matching lines that look like names
#     name_regex = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){0,3}$")
#     for line in top_lines:
#         if name_regex.match(line):
#             return line

#     # Step 3: Fallback to spaCy NER on top 500 chars
#     doc = nlp("\n".join(top_lines))
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             return ent.text

#     return None

# import re

def extract_name(text, email=None):
    lines = text.strip().splitlines()
    for line in lines[:10]:  # Check top 10 lines for flexibility
        line = line.strip()

        # Case 1: All uppercase, like "IM A SAMPLE IV"
        if re.match(r"^[A-Z][A-Z\s\.]{2,}$", line):
            words = line.split()
            if 1 < len(words) <= 5 and all(re.match(r"^[A-Z]{1,3}\.?$", w) or w.isalpha() for w in words):
                return line.title()

        # Case 2: Title case with possible initials, like "Lorem I Ipsum" or "John A. Doe"
        if re.match(r"^[A-Z][a-z]+(?: [A-Z]\.?| [A-Z][a-z]+){0,3}$", line):
            return line

    # Fallback: Derive from email username
    if email:
        name_part = email.split("@")[0]
        name_part = re.sub(r'[\W\d_]+', ' ', name_part)
        return ' '.join(word.capitalize() for word in name_part.split())

    return None

# def extract_name(text, email=None):
#     lines = text.strip().splitlines()
#     for line in lines[:5]:
#         line = line.strip()
#         if re.match(r"^[A-Z][A-Z ]{2,30}$", line):
#             words = line.split()
#             if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
#                 return line.title()
#         if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){0,3}$", line):
#             return line
#     if email:
#         name_part = email.split("@")[0]
#         name_part = re.sub(r'[\W\d_]+', ' ', name_part)
#         return ' '.join(word.capitalize() for word in name_part.split())
#     return None