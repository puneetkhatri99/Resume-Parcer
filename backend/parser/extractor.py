import re
import pickle
import spacy
from sentence_transformers import SentenceTransformer, util
from urllib.parse import urlparse

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


# === HELPERS ===

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r"(?:\+91[-\s]?)?\(?\d{3,5}\)?[-\s]?\d{5,10}", text)
    return match.group(0) if match else None

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


def extract_social_links(text):
    # Extract all potential URLs
    raw_urls = re.findall(r'https?://[^\s,;)\]]+', text)

    # Define known social platforms (lowercased)
    platforms = {
        "linkedin": "LinkedIn",
        "github": "GitHub",
        "portfolio": "Portfolio",
        "behance": "Behance",
        "medium": "Medium",
        "twitter": "Twitter",
        "leetcode": "LeetCode",
        "dribbble": "Dribbble",
        "dev.to": "Dev.to"
    }

    cleaned = []
    seen = set()

    for url in raw_urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for key in platforms:
            if key in domain or key in parsed.path.lower():
                if url not in seen:
                    seen.add(url)
                    cleaned.append({
                        "platform": platforms[key],
                        "url": url
                    })

    return cleaned

def extract_section(text, start_keywords, stop_keywords=None, max_lines=40):
    lines = text.splitlines()
    capture = False
    section = []
    for line in lines:
        line_lower = line.lower().strip()
        if not capture and any(k in line_lower for k in start_keywords):
            capture = True
            continue
        if capture and stop_keywords and any(k in line_lower for k in stop_keywords):
            break
        if capture:
            section.append(line.strip())
            if len(section) >= max_lines:
                break
    return "\n".join(section).strip() if section else None

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



def extract_experience(text, max_lines=40):

    experience_keywords = [
        "experience", "professional experience", "work experience", "employment",
        "internship", "work history", "career", "job experience", "industry experience"
    ]
    stop_keywords = [
        "education", "academic", "skills", "projects", "certification", "summary", "profile"
    ]

    lines = text.splitlines()
    section = []
    capture = False
    empty_count = 0

    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        normalized = line_lower.strip().replace(":", "")

        # Start capturing
       
        if not capture and any(line_lower.startswith(keyword) for keyword in experience_keywords):
            capture = True
            continue

        # Stop capturing at known boundaries
        if capture:
            if any(kw in normalized for kw in stop_keywords):
                break

            # Count blank lines to decide if section has ended
            if line_clean == "":
                empty_count += 1
                if empty_count >= 5:
                    break
                continue
            else:
                empty_count = 0  # reset

            section.append(line_clean)

        if capture and len(section) >= max_lines:
            break

    return "\n".join(section).strip() if section else None


def extract_structured_experience(text):
    
    experience_text = extract_experience(text)
    lines = experience_text.splitlines()
    experiences = []
    current_exp = {}
    description_lines = []

    # Pattern to match lines like:
    # Web Development Intern – BWorth Technologies Pvt Ltd Sep 2024 – Nov 2024
    position_line_pattern = re.compile(
        r"(?P<position>.+?)\s+[-–]\s+(?P<company>.+?)\s+(?P<duration>(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4}\s*[–-]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4})",
        re.IGNORECASE
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = position_line_pattern.match(line)
        if match:
            # Save previous experience
            if current_exp:
                current_exp["description"] = description_lines
                experiences.append(current_exp)
                current_exp = {}
                description_lines = []

            # Start new experience
            current_exp = {
                "position": match.group("position").strip(),
                "company": match.group("company").strip(),
                "location": "",  # You can improve this later
                "duration": match.group("duration").strip(),
            }
        elif current_exp:
            description_lines.append(line)

    # Save the last one
    if current_exp:
        current_exp["description"] = description_lines
        experiences.append(current_exp)

    return experiences if experiences else None

def extract_projects(text):
    return extract_section(text, ["projects", "portfolio"],
                           ["experience", "education", "skills", "certifications"])

def extract_education(text):
    return extract_section(text, ["education", "academic", "qualification"],
                           ["experience", "skills", "projects", "certifications"])

# === Skill Matching ===

def match_skills_from_resume(text, skills, embeddings, top_k=20, threshold=0.55):
    text_emb = model.encode(text, convert_to_tensor=True)
    sim_scores = util.cos_sim(text_emb, embeddings)[0]
    top_indices = [i for i in sim_scores.argsort(descending=True) if sim_scores[i] > threshold][:top_k]

    results = set()
    for i in top_indices:
        skill_name = skills[i]["name"].strip()
        results.add(skill_name)
    return results

# Keyword match skills
def extract_skills_with_keywords(text, canonical_skills):
    text_lower = text.lower()
    found = set()

    for skill in canonical_skills:
        name = skill["name"].strip()
        if name.lower() in text_lower:
            found.add(name)
    return found

# Merge keyword + semantic sets
def merge_skills(semantic, keyword):
    return sorted(list(semantic | keyword))

# === Final Resume Extractor ===

def extract_resume_info(text):
    email = extract_email(text)
    phone = extract_phone(text)
    name = extract_name(text, email)
    summary = extract_summary(text)
    experience = extract_structured_experience(text)
    education = extract_education(text)
    projects = extract_projects(text)
    social_links = extract_social_links(text)

    keyword_hard = extract_skills_with_keywords(text, hard_skills)
    keyword_soft = extract_skills_with_keywords(text, soft_skills)
    semantic_hard = match_skills_from_resume(text, hard_skills, hard_embeddings)
    semantic_soft = match_skills_from_resume(text, soft_skills, soft_embeddings)

    hard = merge_skills(semantic_hard, keyword_hard)
    soft = merge_skills(semantic_soft, keyword_soft)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "social_links": social_links,
        "education": education,
        "experience": experience,
        "projects": projects,
        "hard_skills": hard,
        "soft_skills": soft
    }