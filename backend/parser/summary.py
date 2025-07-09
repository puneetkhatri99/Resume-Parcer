import re

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
