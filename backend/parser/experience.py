import re

def extract_experience(text, max_lines=80):

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
        # normalized = line_lower.strip().replace(":", "")

        # Start capturing
       
        if not capture and any(line_lower.startswith(keyword) for keyword in experience_keywords):
            capture = True
            continue

        # Stop capturing at known boundaries
        if capture:
            if any(line_lower.startswith(kw) for kw in stop_keywords):
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
    lines = text.splitlines()
    experiences = []
    current_exp = None
    description = []

    # Pattern to detect line with position and duration
    pattern = re.compile(r"(?P<position>.+?)\s+(?P<duration>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[–-]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4})", re.IGNORECASE)

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for position line
        match = pattern.match(line)
        if match:
            # Save previous entry
            if current_exp:
                current_exp["description"] = description
                experiences.append(current_exp)
                description = []

            # Prepare new entry
            position = match.group("position").strip()
            duration = match.group("duration").strip()

            # Company is likely in the next line
            i += 1
            company = lines[i].strip() if i < len(lines) else ""

            current_exp = {
                "position": position,
                "company": company,
                "duration": duration,
                "location": "",  # Optional: extract if available
                "description": []
            }
        elif current_exp and line.startswith("-"):
            description.append(line)
        elif current_exp and re.match(r"^[A-Z ]{3,}$", line):
            # Possibly next section like "PROJECTS"
            break
        elif current_exp:
            description.append(line)

        i += 1

    # Add final
    if current_exp:
        current_exp["description"] = description
        experiences.append(current_exp)

    return experiences if experiences else None

