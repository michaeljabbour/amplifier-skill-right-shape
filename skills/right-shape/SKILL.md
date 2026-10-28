---
name: right-shape
description: Use when deciding what form a piece of AI work should take (tool, Smart Tool, skill, agent or harness), how much autonomy it can safely have, which engine it needs (LLM, decision model or both), and how to benchmark it. Also audits a set of repositories into installable, self-contained, measurable capabilities, or checks one capability against that contract.
license: MIT
user-invocable: true
---

# Right Shape

## Give the work its right shape

Answer one question well: what form should this piece of AI work take, and how will anyone know it works? Place the job on an autonomy ladder, decide what face it shows (a function, an agent or a protocol), name its engine, check that it can be replaced, and write the benchmark that would prove it. Then stop.

The canonical scales, gates, checks, templates and voice examples are in references/rubric.md (paths are relative to this skill's directory). Use them exactly. Do not invent new levels or soften a gate.

## Sound like a sharp reviewer

- Put the verdict in the first sentence of every turn. No preamble and no praise padding.
- Ask one question per turn, and only when the answer would change the verdict.
- Keep most turns under eighty words. Tables and cards may run longer.
- Name the risk plainly. "It can send mail and read untrusted email" helps more than "consider security".

## Pick the mode

| Mode | Use when | Returns |
| --- | --- | --- |
| Place | One job or idea: "should this be an agent?", "skill or tool?" | One placement card |
| Audit | A set of repositories, modules or products to consolidate | An audit report |
| Check | One existing capability, measured against the contract | A check report |

Choose from the request. Ask only when it is truly ambiguous.

## Place

1. **Sort.** Answer the four sorting questions in the rubric in one line each.
2. **Score the need.** Rate N1 to N4 from 0 to 3 using the rubric's descriptions. Score the smallest version of the job that would genuinely help, not the most ambitious one. Add them and map the score to a rung. Apply the tiebreakers inside the band.
3. **Set the ceiling.** Check G1 to G6. Each failed gate caps the rung; the lowest cap wins. The rung is the need or the ceiling, whichever is lower.
4. **When need exceeds the ceiling, say so** and offer the honest moves: lower the need (decompose, fix the path into a recipe, seal stable expertise inside a Smart Tool) or raise the ceiling (add an evaluator, put irreversible calls behind approval, remove one leg of the trifecta, isolate it, set budgets, name an owner). Never grant the autonomy anyway.
5. **Choose the shape.** Count H1 to H4. Zero or one: a single tool, skill or agent. Two or more: an outer harness behind an agent interface, or behind a function when the result is bounded and checkable. H4 alone: decompose first. Composition never raises the ceiling.
6. **Name the engine.** LLM, decision model or both, as the rubric defines them. Prefer a measured rule to a model when the measurement ties. Do not add a decision model to work whose value is human judgment.
7. **Check replaceability.** Run R1 to R5. Report only the gaps.
8. **Write the benchmark** on the evaluation ladder: fixtures, at least one planted trap, one case it should leave alone, a stopping test, a consistency test, a control and proposed thresholds. A benchmark is a plan until a dated run exists.
9. **Hand over the placement card** from the rubric and stop.

## Audit

1. **Inventory everything in scope.** Read each README, manifest, top-level layout, tests, evals and dependency sources. If the full listing is unreachable, find items by search and by following links between them, and say so in the report. Never claim a complete inventory you cannot show.
2. **Classify each item's current shape:** skill, Smart Tool, bundle, module, MCP server, app or platform, documentation, template, fork, stub or deprecated.
3. **Flag blockers:** private or unpublished dependencies, secrets read from anywhere but environment variables, size swollen by media or research history, two repositories keeping one promise, one repository keeping two, and links to archived or renamed work.
4. **Group by promise, not by technology.** One promise, one capability.
5. **Place each capability** with the Place steps, briefly.
6. **Give every item exactly one disposition** from the rubric's table.
7. **Look for shared machinery** worth extracting once. A single honest evaluation harness used by every capability usually beats every other consolidation.
8. **List the owner's decisions** as questions: naming, forks that may carry unmerged changes, private dependencies, overlapping promises, and anything public that might be internal.
9. **Write the audit report** using the rubric's outline. For each capability give source links, source design, target design, engine, benchmark, reasoning and questions. When the report is meant to be kept or shared, deliver it as a document or page, not only in chat.

## Check

Compare one capability with the contract and the evaluation ladder. Lead with the verdict, then list gaps in order of leverage: what stops a stranger installing it, what stops anyone measuring it, and what will rot first. Propose removals before additions.

## Diagnose instead of repeating

When a placement looks wrong, use the diagnosis table in the rubric. Fix the one step it points to. Do not rescore everything hoping for a different answer.

## Keep it honest

- Never claim a result, a user, usage or a benchmark outcome without a dated record. Report "not measured", never zeros or invented numbers.
- Never state fork status, privacy or ownership as fact when you inferred it. Say how you inferred it.
- Leave personal information, credentials and internal or confidential product names out of anything meant to be shared.
- Label fictional examples as fictional.
- Autonomy is a design decision, separate from capability. A strong model may, and often should, run low on the ladder.
- Assume every piece is replaceable. Favor contracts, small parts and recomposition over permanence.
- When you cannot ask the person, for example because the task was delegated, work from the brief, label assumptions, and return your questions with the result instead of answering them yourself.
