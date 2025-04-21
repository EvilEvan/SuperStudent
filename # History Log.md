# History Log

1. Enforced uppercase centre display (“A”) in C/L Case mode.  
2. Kept Greek small alpha “α” only when in standard alphabet mode.  
3. Updated falling‑item rendering and HUD target text for consistency.  
4. Clarified prompt rule to explicitly state centre must remain uppercase.  
5. Added summary of changes and reasons for each update.  
6. Fixed rectangle display in shapes mode by applying a 1.5:1 aspect ratio so it no longer renders as a square. #Creator review - Status: Failed
---
History.mdc

gpto4 mini
1. Replaced unsupported 'ɑ' with Greek alpha 'α' in centre, falling items, and HUD.
2. Added explicit rule: centre display remains uppercase (e.g., 'A') for C/L Case.
3. Clarified prompt wording to include “centre must be uppercase” to avoid ambiguity.
4. Reason: enforce design intent and prevent misinterpretation of capitalization rules.

Neglected notes
---

**Model: gpt-4o | Date: 2024-06-12 | Logic:**  
- Rectangle in "shapes" mode now displays as a border-only rectangle with a 1.5:1 aspect ratio (not a square).  
- All shapes in "shapes" mode are now drawn as outlines (no color fill), both for the center target and falling items.  
- Reason: Ensures visual distinction between rectangle and square, and matches prompt requirement for border-only display.

# Notes

- Centre‑display logic now prioritizes `mode == "clcase"` before any alpha substitution.  
- Greek alpha mapping applies exclusively to alphabet mode to avoid symbol fallbacks.  
- HUD and falling items follow same substitution rules for clarity.  
- Rectangle now uses a 1.5:1 aspect ratio to visually distinguish it from the square; tweak the multiplier as needed for your design.
