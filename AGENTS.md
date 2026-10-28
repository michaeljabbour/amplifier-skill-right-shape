# Working on Right Shape

- Read `skills/right-shape/SKILL.md` and its `references/rubric.md` before changing
  the method. Record any change in CHANGELOG.md.
- The rubric is the single source for scales, gates, checks, engines, dispositions
  and templates. Never copy it into the mode, the recipe or the site content.
- A gate caps the rung. Never let a placement exceed the lowest failed cap, and never
  let composition raise it.
- Never claim results, users, usage, benchmark outcomes or deployment without evidence.
  `docs/BENCHMARK.md` is a plan until a dated record exists under `docs/evaluations/`.
- Examples are fictional and must say so. Do not use real people, real organizations,
  internal product names, credentials or any personal information.
- The site is static Python, HTML, CSS and JavaScript. Keep it free of runtime
  dependencies, external fonts, analytics and backend services.
- The Amplifier bundle is `bundle.md`, `behaviors/`, `modes/` and `recipes/`. Keep the
  mode body short (it is injected every turn) and the method in the skill. Validate the
  recipe with the `recipes` tool after edits.
- Keep only one file named `SKILL.md` in the repository; snapshots use another name.
- `site/site.json` holds fictional placements. The build recomputes every placement from
  the rubric and refuses one that does not follow it.
- Keep the MIT notice in `site/theme/LICENSE`. Do not imply institutional affiliation.
- Voice: verdict first, one question per turn, plain words.
- Use visible labels, keyboard controls and reduced-motion support.
- Run `python3 scripts/build.py`, `python3 scripts/check.py` and
  `node --check site/site.js`. Inspect desktop and phone layouts after UI changes.
- Do not add a remote, push, publish, deploy or contact anyone unless asked.
