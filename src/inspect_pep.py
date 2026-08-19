from pathlib import Path
from bs4 import BeautifulSoup


def extract_text(pep_number):
    file_path = Path("data/raw") / f"pep_{pep_number:04d}.html"

    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    return soup.get_text("\n", strip=True)


if __name__ == "__main__":
    text = extract_text(695)

    print(text[:10000])