import json
import faiss
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# === CONFIG ===
INPUT_JSON = "../skills/skills.json"
OUTPUT_JSON = "../skills/dedupli_skills.json"
SIMILARITY_THRESHOLD = 0.7

# === Load skill data ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    skills = json.load(f)

skill_names = [entry["name"] for entry in skills]

# === Load model and encode
print("🧠 Encoding skills with SentenceTransformer...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(skill_names, convert_to_numpy=True, show_progress_bar=True)

# === Normalize vectors for cosine similarity
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# === Build FAISS index
print("⚡ Building FAISS index...")
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

# === Deduplicate with FAISS search
print("🔍 Deduplicating with FAISS...")
seen = set()
unique_skills = []

for i in tqdm(range(len(embeddings))):
    if i in seen:
        continue

    D, I = index.search(embeddings[i:i+1], 50)  # Top 50 matches
    for j, score in zip(I[0], D[0]):
        if score >= SIMILARITY_THRESHOLD:
            seen.add(j)

    unique_skills.append(skills[i])

# === Save result
print(f"✅ Reduced {len(skills)} → {len(unique_skills)} unique skills")
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(unique_skills, f, indent=2)

print(f"💾 Saved to {OUTPUT_JSON}")