
import re
import pickle
import json
import spacy
from sentence_transformers import SentenceTransformer, util

# ✅ Load NLP model (spaCy) for name extraction
nlp = spacy.load("en_core_web_sm")

# ✅ Load transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Load skill data with precomputed embeddings

def extract_skills_section(text):
    lines = text.splitlines()
    skills_lines = []
    capture = False

    for line in lines:
        line_lower = line.lower().strip()
        if any(h in line_lower for h in ["skills", "technical skills", "technologies", "tools"]):
            capture = True
            continue

        if capture and any(h in line_lower for h in ["experience", "education", "projects", "certification", "summary"]):
            break

        if capture and len(line.strip()) > 0:
            skills_lines.append(line.strip())

    return "\n".join(skills_lines)


with open("skills/skill_embeddings_split.pkl", "rb") as f:
    skill_data = pickle.load(f)

hard_skills = skill_data["hard_skills"]
hard_embeddings = skill_data["hard_embeddings"]
soft_skills = skill_data["soft_skills"]
soft_embeddings = skill_data["soft_embeddings"]

# -------------------------
# 📧 Email extraction
# -------------------------
def extract_email(text):
    match = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match[0] if match else None

# -------------------------
# 📞 Phone number extraction
# -------------------------
def extract_phone(text):
    match = re.findall(r"(?:\+91[-\s]?)?\(?\d{3,5}\)?[-\s]?\d{5,10}", text)
    return match[0] if match else None

# -------------------------
# 🙋 Name extraction
# -------------------------
import re

def extract_name(text, email=None):
    try:
        lines = text.strip().splitlines()

        # Try name from first 5 lines
        for line in lines[:5]:
            line = line.strip()

            # Accept names like "NISCHAY SHARMA" or "Nischay Sharma"
            if re.match(r"^[A-Z][A-Z ]{2,30}$", line):  # All uppercase, 2+ words
                words = line.split()
                if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
                    return line.title()  # Convert to title case

            # Or capitalized names like "Nischay Sharma"
            if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){0,3}$", line):
                return line

        # Fallback: extract from email
        if email:
            name_part = email.split("@")[0]
            name_part = re.sub(r'[\W\d_]+', ' ', name_part)  # remove digits/symbols
            return ' '.join(word.capitalize() for word in name_part.split())

        return None
    except Exception as e:
        print(f"[⚠️ Name Extraction Error] {e}")
        return None
# -------------------------
# 📝 Summary extraction
# -------------------------
def extract_summary(text):
    summary_headings = ["professional summary", "summary", "objective", "career summary", "profile"]
    lines = text.lower().splitlines()

    for i, line in enumerate(lines):
        if any(h in line for h in summary_headings):
            summary_lines = []
            for j in range(i + 1, min(i + 8, len(lines))):
                next_line = lines[j].strip()
                if next_line == "" or len(next_line.split()) < 3:
                    break
                summary_lines.append(next_line)
            return " ".join(summary_lines).strip().capitalize()

    return None

# -------------------------
# 🧠 Semantic skill matcher
# -------------------------
def match_skills_from_resume(text, skills, embeddings, top_k=15, threshold=0.45):
    text_emb = model.encode(text, convert_to_tensor=True)
    sim_scores = util.cos_sim(text_emb, embeddings)[0]
    top_indices = [i for i in sim_scores.argsort(descending=True) if sim_scores[i] > threshold][:top_k]

    seen = set()
    results = []
    for i in top_indices:
        skill = skills[i]
        name_key = skill["name"].lower().strip()
        if name_key not in seen:
            seen.add(name_key)
            score = float(sim_scores[i])
            results.append({
                "name": skill["name"],
                "score": round(score, 3),
                "type": skill["type"],
                "source": "semantic",
                "confidence": "fuzzy" if score < 0.6 else "high"
            })
    return results

# -------------------------
# 🔍 Keyword-based matcher
# -------------------------
def extract_skills_with_keywords(text, canonical_skills):
    text_lower = text.lower()
    found = []
    seen = set()

    for skill in canonical_skills:
        name = skill["name"].strip()
        if name.lower() in text_lower and name.lower() not in seen:
            seen.add(name.lower())
            found.append({
                "name": name,
                "score": 1.0,
                "type": skill["type"]
            })
    return found

# -------------------------
# 🔀 Merge skill sets
# -------------------------
def merge_skills(semantic, keyword):
    seen = set()
    merged = []
    for s in keyword + semantic:  # prioritize exact matches
        key = s["name"].lower()
        if key not in seen:
            seen.add(key)
            merged.append(s)
    return merged

# -------------------------
# 🧩 Final Resume Extractor
# -------------------------
def extract_resume_info(text):
    # Hybrid skill extraction
    semantic_hard = match_skills_from_resume(text, hard_skills, hard_embeddings)
    semantic_soft = match_skills_from_resume(text, soft_skills, soft_embeddings)
    keyword_hard = extract_skills_with_keywords(text, hard_skills)
    keyword_soft = extract_skills_with_keywords(text, soft_skills)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "summary": extract_summary(text),
        "hard_skills": merge_skills(semantic_hard, keyword_hard),
        "soft_skills": merge_skills(semantic_soft, keyword_soft)
    }

# -------------------------
# 🧪 CLI Example
# -------------------------
if __name__ == "__main__":
    with open("sample_resume.txt", "r", encoding="utf-8") as f:
        resume_text = f.read()

    parsed = extract_resume_info(resume_text)
    print(json.dumps(parsed, indent=2))