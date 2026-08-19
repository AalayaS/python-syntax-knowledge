import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from dataset import PEP_DATASET


RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "knowledge_state.json"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


# ============================================================
# PEP PARSER
# ============================================================

def parse_pep(pep_number):
    file_path = RAW_DIR / f"pep_{pep_number:04d}.html"

    html = file_path.read_text(encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")

    # --------------------------------------------------------
    # Extract page title
    # --------------------------------------------------------

    page_title = soup.find("title")

    title = ""

    if page_title:
        title = page_title.get_text(
            " ",
            strip=True
        )

        title = title.split("|")[0].strip()

    # --------------------------------------------------------
    # Extract H2/H3 sections
    # --------------------------------------------------------

    sections = []

    for heading in soup.find_all(["h2", "h3"]):

        section_title = clean_text(
            heading.get_text(
                " ",
                strip=True
            )
        )

        content = []

        current = heading.find_next_sibling()

        while current:

            # Stop when the next section begins
            if current.name in ["h2", "h3"]:
                break

            text = clean_text(
                current.get_text(
                    " ",
                    strip=True
                )
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


# ============================================================
# ID GENERATOR
# ============================================================

def make_id(prefix, pep_number, index):
    return f"pep_{pep_number}_{prefix}_{index}"


# ============================================================
# EXPLICIT FEATURE CONCEPT MAPPING
#
# IMPORTANT:
# These mappings are OUR domain decisions.
# We are not using an automatic entity/relation extraction tool.
# ============================================================

FEATURE_CONCEPTS = {

    # --------------------------------------------------------
    # Assignment Expressions
    # --------------------------------------------------------

    572: [
        "assignment",
        "expression",
        "variable binding",
        "assignment expression",
        "named expression",
        "walrus operator",
    ],

    # --------------------------------------------------------
    # Structural Pattern Matching
    # --------------------------------------------------------

    634: [
        "pattern matching",
        "match statement",
        "case statement",
        "pattern",
    ],

    635: [
        "pattern matching",
        "match statement",
        "case statement",
        "pattern",
    ],

    636: [
        "pattern matching",
        "match statement",
        "case statement",
        "pattern",
    ],

    # --------------------------------------------------------
    # Type Parameter Syntax
    # --------------------------------------------------------

    695: [
        "type parameters",
        "generic",
        "type variable",
        "type alias",
        "typing",
    ],

    # --------------------------------------------------------
    # Type Hints
    # --------------------------------------------------------

    484: [
        "type hints",
        "typing",
        "type annotations",
        "type variables",
    ],

    # --------------------------------------------------------
    # Parameter Specifications
    # --------------------------------------------------------

    612: [
        "parameter specification",
        "typing",
        "generic",
    ],

    # --------------------------------------------------------
    # Variadic Generics
    # --------------------------------------------------------

    646: [
        "variadic generics",
        "type variables",
        "typing",
        "generic",
    ],
}


# ============================================================
# EXPLICIT PEP EVOLUTION RELATIONSHIPS
#
# These relationships are manually defined from the
# documented history of Python syntax proposals.
#
# PEP 622 was split into:
#   - PEP 634: Specification
#   - PEP 635: Motivation and Rationale
#   - PEP 636: Tutorial
#
# This is NOT automatic entity/relation extraction.
# ============================================================

PEP_EVOLUTION_RELATIONSHIPS = [

    {
        "source": "pep_622",
        "type": "SPLIT_INTO",
        "target": "pep_634",
    },

    {
        "source": "pep_622",
        "type": "SPLIT_INTO",
        "target": "pep_635",
    },

    {
        "source": "pep_622",
        "type": "SPLIT_INTO",
        "target": "pep_636",
    },
]


# ============================================================
# BUILD KNOWLEDGE STATE
# ============================================================

def build_knowledge():

    entities = []

    relationships = []

    # --------------------------------------------------------
    # Process every PEP in our selected dataset
    # --------------------------------------------------------

    for pep_info in PEP_DATASET:

        pep_number = pep_info["number"]

        pep = parse_pep(pep_number)

        pep_id = f"pep_{pep_number}"

        # ====================================================
        # PEP ENTITY
        # ====================================================

        entities.append({
            "id": pep_id,
            "type": "PEP",
            "number": pep_number,
            "title": pep["title"],
        })

        # Counters for generated entity IDs

        alternative_index = 0
        objection_index = 0
        example_index = 0

        # Tracks the current H2 section.
        #
        # Example:
        #
        # H2: Rejected alternative proposals
        #     H3: Alternative spellings
        #
        # The H3 belongs to the H2 above it.

        parent_section = None

        # ====================================================
        # PROCESS SECTIONS
        # ====================================================

        for section in pep["sections"]:

            title = section["title"]

            level = section["level"]

            content = section["content"]

            title_lower = title.lower()

            # ------------------------------------------------
            # Track H2 parent
            # ------------------------------------------------

            if level == "h2":
                parent_section = title

            # =================================================
            # ALTERNATIVES
            # =================================================

            if (
                level == "h3"
                and parent_section
                and (
                    "rejected alternative"
                    in parent_section.lower()

                    or

                    "rejected idea"
                    in parent_section.lower()

                    or

                    parent_section.lower()
                    == "alternatives"
                )
            ):

                alternative_index += 1

                alternative_id = make_id(
                    "alternative",
                    pep_number,
                    alternative_index,
                )

                entities.append({
                    "id": alternative_id,
                    "type": "Alternative",
                    "name": title,
                    "description": content,
                    "status": "rejected",
                    "source_pep": pep_number,
                    "source_section": title,
                })

                relationships.append({
                    "source": pep_id,
                    "type": "CONSIDERS",
                    "target": alternative_id,
                })

            # =================================================
            # OBJECTIONS
            # =================================================

            if (
                level == "h3"
                and parent_section
                and "objection"
                in parent_section.lower()
            ):

                objection_index += 1

                objection_id = make_id(
                    "objection",
                    pep_number,
                    objection_index,
                )

                entities.append({
                    "id": objection_id,
                    "type": "Objection",
                    "name": title,
                    "description": content,
                    "source_pep": pep_number,
                    "source_section": title,
                })

                relationships.append({
                    "source": pep_id,
                    "type": "RAISES",
                    "target": objection_id,
                })

            # =================================================
            # EXAMPLES
            # =================================================

            is_example_section = False

            if "example" in title_lower:
                is_example_section = True

            if (
                parent_section
                and "example"
                in parent_section.lower()
            ):
                is_example_section = True

            if (
                level == "h3"
                and is_example_section
            ):

                example_index += 1

                example_id = make_id(
                    "example",
                    pep_number,
                    example_index,
                )

                entities.append({
                    "id": example_id,
                    "type": "Example",
                    "name": title,
                    "description": content,
                    "source_pep": pep_number,
                    "source_section": title,
                })

                relationships.append({
                    "source": pep_id,
                    "type": "ILLUSTRATES",
                    "target": example_id,
                })

        # ====================================================
        # FEATURE ENTITY
        # ====================================================

        feature_name = pep["title"]

        # PEP titles normally look like:
        #
        # PEP 572 – Assignment Expressions
        #
        # We only keep the feature name.

        if "–" in feature_name:

            feature_name = (
                feature_name
                .split("–", 1)[1]
                .strip()
            )

        elif "-" in feature_name:

            feature_name = (
                feature_name
                .split("-", 1)[1]
                .strip()
            )

        feature_id = (
            f"pep_{pep_number}_feature"
        )

        # ----------------------------------------------------
        # Get our manually defined concepts
        # ----------------------------------------------------

        feature_concepts = FEATURE_CONCEPTS.get(
            pep_number,
            []
        )

        entities.append({
            "id": feature_id,
            "type": "Feature",
            "name": feature_name,
            "concepts": feature_concepts,
            "source_pep": pep_number,
        })

        # ----------------------------------------------------
        # PEP -> FEATURE
        # ----------------------------------------------------

        relationships.append({
            "source": pep_id,
            "type": "PROPOSES",
            "target": feature_id,
        })

    # ========================================================
    # ADD EXPLICIT PEP EVOLUTION RELATIONSHIPS
    # ========================================================

    # Only add the relationship if both PEPs exist in our
    # selected dataset.

    pep_ids = {
        entity["id"]
        for entity in entities
        if entity["type"] == "PEP"
    }

    for relation in PEP_EVOLUTION_RELATIONSHIPS:

        if (
            relation["source"] in pep_ids
            and relation["target"] in pep_ids
        ):

            relationships.append(relation)

    # ========================================================
    # FINAL KNOWLEDGE OBJECT
    # ========================================================

    return {
        "schema_version": "0.2",

        "entities": entities,

        "relationships": relationships,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    knowledge = build_knowledge()

    OUTPUT_FILE.write_text(
        json.dumps(
            knowledge,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Knowledge state written to: "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Entities: "
        f"{len(knowledge['entities'])}"
    )

    print(
        f"Relationships: "
        f"{len(knowledge['relationships'])}"
    )

    # --------------------------------------------------------
    # Print explicit evolution relationships for verification
    # --------------------------------------------------------

    evolution_relationships = [
        r
        for r in knowledge["relationships"]
        if r["type"] == "SPLIT_INTO"
    ]

    print("\nPEP EVOLUTION RELATIONSHIPS:")

    for relationship in evolution_relationships:

        print(
            f"- {relationship['source']} "
            f"--{relationship['type']}--> "
            f"{relationship['target']}"
        )


if __name__ == "__main__":
    main()