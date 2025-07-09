import re

def extract_projects(text, max_lines=80):
    """
    Extract the 'Projects' section from resume text.
    Returns a list of project entries (strings).
    """
    start_keywords = ["projects", "portfolio", "personal projects"]
    stop_keywords = ["experience", "education", "skills", "certification", "summary"]

    lines = text.splitlines()
    capture = False
    section = []
    empty_count = 0

    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()

        if not capture and any(line_lower.startswith(kw) for kw in start_keywords):
            capture = True
            continue

        if capture:
            if any(line_lower.startswith(stop) for stop in stop_keywords):
                break

            if line_clean == "":
                empty_count += 1
                if empty_count >= 8:
                    break
                continue
            else:
                empty_count = 0

            section.append(line_clean)

            if len(section) >= max_lines:
                break

    if not section:
        return None

    # Process into structured project list
    projects = []
    current_project = []

    for line in section:
        if re.match(r"^(•|\-|\*)\s+", line) or line == "":
            if current_project:
                projects.append(" ".join(current_project).strip())
                current_project = []
        current_project.append(line)

    if current_project:
        projects.append(" ".join(current_project).strip())

    return projects if projects else None
