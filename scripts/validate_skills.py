#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"


# Required sections for each skill type.
EXECUTION_REQUIRED_HEADINGS = [
    "Purpose",
    "When to Use",
    "When NOT to Use",
    "Inputs Required",
    "Output Format",
    "Procedure",
    "Guardrails",
    "Failure Patterns",
    "Example 1",
    "Example 2",
]

SYSTEM_REQUIRED_HEADINGS = [
    "Purpose",
    "Scope",
    "Inputs / Signals",
    "Core Behavior",
    "Output / Side Effects",
    "Guardrails",
    "Failure Patterns",
    "Example 1",
    "Example 2",
]

# Files every published skill folder must contain.
REQUIRED_SKILL_DIR_FILES = ["SKILL.md", "README.md", "README.ko.md"]

# Agent Skills spec limit for frontmatter description.
MAX_DESCRIPTION_CHARS = 1024

# YAML frontmatter block at the very top of the file.
FRONTMATTER_PAT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Frontmatter fields. The skill type lives under metadata (single source of
# truth); the optional "**Type:**" body line is display-only and must agree.
FM_NAME_PAT = re.compile(r"^name:\s*(\S.*?)\s*$", re.MULTILINE)
FM_DESC_PAT = re.compile(r"^description:\s*(.*)((?:\n[ \t]+\S.*)*)", re.MULTILINE)
FM_TYPE_PAT = re.compile(r"^\s*type:\s*(execution|system)\s*$", re.IGNORECASE | re.MULTILINE)

BODY_TYPE_PAT = re.compile(r"\*\*Type:\*\*\s*(Execution|System)\b", re.IGNORECASE)

# Match markdown headings like: "# Title", "## Purpose", "### 1) Detection"
HEADING_PAT = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def is_template_file(path: Path) -> bool:
    # Ignore templates (they will intentionally have placeholders).
    return "_template" in path.parts


def is_readme_file(path: Path) -> bool:
    return path.name.lower().startswith("readme")


def is_subskill_file(path: Path) -> bool:
    return "subskills" in path.parts


def is_markdown_file(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".markdown"}


def normalize_heading(text: str) -> str:
    # Normalize heading text for matching. Keep it simple and deterministic.
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    # Drop trailing punctuation for robustness.
    t = t.rstrip(":")
    return t


def extract_headings(md: str) -> List[str]:
    headings = []
    for _, title in HEADING_PAT.findall(md):
        headings.append(normalize_heading(title))
    return headings


def find_examples_present(headings: List[str]) -> Tuple[bool, bool]:
    # Accept headings like:
    # "Example 1 (Minimal Context)", "Example 2 (Realistic Scenario)", etc.
    ex1 = any(h.lower().startswith("example 1") for h in headings)
    ex2 = any(h.lower().startswith("example 2") for h in headings)
    return ex1, ex2


def extract_description(fm: str) -> Optional[str]:
    m = FM_DESC_PAT.search(fm)
    if not m:
        return None
    first = m.group(1).strip()
    # Folded/literal block scalar indicators carry no content themselves.
    if first in {">", "|", ">-", "|-", ">+", "|+"}:
        first = ""
    cont = " ".join(line.strip() for line in m.group(2).splitlines() if line.strip())
    return (first + " " + cont).strip()


def validate_skill_file(path: Path) -> List[str]:
    errors: List[str] = []

    md = path.read_text(encoding="utf-8", errors="replace")

    fm_match = FRONTMATTER_PAT.match(md)
    if not fm_match:
        errors.append("Missing YAML frontmatter block (--- ... ---) at the top of the file.")
        return errors
    fm = fm_match.group(1)
    body = md[fm_match.end():]

    # name: required, must match the skill folder name for SKILL.md files.
    name_m = FM_NAME_PAT.search(fm)
    if not name_m:
        errors.append('Missing "name:" in frontmatter.')
    elif path.name == "SKILL.md" and name_m.group(1) != path.parent.name:
        errors.append(
            f'Frontmatter name "{name_m.group(1)}" does not match folder name "{path.parent.name}".'
        )

    # description: required, non-empty, spec length limit.
    desc = extract_description(fm)
    if not desc:
        errors.append('Missing or empty "description:" in frontmatter.')
    elif len(desc) > MAX_DESCRIPTION_CHARS:
        errors.append(
            f"Frontmatter description is {len(desc)} chars; maximum is {MAX_DESCRIPTION_CHARS}."
        )

    # type: required in frontmatter metadata.
    fm_type_m = FM_TYPE_PAT.search(fm)
    if not fm_type_m:
        errors.append(
            'Missing skill type in frontmatter. Add "type: execution" or '
            '"type: system" under metadata.'
        )
        return errors
    skill_type = fm_type_m.group(1).lower()

    # Optional display line in the body must not contradict the frontmatter.
    body_type_m = BODY_TYPE_PAT.search(body)
    if body_type_m and body_type_m.group(1).lower() != skill_type:
        errors.append(
            f'Body "**Type:** {body_type_m.group(1)}" contradicts frontmatter '
            f'"type: {skill_type}".'
        )

    if skill_type == "execution":
        required = EXECUTION_REQUIRED_HEADINGS
    else:
        required = SYSTEM_REQUIRED_HEADINGS

    headings = extract_headings(body)
    headings_lower = [h.lower() for h in headings]

    # Validate required headings
    for req in required:
        req_l = req.lower()
        if req_l in {"example 1", "example 2"}:
            # examples validated separately to allow suffixes
            continue
        if req_l not in headings_lower:
            errors.append(f'Missing required section heading: "{req}"')

    # Validate examples
    ex1, ex2 = find_examples_present(headings)
    if not ex1:
        errors.append(
            'Missing "Example 1" section (heading must start with "Example 1")'
        )
    if not ex2:
        errors.append(
            'Missing "Example 2" section (heading must start with "Example 2")'
        )

    return errors


def validate_skill_dirs() -> List[Tuple[Path, List[str]]]:
    # Every published skill folder must ship its SKILL.md and both READMEs.
    failed: List[Tuple[Path, List[str]]] = []
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        if skill_dir.name == "_template":
            continue
        missing = [
            fname
            for fname in REQUIRED_SKILL_DIR_FILES
            if not (skill_dir / fname).is_file()
        ]
        if missing:
            failed.append((skill_dir, [f"Missing required file(s): {', '.join(missing)}"]))
    return failed


def main() -> int:
    if not SKILLS_DIR.exists():
        print(f"ERROR: skills directory not found at {SKILLS_DIR}")
        return 2

    md_files = [
        p
        for p in SKILLS_DIR.rglob("*")
        if p.is_file()
        and is_markdown_file(p)
        and not is_template_file(p)
        and not is_readme_file(p)
        and not is_subskill_file(p)
    ]

    # Nothing to validate is okay (early stage repo).
    if not md_files:
        print(
            "No skill markdown files found (excluding templates). Nothing to validate."
        )
        return 0

    failed: List[Tuple[Path, List[str]]] = validate_skill_dirs()
    for p in sorted(md_files):
        errs = validate_skill_file(p)
        if errs:
            failed.append((p, errs))

    if failed:
        print("Skill validation failed.\n")
        for path, errs in failed:
            rel = path.relative_to(REPO_ROOT)
            print(f"- {rel}")
            for e in errs:
                print(f"  - {e}")
            print()
        print("Fix the issues above to pass CI.")
        return 1

    print(f"Skill validation passed ({len(md_files)} file(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
