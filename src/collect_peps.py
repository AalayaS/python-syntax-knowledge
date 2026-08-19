import requests
from pathlib import Path

from dataset import PEP_DATASET


BASE_URL = "https://peps.python.org/pep-{:04d}/"
OUTPUT_DIR = Path("data/raw")


def download_pep(pep_number):
    url = BASE_URL.format(pep_number)

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    output_file = OUTPUT_DIR / f"pep_{pep_number:04d}.html"
    output_file.write_text(response.text, encoding="utf-8")

    print(f"Downloaded PEP {pep_number}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for pep in PEP_DATASET:
        try:
            download_pep(pep["number"])
        except requests.RequestException as error:
            print(f"Could not download PEP {pep['number']}: {error}")


if __name__ == "__main__":
    main()