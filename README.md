 HEAD
# Python Syntax Knowledge Graph

A knowledge-based reasoning system for analyzing proposed Python syntax
and identifying related prior Python Enhancement Proposals (PEPs).

## Overview

This project builds a structured knowledge graph from selected Python
PEPs and uses rule-based reasoning to compare a new syntax proposal
against existing Python language proposals.

The system can identify:

- Related Python Enhancement Proposals
- Matching language concepts
- Alternatives considered by previous proposals
- Objections raised during proposal discussions
- Examples associated with previous proposals
- Historical relationships between PEPs
- Direct, related, and weak matches

## Architecture

The project follows a simple pipeline:

PEP Dataset
    ↓
PEP Collection
    ↓
PEP Parsing
    ↓
Knowledge Graph Construction
    ↓
Concept Mapping
    ↓
Reasoning Engine
    ↓
Prior-Art Analysis

## Main Components

### `src/dataset.py`

Contains the selected PEP dataset and manually defined concept mappings.

### `src/collect_peps.py`

Collects PEP source documents.

### `src/parse_pep.py`

Parses individual PEP documents and extracts structured information.

### `src/build_knowledge.py`

Builds the knowledge graph containing entities and relationships.

### `src/reason.py`

Accepts a proposed Python syntax and searches the knowledge graph
for relevant prior art.

The reasoning engine uses:

- Token matching
- Manually defined concept aliases
- Relevance scoring
- Match classification
- Graph traversal
- Historical relationship traversal
- Rule-based reasoning explanations

## Match Classification

The reasoning system classifies matches using relevance scores:

| Score | Classification |
|-------|----------------|
| ≥ 0.70 | DIRECT |
| ≥ 0.40 | RELATED |
| ≥ 0.20 | WEAK |
| < 0.20 | NONE |

## Example

Input:

> I want to introduce syntax that allows assignment inside an expression.

Output:

```text
PEP 572: PEP 572 – Assignment Expressions
Feature: Assignment Expressions
Relevance score: 1.0
Match type: DIRECT

# python-syntax-knowledge
origin/main
