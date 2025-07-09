import re

def extract_social_links(text):
    social_domains = [
        "linkedin.com", "github.com", "leetcode.com",
        "portfolio", "behance.net", "medium.com"
    ]
    
    # Regex to catch both https:// and bare social domains
    pattern = re.compile(r'(?:(?:https?://)?(?:www\.)?)?((?:' + '|'.join(re.escape(d) for d in social_domains) + r')[^\s,]+)', re.IGNORECASE)
    
    matches = pattern.findall(text)
    
    # Normalize: add https:// if missing
    links = []
    for match in matches:
        url = match.strip("—– ").strip()
        if not url.startswith("http"):
            url = "https://" + url
        links.append(url)

    # Remove duplicates and return as a JSON-safe list
    return list(sorted(set(links)))