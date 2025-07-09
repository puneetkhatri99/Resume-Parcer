import pickle
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("skills/skill_embeddings_split.pkl", "rb") as f:
    skill_data = pickle.load(f)

hard_skills = skill_data["hard_skills"]
hard_embeddings = skill_data["hard_embeddings"]
soft_skills = skill_data["soft_skills"]
soft_embeddings = skill_data["soft_embeddings"]


def match_skills_from_resume(text, skills, embeddings, top_k=8, threshold=0.65):
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
