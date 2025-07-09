import re

def extract_education(text, max_lines=50):
    start_keywords = ["education", "academic", "qualifications"]
    stop_keywords = ["experience", "skills", "projects", "certifications", "summary"]

    lines = text.splitlines()
    section = []
    capture = False
    empty_count = 0

    # Step 1: Capture Education Section
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()

        if not capture and any(line_lower.startswith(kw) for kw in start_keywords):
            capture = True
            continue

        if capture:
            if any(line_lower.startswith(kw) for kw in stop_keywords):
                break

            if line_clean == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                continue
            else:
                empty_count = 0

            section.append(line_clean)

        if capture and len(section) >= max_lines:
            break

    if not section:
        return None

    # Step 2: Parse entries
    education_entries = []
    current = {}

    for line in section:
        if not current.get("degree") and re.search(r"(bachelor|master|secondary|diploma|b\.tech|m\.tech|ph\.d|cbse)", line, re.IGNORECASE):
            current["degree"] = line
        elif not current.get("institution") and re.search(r"(university|college|school|institute)", line, re.IGNORECASE):
            current["institution"] = line
        elif not current.get("duration") and re.search(r"\d{4}.*\d{4}|\d{4}", line):
            current["duration"] = line
        elif not current.get("grade") and re.search(r"(cgpa|percentage|gpa)", line, re.IGNORECASE):
            current["grade"] = line
        else:
            # If degree and institution already captured, assume next entry starts
            if current.get("degree") and current.get("institution"):
                education_entries.append(current)
                current = {}
                # Re-process current line for next record
                if re.search(r"(bachelor|master|secondary|diploma|b\.tech|m\.tech|ph\.d|cbse)", line, re.IGNORECASE):
                    current["degree"] = line
                elif re.search(r"(university|college|school|institute)", line, re.IGNORECASE):
                    current["institution"] = line

    if current:
        education_entries.append(current)

    return education_entries if education_entries else None