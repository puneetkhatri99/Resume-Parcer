import re
import json

def parse_single_insert_sql(file_path, output_path="parsed_skills.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the entire bulk INSERT VALUES section
    match = re.search(r"INSERT INTO `job_skills`.*?VALUES\s*(.+);", content, re.DOTALL)
    if not match:
        print("No INSERT INTO values found.")
        return

    # Extract all tuples (1, 'Accounting', 'Hard Skill', ...)
    raw_entries = re.findall(r"\((.*?)\)", match.group(1), re.DOTALL)
    
    skills = {}
    for entry in raw_entries:
        # Safely split: match either quoted strings or unquoted values
        parts = re.findall(r"'(.*?)'|(\bNULL\b|\d+)", entry)

        values = [p[0] if p[0] else p[1] for p in parts]
        values = [v if v != "NULL" else None for v in values]

        if len(values) >= 3:
            skill = values[1].strip()
            skill_type = values[2].strip().lower() if values[2] else None

            key = skill.lower()
            if key not in skills:
                skills[key] = {
                    "name": skill,
                    "type": skill_type  # like "hard skill", "soft skill"
                }

    # Save as JSON
    with open("../skills/skills.json", "w", encoding="utf-8") as out:
        json.dump(list(skills.values()), out, indent=2)

    print(f"✅ Parsed and saved {len(skills)} unique skills to '../skills/skills.json'.")

# Run it
parse_single_insert_sql("../skills/job_skills.sql")