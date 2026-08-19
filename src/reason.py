import json
import re
from pathlib import Path


KNOWLEDGE_FILE = Path(
    "data/processed/knowledge_state.json"
)


# ============================================================
# LOAD KNOWLEDGE
# ============================================================

def load_knowledge():
    return json.loads(
        KNOWLEDGE_FILE.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):
    """
    Convert text into a set of meaningful tokens.

    This is deliberately simple and transparent.
    It is part of our own mapping/reasoning logic.
    """

    text = text.lower()

    words = re.findall(
        r"[a-zA-Z_][a-zA-Z0-9_]*",
        text
    )

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "for",
        "with",
        "is",
        "are",
        "be",
        "this",
        "that",
        "new",
        "want",
        "allow",
        "allows",
        "using",
        "use",
        "i",
        "it",
        "on",
        "into",
        "based",
        "its",
        "their",
        "how",
        "make",
        "makes",
        "defining",
    }

    return {
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    }


# ============================================================
# MANUAL CONCEPT MAPPING
# ============================================================

def phrase_matches(text, phrases):
    """
    Detect explicitly defined domain concepts and
    their manually defined aliases.

    These mappings are intentionally authored for
    the Python syntax-evolution domain.
    """

    text = text.lower()

    CONCEPT_ALIASES = {

        # ----------------------------------------------------
        # PEP 572
        # ----------------------------------------------------

        "assignment expression": [
            "assignment expression",
            "assignment inside an expression",
            "assign inside an expression",
            "assignment while evaluating",
            "assign while evaluating",
            "assign a value while evaluating",
            "assigning a value while evaluating",
            "assignment during expression evaluation",
            "new operator that assigns a value while evaluating",
        ],

        "assignment": [
            "assignment",
            "assign a value",
            "assigning a value",
        ],

        "expression": [
            "expression",
            "expressions",
            "inside an expression",
            "within an expression",
        ],

        # ----------------------------------------------------
        # PEP 634 / 635 / 636
        # ----------------------------------------------------

        "pattern matching": [
            "pattern matching",
            "structural pattern matching",
            "structure matching",
            "structural matching",
            "matching the structure",
            "match the structure",
            "matching object structure",
            "match object structure",
            "matching objects",
        ],

        "match statement": [
            "match statement",
            "match syntax",
            "match construct",
        ],

        "case statement": [
            "case statement",
            "case syntax",
            "case construct",
            "selecting a case",
            "select a case",
        ],

        "pattern": [
            "pattern",
            "patterns",
        ],

        # ----------------------------------------------------
        # PEP 695
        # ----------------------------------------------------

        "type parameters": [
            "type parameters",
            "type parameter",
            "generic parameters",
            "parameterized types",
        ],

        "generic": [
            "generic",
            "generics",
            "generic class",
            "generic classes",
            "generic function",
            "generic functions",
        ],

        "type variable": [
            "type variable",
            "type variables",
            "typevar",
            "type vars",
        ],

        "type alias": [
            "type alias",
            "type aliases",
        ],

        "typing": [
            "typing",
            "type system",
            "static typing",
        ],

        # ----------------------------------------------------
        # PEP 484
        # ----------------------------------------------------

        "type hints": [
            "type hints",
            "type hint",
        ],

        "type annotations": [
            "type annotations",
            "type annotation",
            "annotations",
        ],

        # ----------------------------------------------------
        # PEP 612
        # ----------------------------------------------------

        "parameter specification": [
            "parameter specification",
            "parameter specifications",
            "parameter specification variables",
            "paramspec",
            "paramspec variables",
        ],

        # ----------------------------------------------------
        # PEP 646
        # ----------------------------------------------------

        "variadic generics": [
            "variadic generics",
            "variadic generic",
            "variadic type parameters",
            "variable number of type parameters",
            "type parameter tuples",
            "type parameter tuple",
            "type tuples",
        ],
    }

    matches = []

    for concept in phrases:

        concept_lower = concept.lower()

        aliases = CONCEPT_ALIASES.get(
            concept_lower,
            [concept_lower]
        )

        for alias in aliases:

            if alias in text:

                matches.append(
                    concept
                )

                break

    return list(
        dict.fromkeys(matches)
    )


