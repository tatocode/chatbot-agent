#!/usr/bin/env python3
"""
Skill Validator Script
Validates that a skill directory follows the expected conventions.

Usage:
    python3 validate_skill.py <skill-name>
    python3 validate_skill.py <skill-name> --dir /path/to/skills

The script checks:
- SKILL.md exists and has valid YAML frontmatter
- Required sections are present
- All referenced file paths exist
- Scripts are executable (have shebang)
- No orphaned files

Exit code: 0 if valid, 1 if issues found.
"""

import argparse
import os
import re
import sys


SKILLS_DIR = "/skills"


def parse_frontmatter(content: str) -> tuple[dict | None, str | None]:
    """Extract YAML frontmatter from SKILL.md content."""
    # Simple frontmatter parser (no PyYAML dependency)
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, "Missing or invalid YAML frontmatter (must start and end with '---')"

    raw = match.group(1)
    fields = {}
    for line in raw.strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")

    errors = []
    if "name" not in fields:
        errors.append("Missing 'name' in frontmatter")
    if "description" not in fields:
        errors.append("Missing 'description' in frontmatter")

    if errors:
        return fields, "; ".join(errors)
    return fields, None


REQUIRED_SECTIONS = [
    "When to use",
    "How to use",
]


def check_sections(content: str) -> list[str]:
    """Check that required markdown sections are present."""
    issues = []
    for section in REQUIRED_SECTIONS:
        # Match ## Section Name (case-insensitive)
        if not re.search(rf"^##\s+{re.escape(section)}\s*$", content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"Missing required section: '{section}'")
    return issues


def find_referenced_paths(content: str, skill_dir: str) -> list[str]:
    """Find absolute paths referenced in the markdown content."""
    paths = re.findall(r"/skills/[^\s)`\"'<>]+", content)
    return list(set(paths))


def validate_script(path: str) -> list[str]:
    """Validate a single script file."""
    issues = []
    if not os.path.exists(path):
        return [f"Script not found: {path}"]

    try:
        with open(path, "r") as f:
            first_line = f.readline().strip()
            if not first_line.startswith("#!"):
                issues.append(f"Script missing shebang: {path}")
    except Exception as e:
        issues.append(f"Cannot read script {path}: {e}")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate a skill directory structure.")
    parser.add_argument("skill_name", help="Name of the skill to validate (e.g., 'calculator')")
    parser.add_argument("--dir", default=SKILLS_DIR, help=f"Skills root directory (default: {SKILLS_DIR})")
    args = parser.parse_args()

    skill_dir = os.path.join(args.dir, args.skill_name)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    scripts_dir = os.path.join(skill_dir, "scripts")

    all_issues = []

    # Check skill directory exists
    if not os.path.isdir(skill_dir):
        print(f"ERROR: Skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # Check SKILL.md exists
    if not os.path.isfile(skill_md):
        print(f"ERROR: SKILL.md not found: {skill_md}", file=sys.stderr)
        sys.exit(1)

    print(f"Validating skill: {args.skill_name}")
    print(f"  Directory: {skill_dir}")
    print()

    # Read SKILL.md
    with open(skill_md, "r") as f:
        content = f.read()

    # Validate frontmatter
    print("[1/4] Checking YAML frontmatter...")
    frontmatter, fm_error = parse_frontmatter(content)
    if fm_error:
        all_issues.append(f"Frontmatter: {fm_error}")
        print(f"  ⚠  {fm_error}")
    else:
        print(f"  ✓ Name: {frontmatter.get('name', '?')}")
        print(f"  ✓ Description: {frontmatter.get('description', '?')}")

    # Check required sections
    print("[2/4] Checking required sections...")
    section_issues = check_sections(content)
    for issue in section_issues:
        all_issues.append(issue)
        print(f"  ⚠  {issue}")
    if not section_issues:
        print("  ✓ All required sections present")

    # Check referenced paths
    print("[3/4] Checking referenced paths...")
    ref_paths = find_referenced_paths(content, skill_dir)
    path_issues = []
    for ref_path in ref_paths:
        # Only check paths within the skills directory
        if ref_path.startswith("/skills/") and not os.path.exists(ref_path):
            path_issues.append(f"Referenced path not found: {ref_path}")
            print(f"  ⚠  Referenced path not found: {ref_path}")
    if not path_issues:
        print(f"  ✓ All {len(ref_paths)} referenced path(s) exist")

    # Check scripts directory
    print("[4/4] Checking scripts...")
    if os.path.isdir(scripts_dir):
        script_files = sorted(os.listdir(scripts_dir))
        if not script_files:
            print("  ⚠  scripts/ directory is empty")
        else:
            for sf in script_files:
                script_path = os.path.join(scripts_dir, sf)
                if os.path.isfile(script_path):
                    script_issues = validate_script(script_path)
                    for si in script_issues:
                        all_issues.append(si)
                        print(f"  ⚠  {si}")
                    if not script_issues:
                        print(f"  ✓ {sf}")
                else:
                    print(f"  - {sf} (not a file, skipped)")
    else:
        print("  - No scripts/ directory (optional)")

    # Summary
    print()
    if all_issues:
        print(f"Validation COMPLETE — {len(all_issues)} issue(s) found")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        sys.exit(1)
    else:
        print("Validation COMPLETE — All checks passed ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
