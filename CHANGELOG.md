# Changelog

## 0.1.1 (2026-10-28)

- Open the site and README with what the skill is for, in plain words, and a three-step "how it works".
- Add "Three choices, kept separate": shape, freedom and engine, each with plain options, plus the five shapes side by side with an everyday comparison, when to pick each, an example and who is in charge.
- Add a short glossary to the site and README.
- Accessibility: fix low-contrast text on tinted panels, put the top strip inside a landmark, and make every horizontally scrolling table, ladder and code block reachable and labeled for keyboard users. An axe audit (WCAG 2 A and AA, plus best practices) reports no violations on desktop or phone.

## 0.1.0 (2026-10-28)

- Add the `right-shape` skill with three modes: Place one job, Audit a set of repositories, and Check one capability against the contract.
- Add `references/rubric.md`: sorting questions, shapes, need dimensions, the autonomy ladder, six gates, four shape checks, engines (LLM, decision model, both), replaceability checks, the evaluation ladder, the capability contract, dispositions, a diagnosis table, card templates and voice examples.
- Package the repository as the `right-shape` Amplifier bundle with the `/shape` mode and the staged `right-shape-audit` recipe.
- Add fictional worked examples and the benchmark plan. The benchmark has not been run.
- Add a static explanatory site with an interactive placement calculator that reads its numbers from the rubric, and a checked GitHub Pages workflow.