# ============================================================
# FEATURE SCORING
# ============================================================

def calculate_score(
    input_tokens,
    entity,
    matched_phrases=None
):
    """
    Calculate relevance using:

    1. Token overlap
    2. Explicitly mapped domain concepts

    Explicit concept mappings receive stronger weight.
    """

    concepts = entity.get(
        "concepts",
        []
    )

    if not concepts:
        return 0.0

    # --------------------------------------------------------
    # Token overlap
    # --------------------------------------------------------

    matched_concepts = 0

    for concept in concepts:

        concept_tokens = tokenize(
            concept
        )

        if not concept_tokens:
            continue

        if concept_tokens.issubset(
            input_tokens
        ):
            matched_concepts += 1

    token_score = (
        matched_concepts
        / len(concepts)
    )

    # --------------------------------------------------------
    # Explicit concept mapping
    # --------------------------------------------------------

    explicit_matches = 0

    if matched_phrases:
        explicit_matches = len(
            matched_phrases
        )

    explicit_score = min(
        explicit_matches * 0.30,
        0.60
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    return min(
        token_score + explicit_score,
        1.0
    )


# ============================================================
# MATCH CLASSIFICATION
# ============================================================

def classify_match(score):
    """
    Convert the numerical relevance score into
    a human-readable match category.
    """

    if score >= 0.70:
        return "DIRECT"

    if score >= 0.40:
        return "RELATED"

    if score >= 0.20:
        return "WEAK"

    return "NONE"


# ============================================================
# REASONING EXPLANATION
# ============================================================

def build_reasoning(
    match_type,
    matched_concepts,
    feature,
):
    """
    Generate a transparent explanation of why
    a feature was considered relevant.

    This is rule-based reasoning authored for
    the syntax-evolution domain.
    """

    feature_name = feature.get(
        "name",
        "this feature"
    )

    if match_type == "DIRECT":

        if matched_concepts:

            concepts_text = ", ".join(
                matched_concepts
            )

            return (
                f"The proposed syntax directly overlaps "
                f"with the concepts associated with "
                f"{feature_name}. The strongest matching "
                f"concepts are: {concepts_text}."
            )

        return (
            f"The proposed syntax has a strong conceptual "
            f"overlap with {feature_name}."
        )

    if match_type == "RELATED":

        if matched_concepts:

            concepts_text = ", ".join(
                matched_concepts
            )

            return (
                f"The proposal is related to {feature_name} "
                f"because it shares broader concepts with "
                f"the feature. The matched concepts are: "
                f"{concepts_text}."
            )

        return (
            f"The proposal has a partial conceptual "
            f"relationship with {feature_name}."
        )

    if match_type == "WEAK":

        return (
            f"The proposal has a weak conceptual overlap "
            f"with {feature_name}. The relationship should "
            f"be treated as possible prior art rather than "
            f"a direct match."
        )

    return (
        "No meaningful conceptual relationship was found."
    )


# ============================================================
# FIND RELATED FEATURES
# ============================================================

def find_related_features(
    user_input,
    knowledge,
    limit=5,
):
    """
    Find Features relevant to the new user input.
    """

    input_tokens = tokenize(
        user_input
    )

    candidates = []

    for entity in knowledge["entities"]:

        if entity["type"] != "Feature":
            continue

        concepts = entity.get(
            "concepts",
            []
        )

        matched_phrases = phrase_matches(
            user_input,
            concepts
        )

        score = calculate_score(
            input_tokens,
            entity,
            matched_phrases
        )

        if score <= 0:
            continue

        match_type = classify_match(
            score
        )

        candidates.append({

            "score": min(
                score,
                1.0
            ),

            "entity": entity,

            "matched_concepts":
                matched_phrases,

            "match_type":
                match_type,
        })

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return candidates[:limit]


# ============================================================
# GRAPH TRAVERSAL
# ============================================================

def get_connected_entities(
    source_id,
    relationship_types,
    knowledge,
):
    """
    Traverse outgoing relationships starting from
    a particular entity.
    """

    connected = []

    for relationship in knowledge[
        "relationships"
    ]:

        if (
            relationship["source"]
            == source_id
            and relationship["type"]
            in relationship_types
        ):

            target_id = relationship[
                "target"
            ]

            for entity in knowledge[
                "entities"
            ]:

                if entity["id"] == target_id:

                    connected.append(
                        entity
                    )

    return connected


# ============================================================
# REVERSE GRAPH TRAVERSAL
# ============================================================

def get_incoming_entities(
    target_id,
    relationship_types,
    knowledge,
):
    """
    Find entities that point TO the given entity.
    """

    connected = []

    for relationship in knowledge[
        "relationships"
    ]:

        if (
            relationship["target"]
            == target_id
            and relationship["type"]
            in relationship_types
        ):

            source_id = relationship[
                "source"
            ]

            for entity in knowledge[
                "entities"
            ]:

                if entity["id"] == source_id:

                    connected.append(
                        entity
                    )

    return connected


# ============================================================
# FIND PEP
# ============================================================

def find_pep(
    pep_number,
    knowledge
):
    """
    Find the PEP entity associated with a Feature.
    """

    pep_id = f"pep_{pep_number}"

    for entity in knowledge[
        "entities"
    ]:

        if entity["id"] == pep_id:

            return entity

    return None


# ============================================================
# FIND ENTITY BY ID
# ============================================================

def find_entity(
    entity_id,
    knowledge
):
    """
    Find an entity by its ID.
    """

    for entity in knowledge[
        "entities"
    ]:

        if entity["id"] == entity_id:

            return entity

    return None


# ============================================================
# BUILD HISTORICAL CONTEXT
# ============================================================

def get_historical_context(
    pep,
    knowledge
):
    """
    Build historical context around a PEP.
    """

    historical_parent_peps = get_incoming_entities(
        pep["id"],
        {"SPLIT_INTO"},
        knowledge
    )

    historical_child_peps = get_connected_entities(
        pep["id"],
        {"SPLIT_INTO"},
        knowledge
    )

    related_historical_peps = []

    # --------------------------------------------------------
    # Direct parent PEPs
    # --------------------------------------------------------

    for parent in historical_parent_peps:

        if parent["id"] != pep["id"]:

            related_historical_peps.append({
                "relationship": "SPLIT_FROM",
                "pep": parent,
            })

    # --------------------------------------------------------
    # Sibling PEPs
    # --------------------------------------------------------

    for parent in historical_parent_peps:

        siblings = get_connected_entities(
            parent["id"],
            {"SPLIT_INTO"},
            knowledge
        )

        for sibling in siblings:

            if sibling["id"] == pep["id"]:
                continue

            already_present = any(
                item["pep"]["id"]
                == sibling["id"]
                for item in related_historical_peps
            )

            if not already_present:

                related_historical_peps.append({
                    "relationship": "SAME_ORIGIN",
                    "pep": sibling,
                })

    # --------------------------------------------------------
    # Direct child PEPs
    # --------------------------------------------------------

    for child in historical_child_peps:

        if child["id"] == pep["id"]:
            continue

        already_present = any(
            item["pep"]["id"]
            == child["id"]
            for item in related_historical_peps
        )

        if not already_present:

            related_historical_peps.append({
                "relationship": "SPLIT_INTO",
                "pep": child,
            })

    return related_historical_peps


# ============================================================
# REASON OVER NEW INPUT
# ============================================================

def reason(user_input):

    knowledge = load_knowledge()

    related_features = find_related_features(
        user_input,
        knowledge
    )

    results = []

    for candidate in related_features:

        score = candidate[
            "score"
        ]

        feature = candidate[
            "entity"
        ]

        matched_concepts = candidate[
            "matched_concepts"
        ]

        match_type = candidate[
            "match_type"
        ]

        pep_number = feature[
            "source_pep"
        ]

        pep = find_pep(
            pep_number,
            knowledge
        )

        if not pep:
            continue

        # ----------------------------------------------------
        # Graph traversal
        # ----------------------------------------------------

        alternatives = get_connected_entities(
            pep["id"],
            {"CONSIDERS"},
            knowledge,
        )

        objections = get_connected_entities(
            pep["id"],
            {"RAISES"},
            knowledge,
        )

        examples = get_connected_entities(
            pep["id"],
            {"ILLUSTRATES"},
            knowledge,
        )

        # ----------------------------------------------------
        # Historical context
        # ----------------------------------------------------

        historical_context = get_historical_context(
            pep,
            knowledge
        )

        # ----------------------------------------------------
        # Reasoning explanation
        # ----------------------------------------------------

        reasoning = build_reasoning(
            match_type,
            matched_concepts,
            feature,
        )

        results.append({

            "pep": pep,

            "feature": feature,

            "similarity": round(
                score,
                3
            ),

            "match_type":
                match_type,

            "matched_concepts":
                matched_concepts,

            "reasoning":
                reasoning,

            "alternatives":
                alternatives,

            "objections":
                objections,

            "examples":
                examples,

            "historical_context":
                historical_context,
        })

    return results


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(user_input):

    results = reason(
        user_input
    )

    print("\nNEW INPUT")
    print("--------")

    print(user_input)

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not results:

        print(
            "\nNo closely related "
            "feature was found."
        )

        return

    # --------------------------------------------------------
    # Prior art
    # --------------------------------------------------------

    print(
        "\nRELATED PRIOR ART"
    )

    print(
        "-----------------"
    )

    for result in results:

        pep = result[
            "pep"
        ]

        feature = result[
            "feature"
        ]

        print()

        print(
            f"PEP {pep['number']}: "
            f"{pep['title']}"
        )

        print(
            f"Feature: "
            f"{feature.get('name', '')}"
        )

        print(
            f"Relevance score: "
            f"{result['similarity']}"
        )

        print(
            f"Match type: "
            f"{result['match_type']}"
        )

        # ----------------------------------------------------
        # Matched concepts
        # ----------------------------------------------------

        matched = result[
            "matched_concepts"
        ]

        if matched:

            print(
                "\nMatched concepts:"
            )

            for concept in matched:

                print(
                    f"- {concept}"
                )

        # ----------------------------------------------------
        # Reasoning
        # ----------------------------------------------------

        reasoning = result.get(
            "reasoning"
        )

        if reasoning:

            print(
                "\nREASONING"
            )

            print(
                "---------"
            )

            print(
                reasoning
            )

        # ----------------------------------------------------
        # Alternatives
        # ----------------------------------------------------

        alternatives = result[
            "alternatives"
        ]

        if alternatives:

            print(
                "\nAlternatives considered:"
            )

            for alternative in alternatives:

                print(
                    f"- "
                    f"{alternative.get('name', alternative.get('description', ''))}"
                )

        # ----------------------------------------------------
        # Objections
        # ----------------------------------------------------

        objections = result[
            "objections"
        ]

        if objections:

            print(
                "\nObjections:"
            )

            for objection in objections:

                print(
                    f"- "
                    f"{objection.get('name', objection.get('description', ''))}"
                )

        # ----------------------------------------------------
        # Examples
        # ----------------------------------------------------

        examples = result[
            "examples"
        ]

        if examples:

            print(
                "\nExamples:"
            )

            for example in examples:

                print(
                    f"- "
                    f"{example.get('name', example.get('description', ''))}"
                )

        # ----------------------------------------------------
        # Historical PEP context
        # ----------------------------------------------------

        historical_context = result[
            "historical_context"
        ]

        if historical_context:

            print(
                "\nHistorical context:"
            )

            for item in historical_context:

                related_pep = item[
                    "pep"
                ]

                relationship = item[
                    "relationship"
                ]

                if relationship == "SPLIT_FROM":

                    print(
                        f"- PEP "
                        f"{related_pep['number']} "
                        f"was the earlier proposal "
                        f"from which this PEP was split."
                    )

                elif relationship == "SAME_ORIGIN":

                    print(
                        f"- PEP "
                        f"{related_pep['number']} "
                        f"shares the same historical "
                        f"origin."
                    )

                elif relationship == "SPLIT_INTO":

                    print(
                        f"- This PEP was later split "
                        f"into PEP "
                        f"{related_pep['number']}."
                    )


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":

    user_input = input(
        "\nDescribe your proposed "
        "Python syntax:\n> "
    )

    print_results(
        user_input
    )