import pickle
from .name import extract_name
from .skills import match_skills_from_resume, extract_skills_with_keywords, merge_skills
from .email import extract_email , extract_phone
from .social import extract_social_links
from .summary import extract_summary
from .experience import extract_experience, extract_structured_experience
from .projects import extract_projects
from .education import extract_education  


with open("skills/skill_embeddings_split.pkl", "rb") as f:
    skill_data = pickle.load(f)

hard_skills = skill_data["hard_skills"]
hard_embeddings = skill_data["hard_embeddings"]
soft_skills = skill_data["soft_skills"]
soft_embeddings = skill_data["soft_embeddings"]


def extract_resume_info(text):
    email = extract_email(text)
    phone = extract_phone(text)
    name = extract_name(text)
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