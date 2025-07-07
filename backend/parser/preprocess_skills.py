import json
import pickle
from sentence_transformers import SentenceTransformer

# Paths
JSON_PATH = "../skills/skills.json"
PICKLE_OUTPUT_PATH = "../skills/skill_embeddings_split.pkl"

print("📦 Loading skills from JSON...")
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ✅ Step 1: Filter valid entries and preserve full objects
hard_skills = [entry for entry in data if entry.get("type", "").lower().startswith("hard")]
soft_skills = [entry for entry in data if entry.get("type", "").lower().startswith("soft")]

print(f"🛠️  {len(hard_skills)} hard skills")
print(f"💬 {len(soft_skills)} soft skills")

# ✅ Step 2: Load the sentence transformer model
print("🧠 Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Step 3: Generate embeddings for skill *names*
print("⚙️  Encoding hard skill embeddings...")
hard_embeddings = model.encode([s["name"] for s in hard_skills], convert_to_tensor=True, show_progress_bar=True)

print("⚙️  Encoding soft skill embeddings...")
soft_embeddings = model.encode([s["name"] for s in soft_skills], convert_to_tensor=True, show_progress_bar=True)

# ✅ Step 4: Save full objects and embeddings
print(f"💾 Saving to: {PICKLE_OUTPUT_PATH}")
with open(PICKLE_OUTPUT_PATH, "wb") as f:
    pickle.dump({
        "hard_skills": hard_skills,               # list of dicts
        "hard_embeddings": hard_embeddings,
        "soft_skills": soft_skills,               # list of dicts
        "soft_embeddings": soft_embeddings
    }, f)

print("🎉 Done! Skill embeddings with types saved.")