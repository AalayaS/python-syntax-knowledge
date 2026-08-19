from pathlib import Path
from bs4 import BeautifulSoup
import re


RAW_DIR = Path("data/raw")

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()
def parse_pep(pep_number):
    file_path = RAW_DIR / f"pep_{pep_number:04d}.html"

    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # The actual PEP title is stored in the page title.
    page_title = soup.find("title")

    title = ""
    if page_title:
        title = page_title.get_text(" ", strip=True)

        # Remove the site suffix if present.
        title = title.split("|")[0].strip()

    sections = []

    for heading in soup.find_all(["h2", "h3"]):
        section_title = clean_text(
            heading.get_text(" ", strip=True)
        )

        content = []

        current = heading.find_next_sibling()

        while current:
            if current.name in ["h2", "h3"]:
                break

            text = clean_text(
                current.get_text(" ", strip=True)
            )

            if text:
                content.append(text)

            current = current.find_next_sibling()

        sections.append({
            "title": section_title,
            "level": heading.name,
            "content": "\n".join(content),
        })

    return {
        "number": pep_number,
        "title": title,
        "sections": sections,
    }


if __name__ == "__main__":
    pep = parse_pep(572)

    print("PEP:", pep["number"])
    print("TITLE:", pep["title"])
    print("\nSECTIONS:")

    for section in pep["sections"]:
        print(f"- [{section['level']}] {section['title']}")