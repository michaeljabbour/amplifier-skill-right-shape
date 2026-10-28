# Right Shape

[Open the guide and get the skill](https://michaeljabbour.github.io/amplifier-skill-right-shape/).

A placement and audit skill for AI work. It decides what shape a job should take (a tool, a Smart Tool, a skill, an agent or a harness), how much autonomy it can safely have, which engine it needs (an LLM, a decision model, or both), and how anyone would know it works. It can also audit a set of repositories into capabilities that are self-contained, easy to install and measurable. It does not build the capability, and it never grants more autonomy than the gates allow.

**Need** is how much agency the job wants: how open its path is, how much context it carries, how long it runs unattended, and whether it acts on its own. **The ceiling** is how much agency can safely be granted, set by six gates: verifiability, reversibility, the lethal trifecta, isolation, budget and ownership. The placement is whichever is lower. Composition is a separate question: one worker, or a system of workers behind one face.

This project pairs the [`right-shape` skill](skills/right-shape/SKILL.md) and its [rubric](skills/right-shape/references/rubric.md) with an explanatory static website that includes a placement calculator. The [benchmark plan](docs/BENCHMARK.md) sets the bar the skill has to clear; it has not been run yet.

## Use the skill

Give an agent the skill and the work: a job description, an idea, one repository, or a list of repositories. Say which mode you want, or let it choose. Expect a verdict in the first sentence, one question at most, and a card or report at the end.

If your tool supports reusable skills, copy the `skills/right-shape/` directory (`SKILL.md` plus `references/rubric.md`) according to that tool's instructions. Keep the relative `references/` path intact.

### In Amplifier

This repository is also an Amplifier bundle (`right-shape`). Add its behavior to your current host:

```bash
amplifier bundle add "git+https://github.com/michaeljabbour/amplifier-skill-right-shape@main#subdirectory=behaviors/right-shape.yaml" --app
```

For a local checkout that stays in step with your edits, use `file:///<path-to-checkout>/behaviors/right-shape.yaml` instead. Remove with `amplifier bundle remove right-shape-behavior --app`. Start a new session, then:

- **Skill:** `/right-shape`, or ask for it by name. Nothing loads until it is used.
- **Mode:** `/shape` sets a reviewing posture for the session: verdict first, gates before ambition, and every file edit asks you first. `/mode off` leaves it.
- **Recipe:** `@right-shape:recipes/right-shape-audit.yaml` runs one bounded audit that pauses for you after the inventory and again after the placements, then writes a report to `.right-shape/` in your working directory. It never edits anything in scope.

The skill is registered through `tool-skills`. If no other bundle in your host configures skill sources, Amplifier stops scanning its default skill directories (`.amplifier/skills` in the workspace and `~/.amplifier/skills`); add them to your own skills configuration if you need them. Don't also keep a hand-copied `right-shape` in `~/.amplifier/skills`, or two copies will compete.

Example requests:

> Use right-shape on this idea: an agent that watches our support inbox and refunds orders under fifty dollars. Place it.

> Use right-shape to audit the repositories in repos.txt. Follow the layout of our newest skill repository. Ask me before deciding anything about forks.

> Use right-shape to check this Smart Tool against the contract. What stops a stranger installing it?

See [worked examples](docs/EXAMPLES.md): three placements and one audit, all fictional.

## How it works

1. **Sort.** Where does the expertise live, who starts it, how much of the loop a person holds, and whether it is one worker or many.
2. **Score the need.** Four dimensions from 0 to 3 map to a rung on a ten-rung ladder, from a single call to a swarm.
3. **Set the ceiling.** Six gates. Each failure caps the rung. The placement is the lower of need and ceiling, and the skill says what would raise the ceiling honestly.
4. **Choose the shape and engine.** Four composition checks decide between a single worker and an outer harness behind an agent interface. The engine is LLM, decision model, or both.
5. **Check replaceability.** Five checks, from a stable contract to a sunset test that shows when scaffolding has become dead weight.
6. **Write a benchmark that can fail.** A planted trap, a case to leave alone, a stopping test, a consistency test and a control.

## Local development

The site follows the family's small Python static-builder approach: HTML, CSS and JavaScript with no backend or runtime dependencies. Use Python 3.11 or later; no package installation is required.

From the project directory:

```sh
python3 scripts/build.py
python3 scripts/check.py
node --check site/site.js   # optional JavaScript syntax check; needs Node.js
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open <http://127.0.0.1:8000> in your browser. Stop the server with `Ctrl+C`. Re-run the build after source changes. `_site/` is generated output.

The build reads the ladder, need dimensions, gates, shape checks, engines, replaceability checks, evaluation ladder and dispositions straight from the rubric, and the benchmark rows from `docs/BENCHMARK.md`, so the page never forks the method. It also recomputes every fictional placement in `site/site.json` from the rubric and refuses one that does not follow it. The check verifies local links and fragments, that the page and downloads match the canonical skill byte for byte, and the ZIP contents. See [site details](site/README.md).

The Pages workflow builds and checks `_site/` on pushes to `main`, then publishes only that static output. It uses GitHub's official actions pinned to fixed commits and needs no project secrets.

## Project contents

- `skills/right-shape/SKILL.md`: the method.
- `skills/right-shape/references/rubric.md`: the scales, gates, checks, engines, contract, dispositions, diagnosis table, card templates and voice.
- `bundle.md`, `behaviors/right-shape.yaml`: the Amplifier bundle and its installable behavior.
- `modes/shape.md`: the `/shape` mode.
- `recipes/right-shape-audit.yaml`: one staged, human-gated audit.
- `docs/EXAMPLES.md`: fictional worked placements and a fictional audit.
- `docs/BENCHMARK.md`: the tests the skill has to pass. Not yet run.
- `scripts/build.py`, `scripts/check.py`: dependency-free build and integrity checks.
- `site/`: page template, metadata, styles, local assets and interaction code.
- `_site/`: generated website and downloadable skill assets.

## Background

The method draws on public work: Anthropic's *Building effective agents* (workflows versus agents), Feng, McDonald and Zhang's *Levels of Autonomy for AI Agents* (autonomy as a design decision separate from capability), Simon Willison's *lethal trifecta*, Anthropic's *Scaling Managed Agents* (stable interfaces, and scaffolding that becomes dead weight), and Rich Sutton's *The Bitter Lesson*.

## Limits

This is a structured judgment aid, not a security review, a compliance process or a guarantee. Rung thresholds and gate caps are design choices to argue with, and two careful reviewers may place the same job a rung apart. An audit sees only what it can read; private repositories and anything nothing links to may be missing. The examples on the site and in the docs are invented.

## License and provenance

MIT; see [LICENSE](LICENSE). The family theme snapshot keeps its own [MIT notice](site/theme/LICENSE). The page follows the Amplifier Smart Tools family site as a design and implementation reference.
