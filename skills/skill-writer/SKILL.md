---
name: skill-writer
description: Use this skill when you need to create a new skill that packages a reusable capability or workflow for the AI agent.
---

# Skill-Writer Skill

A **meta-skill** that enables you to create, validate, and maintain other skills in the skills library. This skill codifies the conventions, patterns, and workflow for generating new skills so they are consistent with the existing library.

## When to use

- The user **explicitly asks** you to create a new skill (e.g., "create a skill for summarizing PDFs")
- The user describes a repetitive workflow that would benefit from being packaged as a skill
- The user wants to encapsulate a capability with clear input/output conventions
- You need to add a reusable helper script that follows the system's skill conventions
- You are extending or refactoring the skills library

## How the skill library works

Every skill lives under `/skills/<skill-name>/` and follows this structure:

```
/skills/<skill-name>/
├── SKILL.md          # Required — documentation and workflow instructions
└── scripts/          # Optional — helper executables
    └── <script>.py   # Python, shell, or other scripts
```

The `/skills/` directory is a **virtual mount** — use `write_file` / `read_file` (not shell commands) to create and edit files there.

## Step-by-step workflow

### Step 1: Understand the user's request

Clarify these points before designing (ask the user only if unclear):

| Question | Purpose |
|---|---|
| What capability should the skill provide? | Defines the skill's purpose |
| What is a good short name? | Convention: lowercase, hyphen-separated (e.g., `stock-price`, `pdf-summarizer`) |
| What inputs does the skill take? | Defines the interface |
| What output should it produce? | Defines success criteria |
| Does it need a helper script? | Complex logic → script; pure documentation → SKILL.md only |
| Any constraints or edge cases? | Guides "Notes/Limitations" section |

If the user gives enough detail, skip clarifying and move to Step 2.

### Step 2: Study existing skills for conventions

Always read at least one existing skill to match current conventions:

```
read_file("/skills/<existing-skill>/SKILL.md", limit=1000)
```

Pay attention to:
- **YAML frontmatter** format (`name`, `description`)
- **Section headings** and their order
- **Tone** — concise, direct, no unnecessary praise
- **Script integration** — how scripts are referenced with absolute paths
- **Examples** — how usage examples are formatted

### Step 3: Design the skill

Plan before writing:

1. **SKILL.md structure** — documentation, workflow steps, examples
2. **Scripts** — what language (prefer Python), CLI interface, error handling
3. **Directory layout** — what files go where

The skill should be **self-contained**: someone unfamiliar should be able to use it by following the instructions in SKILL.md.

### Step 4: Create the skill

1. **Create the directory** (write_file creates intermediate dirs automatically)
2. **Write SKILL.md** following the template below
3. **Create `scripts/`** and write any helper scripts
4. **Ensure all paths are absolute** (`/skills/<skill-name>/scripts/<script>.py`)

#### SKILL.md Template

```markdown
---
name: <skill-name>
description: <one-line description — when to use this skill>
---

# <Skill Name>

<2-3 sentence overview of the skill, its purpose, and value>

## When to use

- <Scenario 1>
- <Scenario 2>
- <Scenario 3>

## How to use

### Step 1: <First step>

<Instructions for the first step>

### Step 2: <Second step>

<Instructions for the second step>

### Step 3: <Output / result>

<What to do with the result>

## Input

<What input the skill expects>

## Output

<What output the skill produces>

## Error handling

<Common errors and how to handle them>

## Limitations

<Edge cases, constraints, things the skill doesn't handle>

## Examples

### Example 1: <Short description>

```<language>
<code example>
</code>
```

### Example 2: <Short description>

<Another practical example>
```

#### Script Template (Python)

```python
#!/usr/bin/env python3
"""
<Script purpose and usage>
Usage: python3 <script>.py <args>
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="<description>")
    parser.add_argument("<arg>", help="<help text>")
    args = parser.parse_args()

    try:
        # Main logic here
        result = ...
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 5: Verify the skill

After writing all files, verify:

- [ ] **SKILL.md** — read it back and check:
  - [ ] YAML frontmatter is valid
  - [ ] All section headings are consistent with conventions
  - [ ] All referenced file paths use absolute paths (`/skills/...`)
  - [ ] Instructions are clear, actionable, and self-contained
  - [ ] Examples compile / make sense
  - [ ] No contradictory or outdated content
- [ ] **Scripts** — if any:
  - [ ] Script exists at the path referenced in SKILL.md
  - [ ] Script has a shebang (`#!/usr/bin/env python3`)
  - [ ] Script handles errors gracefully (prints to stderr, exits non-zero)
  - [ ] Script works with a quick smoke test: `python3 <script-path> <test-input>`
- [ ] **Conventions** — the new skill matches the style of existing skills

## Skill design principles

1. **One capability per skill** — don't combine unrelated tasks in one skill
2. **Minimal dependencies** — prefer Python stdlib; add `requirements.txt` if external packages are necessary
3. **Self-documenting** — SKILL.md should be enough to use the skill without reading external docs
4. **Fail clearly** — scripts should print meaningful error messages to stderr
5. **Composable** — skills should work well when chained or used in parallel (via `task` tool)

## Limitations of this meta-skill

- This skill documents the **pattern** for creating skills but still requires the AI to do the actual writing — it's not an autonomous code generator
- The `/skills/` mount is virtual; you cannot use `execute` (shell) to write files there, only `write_file`
- This skill cannot modify the system prompt or the skill loading mechanism — it only creates skill content

## Examples

### Example 1: Creating a simple documentation-only skill

User: "Create a skill that teaches the AI how to write good commit messages"

1. Clarify: skill name `commit-message-guide`, no script needed
2. Study: read calculator's SKILL.md for format reference
3. Design: pure documentation skill with commit message conventions
4. Create: `write_file("/skills/commit-message-guide/SKILL.md", ...)`
5. Verify: read back the file and check structure

### Example 2: Creating a skill with a helper script

User: "Create a skill that converts temperatures between Celsius and Fahrenheit"

1. Clarify: name `temperature-converter`, takes a value and unit, outputs converted value
2. Study: read web-downloader skill for script integration pattern
3. Design: SKILL.md + Python script that parses CLI args
4. Create:
   - `write_file("/skills/temperature-converter/SKILL.md", ...)`
   - `write_file("/skills/temperature-converter/scripts/convert.py", ...)`
5. Verify: run `python3 /skills/temperature-converter/scripts/convert.py 32F` and confirm output
