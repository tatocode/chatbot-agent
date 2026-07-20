---
name: calculator
description: Use this skill when you need to calculate the result of a formula.
---

# Calculator Skill

Use this skill whenever a task requires mathematical calculation.

## When to use

* Arithmetic operations (`+`, `-`, `*`, `/`, `%`, `**`)
* Expressions with parentheses
* Numeric calculations that require accurate results

## Input

A mathematical expression as a string.

Examples:

* `1 + 2 * 3`
* `(15 + 8) / 2`
* `2 ** 10`

Then, run the following Python script to get the results:

```bash
python3 scripts/cal.py [MATHEMATICAL_EXPRESSION]
```

## Output

The computed numeric result.

## Notes

* Pass only the mathematical expression.
* Do not explain or rewrite the expression before calling this skill.
* Use this skill instead of performing calculations manually to ensure accuracy.
