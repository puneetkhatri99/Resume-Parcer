import re
import pickle
import spacy
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

# Load NLP and embedding models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load precomputed skill data
with open("skills/skill_embeddings_split.pkl", "rb") as f:
    skill_data = pickle.load(f)

hard_skills = skill_data["hard_skills"]
hard_embeddings = skill_data["hard_embeddings"]
soft_skills = skill_data["soft_skills"]
soft_embeddings = skill_data["soft_embeddings"]

def normalize_skill(name):
    return re.sub(r'\d+(\.\d+)?', '', name).strip().lower()

# Email extractor
def extract_email(text):
    match = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match[0] if match else None

# Phone number extractor
def extract_phone(text):
    match = re.findall(r"(?:\+91[-\s]?)?\(?\d{3,5}\)?[-\s]?\d{5,10}", text)
    return match[0] if match else None

# Name extractor
def extract_name(text, email=None):
    lines = text.strip().splitlines()
    for line in lines[:5]:
        line = line.strip()
        if re.match(r"^[A-Z][A-Z ]{2,30}$", line):
            words = line.split()
            if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
                return line.title()
        if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){0,3}$", line):
            return line
    if email:
        name_part = email.split("@")[0]
        name_part = re.sub(r'[\W\d_]+', ' ', name_part)
        return ' '.join(word.capitalize() for word in name_part.split())
    return None

# FIXED: Improved summary extractor
def extract_summary(text):
    summary_headings = [
        "summary", "professional summary", "objective", "career objective",
        "career summary", "profile", "personal profile", "about me", "overview"
    ]
    stop_keywords = [
        "education", "experience", "projects", "certification", "skills",
        "technical skills", "achievements", "work history", "employment"
    ]

    lines = text.splitlines()
    summary_lines = []
    capture = False
    empty_count = 0

    for i, line in enumerate(lines):
        line_clean = line.strip()
        line_lower = line_clean.lower()

        # FIXED: More flexible heading matching - check if heading appears at start of line
        if not capture:
            for heading in summary_headings:
                # Match heading at start of line, optionally followed by colon, dash, or whitespace
                if re.match(rf"^{re.escape(heading)}[:\-\s]", line_lower) or line_lower == heading:
                    capture = True
                    break
            if capture:
                continue

        if capture:
            # Stop if we encounter another section heading
            if any(kw in line_lower for kw in stop_keywords):
                break
            
            # Handle empty lines
            if line_clean == "":
                empty_count += 1
                if empty_count >= 2:  # Stop after 2 consecutive empty lines
                    break
                continue
            
            empty_count = 0
            
            # Stop if we encounter an all-caps section header
            if re.fullmatch(r"[A-Z ]{3,}$", line_clean):
                break
            
            # Skip lines that look like section headers
            if re.match(r"^[A-Z][A-Z\s]+[:\-]?\s*$", line_clean) and len(line_clean.split()) <= 3:
                break
                
            summary_lines.append(" ".join(line_clean.split()))
            if len(summary_lines) >= 10:  # Limit summary length
                break

    # If we found content through line-by-line parsing
    if summary_lines:
        summary = " ".join(summary_lines).strip()
        summary = re.sub(r"\s{2,}", " ", summary)
        return summary

    # IMPROVED: Fallback method - look for summary content after headings
    full_text = text.lower()
    for heading in summary_headings:
        # Look for heading followed by colon or newline
        patterns = [
            rf"{re.escape(heading)}[:\-]\s*(.+?)(?=\n\s*(?:{'|'.join(stop_keywords)})|$)",
            rf"{re.escape(heading)}\s*\n\s*(.+?)(?=\n\s*(?:{'|'.join(stop_keywords)})|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if match:
                summary_text = match.group(1).strip()
                # Clean up the extracted text
                summary_text = re.sub(r'\s+', ' ', summary_text)
                # Limit length to avoid capturing too much
                sentences = summary_text.split('.')
                if len(sentences) > 5:
                    summary_text = '.'.join(sentences[:5]) + '.'
                return summary_text

    return None


def extract_all_sections(text, section_keywords, stop_keywords=None, max_lines=30):
    lines = text.splitlines()
    sections = []
    section = []
    capture = False
    current_heading = ""

    def flush_section():
        if section:
            flat = []
            for line in section:
                if isinstance(line, str):
                    flat.append(line.strip())
                elif isinstance(line, list):
                    flat.extend(str(item).strip() for item in line)
                else:
                    flat.append(str(line).strip())

            sections.append({
                "heading": current_heading,
                "content": "\n".join(flat).strip()
            })

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if any(keyword in line_lower for keyword in section_keywords):
            flush_section()
            capture = True
            current_heading = line_stripped
            section = []
            continue

        if capture and stop_keywords and any(stop in line_lower for stop in stop_keywords):
            flush_section()
            capture = False
            section = []
            current_heading = ""
            continue

        if capture:
            section.append(line_stripped)
            if len(section) >= max_lines:
                flush_section()
                capture = False
                section = []
                current_heading = ""

    if capture:
        flush_section()

    return sections


def extract_skills_section(text):
    return extract_all_sections(
        text,
        section_keywords=["skills", "technical skills", "tools", "technologies"],
        stop_keywords=["experience", "education", "projects", "summary", "certification"]
    )

# -------------------------
# 🧠 Semantic skill matcher
# -------------------------
def match_skills_from_resume(text, skills, embeddings, top_k=15, threshold=0.50):
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
            results.append({
                "name": skill["name"],
                "score": round(float(sim_scores[i]), 3),
                "type": skill["type"]
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


# UPDATED: Final resume info extractor with improved skill extraction
def extract_resume_info(text):
    email = extract_email(text)
    phone = extract_phone(text)
    name = extract_name(text, email)
    summary = extract_summary(text)

    skills_text = text  # extract_skills_section(text)
    # if not skills_text.strip():
    #     skills_text = text  # fallback if "Skills" section not found

    semantic_hard = match_skills_from_resume(skills_text, hard_skills, hard_embeddings)
    semantic_soft = match_skills_from_resume(skills_text, soft_skills, soft_embeddings)
    
    # Use enhanced keyword extraction
    keyword_hard = extract_skills_with_keywords(skills_text, hard_skills)
    keyword_soft = extract_skills_with_keywords(skills_text, soft_skills)

    merged_hard = merge_skills(semantic_hard, keyword_hard)
    merged_soft = merge_skills(semantic_soft, keyword_soft)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "hard_skills": merged_hard,
        "soft_skills": merged_soft,
    }

# Optional: Helper function to debug summary extraction
def debug_summary_extraction(text):
    """Helper function to debug why summary extraction might be failing"""
    print("=== DEBUGGING SUMMARY EXTRACTION ===")
    lines = text.splitlines()
    print(f"Total lines: {len(lines)}")
    print("First 10 lines:")
    for i, line in enumerate(lines[:10]):
        print(f"{i+1}: '{line.strip()}'")
    
    summary_headings = [
        "summary", "professional summary", "objective", "career objective",
        "career summary", "profile", "personal profile", "about me", "overview"
    ]
    
    print("\nLooking for these headings:", summary_headings)
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        for heading in summary_headings:
            if heading in line_lower:
                print(f"Found potential heading on line {i+1}: '{line.strip()}'")
    
    result = extract_summary(text)
    print(f"\nExtracted summary: {result}")
    return result